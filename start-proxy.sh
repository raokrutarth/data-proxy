#!/bin/bash -ex


# Ideally this should be in the build stage but given the env has access to the
# internet, install the dependencies (version locked via poetry.lock) at runtime.
export PATH=${PATH}:"${HOME}/.poetry/bin"
if ! which poetry; then
    # Install poetry if it's not installed
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
fi

poetry config virtualenvs.in-project true
poetry install

export PYTHONPATH=${PYTHONPATH}:"$(pwd)/app"

if [[ -z "${debug}" ]]; then
    # Production runtime
    #   - Use gunicorn+uvicorn for best performance. It defaults to port 8000. Which is what azure expects.
    #   - Use 2 workers given the free tier ony provisions 1 core.
    #   - Auth env vars come from the Azure runtime.
    poetry run gunicorn \
        --bind=0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level info \
        --log-file data-proxy.log \
        main:app
else
    # start development server with simpler env variables that the
    # production OS will populate with actual values.
    export SLACK_PROXY_USERNAME=dev
    export SLACK_PROXY_PASSWORD=dev
    export SLACK_VERIFICATION_TOKEN=u8i
    export SLACK_EVENT_DB_PATH="./slack_proxy_queue_db"

    export GENERIC_PROXY_USERNAME=dev
    export GENERIC_PROXY_PASSWORD=dev
    export GENERIC_EVENT_DB_PATH="./generic_proxy_queue_db"

    # remove old DB data
    rm -rf ${SLACK_EVENT_DB_PATH} ${GENERIC_EVENT_DB_PATH}

    poetry run uvicorn \
        --reload \
        --host 0.0.0.0 \
        --port ${1:-8000} \
        --log-level info \
        --workers 4 \
        main:app
fi