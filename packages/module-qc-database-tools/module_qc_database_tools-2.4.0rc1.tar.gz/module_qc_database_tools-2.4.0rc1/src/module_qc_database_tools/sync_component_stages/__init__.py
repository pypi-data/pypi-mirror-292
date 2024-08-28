from __future__ import annotations

import logging

import itkdb

from module_qc_database_tools import db

log = logging.getLogger(__name__)


def sync_component_stages(db_or_client, serial_number: str, stage: str, *, userdb=None):
    """
    Sync the component and its children (recursively) to the provided stage.

    Args:
        serial_number (:obj:`str`): the serial number of the component.
        stage (:obj:`str`): stage code to sync to.

    Returns:
        changed_components (:obj:`dict`): dictionary of serial numbers and whether it was updated or not
    """

    use_localdb = not isinstance(db_or_client, itkdb.Client)

    get_component = db.local.get_component if use_localdb else db.prod.get_component
    get_children = db.local.get_children if use_localdb else db.prod.get_children
    get_serial_number = (
        db.local.get_serial_number if use_localdb else db.prod.get_serial_number
    )
    get_stage = db.local.get_stage if use_localdb else db.prod.get_stage
    set_component_stage = (
        db.local.set_component_stage if use_localdb else db.prod.set_component_stage
    )

    status = {}
    component, status[serial_number] = get_component(db_or_client, serial_number)

    for child in get_children(db_or_client, component, component_type=None):
        child_serial_number = get_serial_number(child)
        child_stage = get_stage(db_or_client, child)
        status[child_serial_number] = child_stage

    changed_components = {}
    for current_serial_number, current_stage in status.items():
        changed = current_stage != stage
        changed_components[current_serial_number] = (current_stage, changed)

        if changed:
            set_component_stage(
                db_or_client, current_serial_number, stage, userdb=userdb
            )

    return changed_components
