from __future__ import annotations

import logging
from collections.abc import Iterator

from bson import ObjectId

from module_qc_database_tools.typing_compat import LocalDBComponent

log = logging.getLogger(__name__)


def get_component(database, identifier) -> (LocalDBComponent, str):
    """
    Get component information using identifier (serial number or id).

    Args:
        database (:obj:`pymongo.database.Database`): mongoDB database to query for component information
        identifier (:obj:`str`): identifier of component to get information for (serial number or id)

    Returns:
        component (:obj:`dict`): information about the component from localDB
        stage (:obj:`str`): current stage of component
    """
    if ObjectId.is_valid(identifier):
        component = database.component.find_one({"_id": ObjectId(identifier)})
    else:
        component = database.component.find_one({"serialNumber": identifier})

    if not component:
        msg = f"component with {identifier} not in your localDB"
        raise ValueError(msg)

    serial_number = component["serialNumber"]

    component_stage = get_stage(database, component)
    if not component_stage:
        msg = f"component {serial_number} does not have any QC status. Something went wrong in your localDB."
        raise ValueError(msg)

    return (component, component_stage)


def get_serial_number(component: LocalDBComponent) -> str:
    """
    Get the serial number from the component.

    Args:
        component (:obj:`dict`): localDB component to get serial number from

    Returns:
        serial_number (:obj:`str`): serial number of component
    """
    return component["serialNumber"]


def get_stage(database, component: LocalDBComponent) -> str | None:
    """
    Get the stage from the component.

    Args:
        component (:obj:`dict`): localDB component to get stage from

    Returns:
        stage (:obj:`str`): stage of component
    """
    component_id = str(component["_id"])

    component_qcstatus = database.QC.module.status.find_one({"component": component_id})
    return component_qcstatus.get("currentStage")


def get_children(
    database, component: LocalDBComponent, *, component_type
) -> Iterator[LocalDBComponent]:
    """
    Get (unique!) children for component by ID matching the component type from Local DB.

    !!! note

        This returns a generator.

    Args:
        database (:obj:`pymongo.database.Database`): mongoDB database to query for parent-child relationship
        component (:obj:`dict`): the top-level component to recursively get the children of
        component_type (:obj:`str` or :obj:`None`): the component type code to filter children by (None for any)

    Returns:
        children (:obj:`iterator`): generator of localDB components matching the component type
    """

    def _recursive(
        database, component_id: str, *, component_type
    ) -> Iterator[LocalDBComponent]:
        component = database.component.find_one({"_id": ObjectId(component_id)})
        yielded = set()

        if component.get("componentType") == component_type or component_type is None:
            yield component

        for child_id in database.childParentRelation.find(
            {"parent": component_id}
        ).distinct("child"):
            # yield from get_children(database, child_id, component_type=component_type)
            for child in _recursive(database, child_id, component_type=component_type):
                if child["_id"] in yielded:
                    continue
                yield child
                yielded.add(child["_id"])

    component_id = str(component["_id"])
    yield from _recursive(database, component_id, component_type=component_type)


def set_component_stage(database, serial_number: str, stage: str, *, userdb) -> None:
    """
    Set component (by serial number) to the current stage.

    Args:
        database (:obj:`pymongo.database.Database`): mongoDB database to set QC status for stage
        serial_number (:obj:`str`): serial number of component
        stage (:obj:`str`): code of stage to set component to
        userdb (:obj:`pymongo.database.Database`): mongoDB database to query for stage information

    Returns:
        None
    """
    component = database.component.find_one({"serialNumber": serial_number})
    component_id = str(component["_id"])
    ldb_component_type = component["componentType"]

    ctype_map = {
        "bare_module": "BARE_MODULE",
        "front-end_chip": "FE_CHIP",
        "module": "MODULE",
        "module_pcb": "PCB",
        "sensor_tile": "SENSOR_TILE",
    }

    pdb_component_type = ctype_map[ldb_component_type]
    stages = userdb.QC.stages.find_one({"code": pdb_component_type}).get("stage_flow")

    if stage not in stages:
        msg = f"{stage} is not a valid stage on this component type: {pdb_component_type} ({ldb_component_type})"
        raise ValueError(msg)

    userdb.QC.module.status.update_one(
        {"component": component_id}, {"currentStage": stage}
    )
