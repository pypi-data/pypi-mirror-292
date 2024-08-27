"""CLI for registering DAPI files: `opendapi register`."""

import click

from opendapi.adapters.dapi_server import DAPIRequests
from opendapi.adapters.file import OpenDAPIFileContents
from opendapi.cli.common import get_opendapi_config_from_root, print_cli_output
from opendapi.cli.options import (
    construct_change_trigger_event,
    construct_dapi_server_config,
    dapi_server_options,
    dev_options,
    github_options,
    opendapi_run_options,
)
from opendapi.logging import LogDistKey, Timer


@click.command()
@dev_options
@opendapi_run_options
@dapi_server_options
@github_options
def cli(**kwargs):
    """
    This command will find all the DAPI files in the repository to
        1. register them with the DAPI server

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """
    opendapi_config = get_opendapi_config_from_root(kwargs.get("local_spec_path"))
    dapi_server_config = construct_dapi_server_config(kwargs)
    change_trigger_event = construct_change_trigger_event(kwargs)
    dapi_requests = DAPIRequests(
        dapi_server_config=dapi_server_config,
        opendapi_config=opendapi_config,
        trigger_event=change_trigger_event,
        error_msg_handler=lambda msg: print_cli_output(
            msg,
            color="red",
            bold=True,
            markdown_file=change_trigger_event.markdown_file,
        ),
        error_exception_cls=click.ClickException,
        txt_msg_handler=lambda msg: print_cli_output(
            msg,
            color="yellow",
            bold=True,
            no_markdown=True,
        ),
        markdown_msg_handler=lambda msg: print_cli_output(
            msg,
            color="yellow",
            bold=True,
            markdown_file=change_trigger_event.markdown_file,
            no_text=True,
        ),
    )

    should_register = (
        dapi_server_config.register_on_merge_to_mainline
        and (
            change_trigger_event.where == "local"
            or (
                change_trigger_event.where == "github"
                and change_trigger_event.is_push_event
                and change_trigger_event.git_ref
                == f"refs/heads/{dapi_server_config.mainline_branch_name}"
            )
        )
        and (dapi_server_config.woven_integration_mode != "disabled")
    )

    metrics_tags = {
        "org_name": opendapi_config.org_name_snakecase,
        "where": change_trigger_event.where,
        "event_type": change_trigger_event.event_type,
        "should_register": should_register,
    }

    if not should_register:
        print_cli_output(
            "Skipping opendapi register command",
            color="yellow",
            bold=True,
        )
        return

    with Timer(dist_key=LogDistKey.CLI_REGISTER, tags=metrics_tags):
        all_files = OpenDAPIFileContents.build_from_all_files(opendapi_config)

        current_commit_files = OpenDAPIFileContents.build_from_all_files_at_commit(
            opendapi_config, change_trigger_event.after_change_sha
        )

        print_cli_output(
            "Registering DAPI files with the DAPI server...",
            color="green",
            bold=True,
            markdown_file=change_trigger_event.markdown_file,
        )

        with click.progressbar(length=len(all_files.dapis)) as progressbar:
            dapi_requests.register(
                all_files=all_files,
                onboarded_files=current_commit_files,
                commit_hash=change_trigger_event.after_change_sha,
                source=opendapi_config.urn,
                notify_function=lambda progress: progressbar.update(progress)
                or print_cli_output(
                    f"Finished {round(progressbar.pct * 100)}% "
                    f"with {progressbar.format_eta()} remaining",
                    color="green",
                    markdown_file=change_trigger_event.markdown_file,
                ),
            )

            # unregister missing dapis
            dapi_requests.unregister(
                source=opendapi_config.urn,
                except_dapi_urns=[dapi["urn"] for dapi in all_files.dapis.values()],
            )

        print_cli_output(
            "Successfully registered DAPI files with the DAPI server",
            color="green",
            bold=True,
            markdown_file=change_trigger_event.markdown_file,
        )
