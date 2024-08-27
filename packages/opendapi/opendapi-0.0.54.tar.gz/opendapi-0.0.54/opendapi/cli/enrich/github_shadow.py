"""Enricher to work from Github/Shadow mode as part of `opendapi enrich` CLI command."""

from typing import Callable, List, Optional

from opendapi.adapters.dapi_server import DAPIServerResponse
from opendapi.adapters.file import OpenDAPIFileContents
from opendapi.cli.enrich.github import GithubEnricher


class GithubShadowModeEnricher(GithubEnricher):
    """Shadow mode enricher to work from Github as part of `opendapi enrich` CLI command."""

    add_all_untracked_files = False

    def __init__(self, *args, **kwargs):
        """Init the shadow mode enricher"""
        super().__init__(*args, **kwargs)

        # Let us look for committed files which have changed from the base
        self.changed_file_set = self.current_commit_files.dapi_set.intersection(
            self.changed_files_from_base.dapi_set
        )

        if self.changed_files.dapi_set:
            # If opendapi generate changed files, let us go ahead and adjust things
            self._adjust_file_sets()

    def _adjust_file_sets(self):
        """Update the file sets to only include the files pushed from upstream"""

        dapis = {
            dapi: self.changed_files_from_base.dapis[dapi]
            for dapi in self.changed_file_set
            if dapi in self.changed_files_from_base.dapis
        }

        # Only send this small set of files to the server for enrichment and impact analysis
        self.changed_files = OpenDAPIFileContents(
            teams={}, dapis=dapis.copy(), datastores={}, purposes={}, config=self.config
        )
        self.changed_files_from_base = OpenDAPIFileContents(
            teams={}, dapis=dapis.copy(), datastores={}, purposes={}, config=self.config
        )
        self.current_commit_files = OpenDAPIFileContents(
            teams={}, dapis=dapis.copy(), datastores={}, purposes={}, config=self.config
        )
        # self.base_commit_files can remain as-is, as it is just the state of the repo
        # at the base commit, before any generation, before dapis are fetched, etc.

    def should_enrich(self) -> bool:
        """Should we enrich the DAPI files?"""
        return (
            self.dapi_server_config.suggest_changes
            and self.trigger_event.is_pull_request_event
            and (
                # When in shadow mode, we enrich only if the current commit
                # has dapi files in them
                self.dapi_server_config.is_repo_onboarded
                or bool(self.current_commit_files.dapi_set)
            )
        )

    def should_analyze_impact(self) -> bool:
        return self.trigger_event.is_pull_request_event and (
            self.dapi_server_config.is_repo_onboarded or bool(self.changed_file_set)
        )

    def functions_to_run(self) -> List[Callable[[], Optional[DAPIServerResponse]]]:
        """Check if we should run the action."""
        # if this is not a pull request event, we only do things if there are files to process
        if self.trigger_event.is_push_event:
            if self.dapi_server_config.repo_being_configured:
                return [
                    *self.base_functions_to_run,
                    self.dapi_requests.mark_repo_as_configured,  # Initial config PR is merged
                ]

            return super().functions_to_run()

        # this is a pull request event

        if self.dapi_server_config.repo_being_configured:
            self.print_markdown_and_text(
                "This is the initial configuration PR",
                color="yellow",
            )
            return self.base_functions_to_run

        return super().functions_to_run()
