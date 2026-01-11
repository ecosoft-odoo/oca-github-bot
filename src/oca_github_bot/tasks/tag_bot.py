# Copyright (c) ACSONE SA/NV 2019
# Distributed under the MIT License (http://opensource.org/licenses/MIT).

from .. import github
from ..config import switchable
from ..queue import getLogger, task

_logger = getLogger(__name__)


@task()
@switchable()
def tag_bot_add_label(org, repo, pr, username, label_name, dry_run=False):
    """Add a label to a pull request. Create the label if it doesn't exist."""
    with github.repository(org, repo) as gh_repo:
        gh_pr = github.gh_call(gh_repo.pull_request, pr)
        gh_issue = github.gh_call(gh_pr.issue)

        # Check if user has push permissions
        if not github.github_user_can_push(gh_repo, username):
            github.gh_call(
                gh_pr.create_comment,
                f"Sorry @{username}, you don't have permission to add labels.",
            )
            _logger.info(
                f"User {username} does not have push permissions on {org}/{repo}"
            )
            return

        # Check if label exists, create if not
        existing_labels = {label.name for label in gh_repo.labels()}
        if label_name not in existing_labels:
            if dry_run:
                _logger.info(f"DRY-RUN create label {label_name} in {org}/{repo}")
            else:
                _logger.info(f"Creating label {label_name} in {org}/{repo}")
                github.gh_call(gh_repo.create_label, label_name, "ededed")

        # Add label to issue
        if dry_run:
            _logger.info(f"DRY-RUN add label {label_name} to PR {gh_pr.url}")
        else:
            _logger.info(f"Adding label {label_name} to PR {gh_pr.url}")
            github.gh_call(gh_issue.add_labels, label_name)
