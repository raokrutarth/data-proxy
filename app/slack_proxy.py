import logging
import secrets
from os import environ
from typing import Any

import persistqueue
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import create_model
from starlette.responses import JSONResponse

log = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBasic()

_USERNAME = environ.get("SLACK_PROXY_USERNAME")
_PASSWORD = environ.get("SLACK_PROXY_PASSWORD")

# Slack verification token to make sure only Slack can publish to the POST endpoint.
# See https://api.slack.com/authentication/verifying-requests-from-slack
_SLACK_VERIFICATION_TOKEN = environ.get("SLACK_VERIFICATION_TOKEN")


def _get_queue_session() -> persistqueue.SQLiteQueue:
    # Use a file system persisted FIFO queue that uses sqllite internally.
    # TODO check approx memory usage per event and restrict size
    db_path = environ.get("SLACK_EVENT_DB_PATH")
    assert db_path is not None, f"Invalid queue db path: {db_path}"

    return persistqueue.SQLiteQueue(
        path=db_path,
        auto_commit=True,
        multithreading=True,
        timeout=30,  # wait upto 30 sec to acquire a DB lock.
    )


def get_verified_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
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
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/event")
async def send_event(
    body: Any = Body(...),
    event_queue: persistqueue.SQLiteQueue = Depends(_get_queue_session),
):
    """
    Endpoint for slack events API verification and event ingestion.
    """
    if "token" not in body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request body missing required fields.",
        )
    if _SLACK_VERIFICATION_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing verification token. Unable to accept new event.",
        )
    if not secrets.compare_digest(body["token"], _SLACK_VERIFICATION_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    if "challenge" in body:
        # slack event endpoint verification step.
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=dict(
                challenge=body["challenge"],
            ),
        )

    log.info("Adding payload to slack event queue.")
    log.debug("payload value: %s", body)
    event_queue.put(body)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=dict(status="Event saved.")
    )


@router.get(
    "/event",
    response_model=create_model(
        "SlackEventWrapper",
        event=(dict, ...),
        events_left_in_queue=(int, ...),
    ),
)
def get_fifo_event(
    username: str = Depends(get_verified_username),
    event_queue: persistqueue.SQLiteQueue = Depends(_get_queue_session),
):
    """
    ...
    """
    if event_queue.size == 0:
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content="No available events present.",
        )

    log.info(f"Sending least recent slack event to user {username}")

    return dict(
        event=event_queue.get(),
        events_left_in_queue=event_queue.size,
    )
