import logging
import secrets
from os import environ
from os.path import join
from typing import Any, Tuple
from uuid import uuid1

import persistqueue
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    status,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import create_model

log = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBasic()

_USERNAME = environ.get("GENERIC_PROXY_USERNAME")
_PASSWORD = environ.get("GENERIC_PROXY_PASSWORD")


def _get_queue_mapper_db_sesh() -> persistqueue.PDict:

    db_path = environ.get("GENERIC_EVENT_DB_PATH")
    assert db_path is not None, f"Invalid queue db path: {db_path}"
    # dict containing queue ID to persist-queue path
    return persistqueue.PDict(
        path=db_path,
        name="generic_proxy_queues_mapppings",
        multithreading=True,
    )


def get_verified_username(credentials: HTTPBasicCredentials = Depends(security)):
    if _USERNAME is None or _PASSWORD is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to authenticate.",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(credentials.username, _USERNAME)
    correct_password = secrets.compare_digest(credentials.password, _PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _get_queue_details(
    queue_mappings: persistqueue.PDict, queue_id: str
) -> Tuple[str, str]:
    if queue_id in queue_mappings:
        queue_name, queue_path = queue_mappings[queue_id]
        return queue_name, queue_path
    return "", ""


def _get_queue_sesssion(queue_name: str, queue_path: str) -> persistqueue.SQLiteQueue:
    """
    Given a queue name and DB path, return the queue object.
    """
    return persistqueue.SQLiteQueue(
        path=queue_path,
        name=queue_name,
        auto_commit=True,
        multithreading=True,
        timeout=30,  # wait upto 30 sec to acquire a DB lock.
    )


def _add_to_queue(queue_mappings: persistqueue.PDict, queue_id: str, payload: dict):
    """
    Add the payload to the given queue. Create the queue if it doesn't exist.
    """

    q_name, q_path = _get_queue_details(queue_mappings, queue_id)

    if not q_name:
        # queue doesn't exist
        log.info(
            f"Creating new queue. Data map held in directory: {queue_mappings.path}"
        )
        q_name = f"generic_proxy_queue_{str(uuid1())}"
        q_path = join(queue_mappings.path, q_name)
        queue_mappings[queue_id] = (q_name, q_path)
        log.info(
            f"Creating new data queue with name {q_name} with DB in {q_path} for queue ID {queue_id}"
        )
    else:
        log.info(f"Found queue with ID {queue_id}")

    queue = _get_queue_sesssion(q_name, q_path)
    queue.put(payload)
    log.info(f"Added payload {payload} to queue with queue ID {queue_id}")


@router.post(
    "/{queue_id}/data",
    response_model=create_model(
        "DataIngestionResponse",
        status=(
            str,
            ...,
        ),
    ),
)
async def send_data(
    background_tasks: BackgroundTasks,
    body: Any = Body(...),
    queue_id: str = Path(
        ..., title="Queue ID", description="ID to uniquely identify a data queue."
    ),
    username: str = Depends(get_verified_username),
    queue_mappings: persistqueue.PDict = Depends(_get_queue_mapper_db_sesh),
):
    """
    Data ingestion.
    """
    logging.info(
        f"User {username} requested to add payload {body} to generic event queue {queue_id}."
    )
    background_tasks.add_task(_add_to_queue, queue_mappings, queue_id, body)

    return dict(status=f"Event scheduled to be saved in queue {queue_id}.")


@router.get(
    "/{queue_id}/data",
    response_model=create_model(
        "DataProxyGetResponse",
        data=(dict, ...),
        items_left_in_queue=(int, ...),
    ),
)
def get_latest_event(
    username: str = Depends(get_verified_username),
    queue_id: str = Path(
        ..., title="Queue ID", description="ID to uniquely identify a data queue."
    ),
    queue_mappings: persistqueue.PDict = Depends(_get_queue_mapper_db_sesh),
):
    """
    Data access.
    """
    q_name, q_path = _get_queue_details(queue_mappings, queue_id)
    if not q_name:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"Queue with ID {queue_id} not present.",
        )

    queue = _get_queue_sesssion(q_name, q_path)
    if queue.size == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"Queue with ID {queue_id} is empty.",
        )

    log.info(f"Sending least recent payload from queue {queue_id} to user {username}")

    return dict(
        data=queue.get(),
        items_left_in_queue=queue.size,
    )
