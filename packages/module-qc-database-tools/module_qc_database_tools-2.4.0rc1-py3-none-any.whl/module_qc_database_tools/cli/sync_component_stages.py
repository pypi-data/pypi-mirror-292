from __future__ import annotations

import logging
from typing import Optional

import typer
from rich import print as rich_print

from module_qc_database_tools.cli.globals import CONTEXT_SETTINGS, OPTIONS
from module_qc_database_tools.cli.utils import get_dbs_or_client
from module_qc_database_tools.sync_component_stages import sync_component_stages

app = typer.Typer(context_settings=CONTEXT_SETTINGS)
log = logging.getLogger(__name__)


@app.command()
def main(
    serial_number: str = OPTIONS["serial_number"],
    stage: str = OPTIONS["stage"],
    mongo_uri: str = OPTIONS["mongo_uri"],
    localdb_name: str = OPTIONS["localdb_name"],
    userdb_name: str = OPTIONS["userdb_name"],
    ssl: bool = OPTIONS["ssl"],
    itkdb_access_code1: Optional[str] = OPTIONS["itkdb_access_code1"],  # noqa: UP007
    itkdb_access_code2: Optional[str] = OPTIONS["itkdb_access_code2"],  # noqa: UP007
    localdb: bool = OPTIONS["localdb"],
    mongo_serverSelectionTimeout: int = OPTIONS["mongo_serverSelectionTimeout"],
):
    """
    Main executable for syncing component stages recursively.

    !!! note "Added in version 2.4.0"

    """
    # pylint: disable=duplicate-code
    client, userdb = get_dbs_or_client(
        localdb=localdb,
        ssl=ssl,
        mongo_serverSelectionTimeout=mongo_serverSelectionTimeout,
        mongo_uri=mongo_uri,
        localdb_name=localdb_name,
        userdb_name=userdb_name,
        itkdb_access_code1=itkdb_access_code1,
        itkdb_access_code2=itkdb_access_code2,
    )

    try:
        changed_components = sync_component_stages(
            client, serial_number, stage, userdb=userdb
        )
    except Exception as exc:
        rich_print(f":warning: [red bold]Error[/]: {exc}")
        raise typer.Exit(2) from exc

    for current_serial_number, (current_stage, changed) in changed_components.items():
        msg = f"[blue]{current_serial_number}[/]: [yellow]{current_stage}[/]"
        if changed:
            msg += f"-> [yellow]{stage}[/] :new:"
        log.info(msg)


if __name__ == "__main__":
    typer.run(main)
