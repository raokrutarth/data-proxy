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
# See https://api.slack.com/authentication/verifying-requests-from-slack#verifying-requests-from-slack-using-signing-secrets__a-recipe-for-security__step-by-step-walk-through-for-validating-a-request
_SLACK_VERIFICATION_TOKEN = environ.get("SLACK_VERIFICATION_TOKEN")

# Use a file system persisted FIFO queue that uses sqllite internally.
# TODO check approx memory usage per event and restrict size
_EVENT_QUEUE: persistqueue.SQLiteQueue = persistqueue.SQLiteQueue(
    path=environ.get("SLACK_EVENT_DB_PATH"),
    auto_commit=True,
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
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/event")
async def send_event(
    body: Any = Body(...),
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
            detail="Missing verification token to accept new event.",
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

    logging.info(f"Adding payload {body} to slack event queue.")
    _EVENT_QUEUE.put(body)

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
def get_latest_event(
    username: str = Depends(get_verified_username),
):
    """
    ...
    """
    if _EVENT_QUEUE.size == 0:
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content="No available events present.",
        )

    log.info(f"Sending latest slack event to user {username}")

    return dict(
        event=_EVENT_QUEUE.get(),
        events_left_in_queue=_EVENT_QUEUE.size,
    )
