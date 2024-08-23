"""Module for various Git operations and utilities.

This module provides functions to interact with a Git repository, including
staging, committing, pushing changes, and running pre-commit hooks. It also
includes functions to retrieve the status of the repository and handle deleted
files.

Typical usage example:

    from klingon_tools.git_tools import git_get_toplevel, git_commit_file

    repo = git_get_toplevel() if repo:
        git_commit_file('example.txt', repo)
"""

import os
import subprocess
import sys
from typing import Optional, Tuple
import psutil

from git import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
    Repo,
    exc as git_exc,
)

from klingon_tools.git_push_helper import git_push
from klingon_tools.git_user_info import get_git_user_info
from klingon_tools.git_validate_commit import (
    is_commit_message_signed_off,
    is_conventional_commit,
    validate_commit_messages,
)
from klingon_tools.log_msg import log_message
from klingon_tools.litellm_tools import LiteLLMTools

LOOP_MAX_PRE_COMMIT = 10


def branch_exists(branch_name: str) -> bool:
    """Check if a branch exists in the repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def cleanup_lock_file(repo_path: str) -> None:
    """Cleans up the .lock file in the git repository.

    This function checks for running `push` or `git` processes and removes the
    .lock file if it exists in the git repository and no conflicting processes
    are found.

    Args:
        repo_path: The path to the git repository.

    Returns:
        None
    """
    # Construct the path to the .lock file
    lock_file_path = os.path.join(repo_path, ".git", "index.lock")

    # Check if the .lock file exists
    if os.path.exists(lock_file_path):
        # Check for running `push` or `git` processes
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] in ["push", "git"]:
                log_message.error(
                    message=f"Conflicting process '{proc.info['name']}' with"
                    f"PID {proc.info['pid']} is running. Exiting.",
                    status="❌",
                )
                sys.exit(1)
        # Remove the .lock file if no conflicting processes are found
        os.remove(lock_file_path)
        log_message.info("Cleaned up .lock file.")


def git_get_toplevel() -> Optional[Repo]:
    """Initializes a git repository object and returns the top-level directory.

    This function attempts to initialize a git repository object and retrieve
    the top-level directory of the repository. If the current branch is new, it
    pushes the branch upstream.

    Returns:
        An instance of the git.Repo object if successful, otherwise None.
    """
    try:
        # Initialize the git repository object
        repo = Repo(".", search_parent_directories=True)
        # Retrieve the top-level directory of the repository toplevel_dir =
        # repo.git.rev_parse("--show-toplevel") Check if the current branch is
        # a new branch
        current_branch = repo.active_branch
        tracking_branch = current_branch.tracking_branch()
        if tracking_branch is None:
            log_message.info(
                message=f"New branch detected: {current_branch.name}",
                status="🌱",
            )
            # Push the new branch upstream
            repo.git.push("--set-upstream", "origin", current_branch.name)
            log_message.info(
                message=f"Branch {current_branch.name} pushed upstream",
                status="✅",
            )
        # Return the initialized repository object
        return repo
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        # Log an error message if the repository initialization fails
        log_message.error(
            message="Error initializing git repository", status="❌"
        )
        log_message.exception(message=f"{e}")
        # Log an error message if the repository initialization fails
        log_message.error(
            message="Error initializing git repository", status="❌"
        )
        log_message.exception(message=f"{e}")
        # Return None if the repository initialization fails
        return None


def git_get_status(repo: Repo) -> Tuple[list, list, list, list, list]:
    """Retrieves the current status of the git repository.

    This function collects and returns the status of the git repository,
    including deleted files, untracked files, modified files, staged files, and
    committed but not pushed files.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        A tuple containing lists of deleted files, untracked files, modified
        files, staged files, and committed but not pushed files.
    """
    deleted_files = []
    untracked_files = []
    modified_files = []
    staged_files = []
    committed_not_pushed = []

    # Get the current branch of the repository
    current_branch = repo.active_branch

    # Initialize lists to store the status of files
    deleted_files = [
        # List of deleted files
        item.a_path
        for item in repo.index.diff(None)
        if item.change_type == "D"
    ]
    untracked_files = repo.untracked_files  # List of untracked files
    modified_files = [
        # List of modified files
        item.a_path
        for item in repo.index.diff(None)
        if item.change_type == "M"
    ]
    staged_files = [
        item.a_path for item in repo.index.diff("HEAD")
    ]  # List of staged files
    committed_not_pushed = []  # List of committed but not pushed files

    try:
        # Check for committed but not pushed files
        for item in repo.head.commit.diff(f"origin/{current_branch}"):
            if hasattr(item, "a_blob") and hasattr(item, "b_blob"):
                # Add the file to the committed but not pushed list
                committed_not_pushed.append(item.a_path)
    except ValueError as e:
        # Log an error message if there is an issue processing the diff-tree
        # output
        log_message.error(
            message="Error processing diff-tree output:", status="❌"
        )
        log_message.exception(message=f"{e}")
    except Exception as e:
        # Log an error message for any unexpected errors
        log_message.error(message="Unexpected error:", status="❌")
        log_message.exception(message=f"{e}")

    # Return the collected status information
    return (
        deleted_files,
        untracked_files,
        modified_files,
        staged_files,
        committed_not_pushed,
    )


def git_commit_deletes(repo: Repo, deleted_files: list) -> None:
    """Commits deleted files in the given repository.

    This function identifies deleted files in the repository, stages them for
    commit, generates a commit message, and commits the changes. It ensures
    that the commit message follows the Conventional Commits standard and is
    signed off by the user.

    Args:
        repo: An instance of the git.Repo object representing the repository.

    Returns:
        None
    """
    if deleted_files:
        # Combine deleted files from the global list and the repository index
        all_deleted_files = list(
            set(
                deleted_files
                + [
                    item.a_path
                    for item in repo.index.diff(None)
                    if item.change_type == "D"
                ]
            )
        )
        # Log the number of deleted files
        log_message.info(
            message="Deleted files",
            status=f"{len(all_deleted_files)}",
        )
        log_message.debug(
            message=f"Deleted files: {all_deleted_files}", status="🐞"
        )

        # Stage the deleted files for commit
        for file in all_deleted_files:
            if os.path.exists(file):
                repo.index.remove([file], working_tree=True)
            else:
                log_message.info(
                    message=(
                        f"File {file} is already deleted and will be staged "
                        "for removal."
                    ),
                    status="⚠️",
                )
                try:
                    repo.index.remove([file], working_tree=True)
                except git_exc.GitCommandError as e:
                    log_message.error(
                        message=f"Failed to stage deleted file {file}",
                        status="❌",
                    )
                    log_message.exception(message=f"{e}")
                    continue

            # Generate the commit message with scope
            commit_message = f"chore({file}): Committing deleted file"

            # Ensure the commit message is signed off
            if not is_commit_message_signed_off(commit_message):
                user_name, user_email = get_git_user_info()
                signoff = f"\n\nSigned-off-by: {user_name} <{user_email}>"
                commit_message += signoff

            # Commit the deleted file with the generated commit message
            try:
                repo.git.commit("-S", "-m", commit_message)
            except GitCommandError as e:
                if "gpg failed to sign the data" in str(e):
                    log_message.warning(
                        message=(
                            "GPG signing failed. Retrying commit without GPG "
                            "signing."
                        ),
                        status="⚠️",
                    )
                    try:
                        repo.git.commit("-m", commit_message)
                    except GitCommandError as inner_e:
                        log_message.error(
                            message="Failed to commit deleted file",
                            status="❌",
                        )
                        log_message.exception(message=f"{inner_e}")
                        raise
                else:
                    log_message.error(
                        message="Failed to commit deleted file", status="❌"
                    )
                    log_message.exception(message=f"{e}")
                    raise

            # Log the successful commit
            log_message.info(
                message=f"Committed deleted file: {file}", status="✅"
            )

        # Push the commit to the remote repository
        git_push(repo)


def git_stage_diff(file_name: str, repo: Repo, modified_files: list) -> str:
    """Stages a file, generates a diff, and returns the diff.

    This function stages the specified file in the repository, generates a diff
    for the staged file, and returns the diff as a string. It logs the status
    of the staging and diff generation processes.

    Args:
        file_name: The name of the file to be staged and diffed. repo: An
        instance of the git.Repo object representing the repository.

    Returns:
        A string containing the diff of the staged file.
    """
    log_message.info(message="Staging file", status=f"{file_name}")
    process_pre_commit_config(repo, modified_files)

    def stage_file(repo: Repo, file_name: str):
        """Helper function to stage a file."""
        try:
            log_message.debug(
                message="Staging file in repo", status=f"{repo.working_dir}"
            )
            repo.index.add([file_name])
            log_message.debug(message="File staged successfully.", status="✅")
            staged_files = repo.git.diff(
                "--cached", "--name-only"
            ).splitlines()
            log_message.debug(message="Staged files", status=f"{staged_files}")

            # Check if the file was successfully staged
            if file_name in staged_files:
                log_message.info(message="Staged file", status="✅")
            else:
                log_message.error(
                    f"Failed to stage file: {file_name}", status="❌"
                )
                sys.exit(1)
        except Exception as e:
            log_message.error(f"Error staging file: {file_name}", status="❌")
            log_message.exception(message=f"{e}")
            sys.exit(1)

    # Stage the file in the main repo
    stage_file(repo, file_name)

    # Recursively stage files in submodules
    for submodule in repo.submodules:
        submodule_repo = submodule.module()
        if submodule_repo.is_dirty(untracked_files=True):
            stage_file(submodule_repo, file_name)

    # Generate the diff for the staged file
    try:
        log_message.debug(f"Generating diff for file: {file_name}")
        diff = repo.git.diff("HEAD", file_name)
        if diff:
            log_message.info(message="Diff generated", status="✅")
        else:
            log_message.error(message="Failed to generate diff", status="❌")
    except Exception as e:
        log_message.error(message="Error generating diff", status="❌")
        log_message.exception(message=f"{e}")

    return diff


def git_pre_commit(
    file_name: str, repo: Repo, modified_files: list
) -> Tuple[bool, str]:
    """Runs pre-commit hooks on a file.

    This function runs pre-commit hooks on the specified file. If the hooks
    modify the file, it re-stages the file and re-runs the hooks up to a
    maximum number of attempts. If the hooks pass without modifying the file,
    it returns True. If the hooks fail after the maximum number of attempts, it
    exits the script.

    Args:
        file_name: The name of the file to run pre-commit hooks on. repo: An
        instance of the git.Repo object representing the repository.

    Returns:
        True if the pre-commit hooks pass without modifying the file, otherwise
        exits the script after the maximum number of attempts.
    """
    # Stage the file and generate a diff of the file being processed
    diff = git_stage_diff(file_name, repo, modified_files)

    attempt = 0  # Initialize the attempt counter
    log_message.info(80 * "-", status="", style="none")
    log_message.info("Starting pre-commit hooks for", status=f"{file_name}")

    while attempt < LOOP_MAX_PRE_COMMIT:
        # Log start of attempt number
        log_message.info(
            message="Running pre-commit attempt",
            status=f"{attempt + 1}/{LOOP_MAX_PRE_COMMIT}",
        )
        env = os.environ.copy()  # Copy the current environment variables
        # Set PYTHONUNBUFFERED to ensure real-time output
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.Popen(  # Run the pre-commit hooks
            ["pre-commit", "run", "--files", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        stdout, stderr = (
            [],
            [],
        )  # Initialize lists to capture stdout and stderr

        for line in process.stdout:  # Capture stdout line by line
            # Replace specific strings with emoticons
            modified_line = (
                line.replace("Passed", "....✅")
                .replace("Skipped", ".....⏭️")
                .replace("Failed", "....❌")
            )
            sys.stdout.write(modified_line)
            stdout.append(modified_line)

        for line in process.stderr:  # Capture stderr line by line
            # Replace specific strings with emoticons
            modified_line = (
                line.replace("Passed", "....✅")
                .replace("Skipped", ".....⏭️")
                .replace("Failed", "....❌")
            )
            sys.stderr.write(modified_line)
            stderr.append(modified_line)

        process.wait()  # Wait for the process to complete
        result = (
            subprocess.CompletedProcess(  # Create a CompletedProcess instance
                process.args,
                process.returncode,
                "".join(stdout),
                "".join(stderr),
            )
        )

        log_message.debug(
            message="Pre-commit hooks completed with return code",
            status=f"{result.returncode}",
        )
        if (
            "files were modified by this hook" in result.stdout
            or "Fixing" in result.stdout
        ):
            # Log that the file was modified by the pre-commit hook
            log_message.info(message=80 * "-", status="", style="none")
            log_message.info(
                f"File {file_name} was modified by pre-commit hooks",
                status="🔄",
            )
            log_message.info(
                message=("File modified by pre-commit, restaging"),
                status="🔄",
            )
            log_message.info(message=80 * "-", status="", style="none")

            # Re-stage the file and generate a new diff
            diff = git_stage_diff(file_name, repo, modified_files)

            # Increment the attempt counter
            attempt += 1  # Increment the attempt counter
            if (
                attempt == LOOP_MAX_PRE_COMMIT
            ):  # Check if maximum attempts reached
                log_message.error(
                    message=f"Pre-commit hooks failed for {file_name} after "
                    f"{LOOP_MAX_PRE_COMMIT} attempts. Exiting script.",
                    status="❌",
                )
                sys.exit(1)  # Exit the script if maximum attempts reached
        if result.returncode == 0:  # Check if pre-commit hooks passed
            log_message.info(
                f"Pre-commit hooks passed for {file_name}", status="✅"
            )
            return True, diff  # Return True if hooks passed

        if (
            result.returncode == 1
            and "files were modified by this hook" not in result.stdout
            and "Fixing" not in result.stdout
        ):
            log_message.error(
                message="Pre-commit hooks failed without modifying files. "
                "Exiting push.",
                status="❌",
            )
            log_message.debug(
                message=f"Pre-commit stdout: {result.stdout}", status=""
            )
            log_message.debug(
                message=f"Pre-commit stderr: {result.stderr}", status=""
            )
            log_message.info(80 * "-", status="", style="none")
            sys.exit(1)

    log_message.error(
        f"Pre-commit hooks did not pass for {file_name} after "
        f"{LOOP_MAX_PRE_COMMIT} attempts",
        status="❌",
    )
    return False, diff  # Return False if pre-commit hooks did not pass


def git_commit_file(
    file_name: str, repo: Repo, commit_message: Optional[str] = None
) -> None:
    """Commits a file with a generated commit message.

    This function stages the specified file, generates a commit message using
    the diff of the file, and commits the file to the repository. It logs the
    status of each step and handles exceptions that may occur during the
    process.

    Args:
        file_name: The name of the file to be committed. repo: An instance of
        the git.Repo object representing the repository. commit_message: The
        commit message to use. If None, a new commit message will be generated.

    Returns:
        None
    """
    repo.index.add([file_name])

    try:
        if commit_message is None:
            # Generate the diff for the staged file
            diff = repo.git.diff("HEAD", file_name)
            litellm_tools = LiteLLMTools()
            commit_message = None
            while not commit_message or not is_conventional_commit(
                commit_message
            ):
                commit_message = litellm_tools.generate_commit_message(diff)

        # Commit the file with the generated commit message
        if commit_message:
            repo.index.commit(commit_message.strip())
        else:
            raise ValueError("Commit message cannot be None")
        # Log the successful commit
        log_message.info(message="File committed", status="✅")

        # Example call to validate_commit_messages
        litellm_tools = LiteLLMTools()
        validate_commit_messages(repo, litellm_tools)
    except ValueError as ve:
        # Log an error message if the commit message format is invalid
        log_message.error(message="Commit message format error", status="❌")
        log_message.exception(message=f"{ve}")
    except Exception as e:
        # Log an error message if the commit fails
        log_message.error(message="Failed to commit file", status="❌")
        log_message.exception(message=f"{e}")


def log_git_stats(
    deleted_files: list,
    untracked_files: list,
    modified_files: list,
    staged_files: list,
    committed_not_pushed: list,
) -> None:
    """Logs git statistics.

    This function logs the number of deleted files, untracked files, modified
    files, staged files, and committed but not pushed files in the repository.

    Returns:
        None
    """
    # Log a separator line
    log_message.info(message=80 * "-", status="", style="none")
    # Log the number of deleted files
    log_message.info(message="Deleted files", status=f"{len(deleted_files)}")
    # Log the number of untracked files
    log_message.info(
        message="Untracked files", status=f"{len(untracked_files)}"
    )
    # Log the number of modified files
    log_message.info(message="Modified files", status=f"{len(modified_files)}")
    # Log the number of staged files
    log_message.info(message="Staged files", status=f"{len(staged_files)}")
    # Log the number of committed but not pushed files
    log_message.info(
        message="Committed not pushed files",
        status=f"{len(committed_not_pushed)}",
    )
    log_message.info(message=80 * "-", status="", style="none")


def push_changes_if_needed(repo: Repo, args) -> None:
    """Push changes to the remote repository if there are new commits.

    This function checks if there are new commits to push to the remote
    repository. If there are, it pushes the changes. It also handles dry run
    mode and performs cleanup after the push operation.

    Args:
        repo: An instance of the git.Repo object representing the repository.
        args: Command-line arguments.

    Returns:
        None
    """
    # Update git status variables so we have a count of files to push from
    # committed_not_pushed
    committed_not_pushed = git_get_status(repo)[-1]

    def push_submodules(repo: Repo):
        """Recursively push changes in submodules."""
        for submodule in repo.submodules:
            submodule_repo = submodule.module()
            if submodule_repo.is_dirty(untracked_files=True):
                submodule_repo.git.add(A=True)
                submodule_repo.index.commit("Update submodule")
                push_submodules(submodule_repo)
            submodule_repo.remotes.origin.push()

    try:
        # Check if there are new commits to push
        if (
            repo.is_dirty(index=True, working_tree=False)
            or committed_not_pushed
        ):
            if args.dryrun:
                log_message.info(
                    message="Dry run mode enabled. Skipping push.", status="🚫"
                )
            else:
                # Push the commit
                git_push(repo)
                # Push changes in submodules
                push_submodules(repo)

                # Perform cleanup after push operation
                cleanup_lock_file(args.repo_path)
        elif committed_not_pushed:
            log_message.info(
                message="Committing not pushed files found. Pushing changes.",
                status="🚀",
            )
            git_push(repo)
            # Push changes in submodules
            push_submodules(repo)
        else:
            log_message.info(
                message="No new commits to push. Skipping push.", status="🚫"
            )
    except Exception as e:
        log_message.error(message="Failed to push changes", status="❌")
        log_message.exception(message=f"{e}")


def process_pre_commit_config(repo: Repo, modified_files: list) -> None:
    """Process the .pre-commit-config.yaml file.

    This function stages and commits the .pre-commit-config.yaml file if it is
    modified.

    Args:
        repo (Repo): The git repository object.
    """
    # If .pre-commit-config.yaml is modified, stage and commit it
    if ".pre-commit-config.yaml" in modified_files:
        log_message.info(
            message=".pre-commit-config.yaml modified", status="Staging"
        )
        repo.git.add(".pre-commit-config.yaml")
        log_message.info(
            message=".pre-commit-config.yaml staged", status="Committing"
        )
        litellm_tools = LiteLLMTools()
        diff = repo.git.diff("HEAD", ".pre-commit-config.yaml")
        commit_message = litellm_tools.generate_commit_message(diff)
        repo.index.commit(commit_message)
        log_message.info(
            message=".pre-commit-config.yaml committed", status="✅"
        )

        # Remove .pre-commit-config.yaml from modified_files
        modified_files.remove(".pre-commit-config.yaml")

        # If modified_files is empty, log no more files to process and exit
        if not modified_files:
            log_message.info(
                message="No more files to process. Exiting script.",
                status="🚪",
            )
            sys.exit(0)
