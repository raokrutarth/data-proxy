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
    echo "Running in production mode."

    # Remove old DB data
    rm -rf ${SLACK_EVENT_DB_PATH} ${GENERIC_EVENT_DB_PATH} || true

    # Production runtime
    #   - Use gunicorn+uvicorn for best performance. It defaults to port 8000. Which is what azure expects.
    #   - Use 2 workers given the free tier ony provisions 1 core.
    #   - Auth env vars come from the Azure runtime.
    # TODO store log file in secure location
    poetry run gunicorn \
        --bind=0.0.0.0 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level info \
        --log-file /tmp/data-proxy.log \
        main:app
else
    echo "Running in development mode."
    # start development server with simpler env variables that the
    # production OS will populate with actual values.
    export WEBSITE_HOSTNAME="localhost:8000"

    export SLACK_PROXY_USERNAME=dev
    export SLACK_PROXY_PASSWORD=dev
    export SLACK_VERIFICATION_TOKEN=tk
    export SLACK_EVENT_DB_PATH="./slack_proxy_queue_db"

    export GENERIC_PROXY_USERNAME=dev
    export GENERIC_PROXY_PASSWORD=dev
    export GENERIC_EVENT_DB_PATH="./generic_proxy_queue_mapping_db"

    # Remove old DB/queue data
    rm -rf ${SLACK_EVENT_DB_PATH} ${GENERIC_EVENT_DB_PATH}

    poetry run gunicorn \
        --bind=0.0.0.0:8000 \
        --workers 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level info \
        main:app
fi