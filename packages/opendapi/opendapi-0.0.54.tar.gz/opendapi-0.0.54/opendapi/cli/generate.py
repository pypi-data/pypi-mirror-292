"""Entrypoint for the OpenDAPI CLI `opendapi generate` command."""

import click

from opendapi.cli.common import (
    get_opendapi_config_from_root,
    pretty_print_errors,
    print_cli_output,
)
from opendapi.cli.options import dev_options
from opendapi.logging import LogDistKey, Timer
from opendapi.validators.base import MultiValidationError
from opendapi.validators.dapi import DAPI_INTEGRATIONS_VALIDATORS
from opendapi.validators.datastores import DatastoresValidator
from opendapi.validators.teams import TeamsValidator


@click.command()
@dev_options
def cli(**kwargs):
    """
    Generate DAPI files for integrations specified in the OpenDAPI configuration file.

    For certain integrations such as DBT and PynamoDB, this command will also run
    additional commands in the respective integration directories to generate DAPI files.
    """
    print_cli_output(
        "Generating DAPI files for your integrations per `opendapi.config.yaml` configuration",
        color="green",
    )
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    validators = [
        TeamsValidator,
        DatastoresValidator,
    ]

    print_cli_output(
        "Identifying your integrations...",
        color="yellow",
    )
    for intg, validator in DAPI_INTEGRATIONS_VALIDATORS.items():
        if opendapi_config.has_integration(intg):
            if validator:
                validators.append(validator)
            print_cli_output(f"  Found {intg}...", color="green")

    print_cli_output(
        "Generating DAPI files for your integrations...",
        color="yellow",
    )
    errors = []
    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.CLI_GENERATE, tags=metrics_tags):
        for validator in validators:
            inst_validator = validator(
                root_dir=opendapi_config.root_dir,
                enforce_existence=True,
                should_autoupdate=True,
            )

            try:
                inst_validator.run()
            except MultiValidationError as exc:
                errors.append(exc)

    if errors:
        pretty_print_errors(errors)
        raise click.ClickException("Encountered one or more validation errors")

    print_cli_output(
        "Successfully generated DAPI files for your integrations",
        color="green",
    )
