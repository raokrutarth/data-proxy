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

    # Production runtime
    #   - Use gunicorn+uvicorn for best performance. It defaults to port 8000. Which is what azure expects.
    #   - Use limited workers given the free tier ony provisions 1 core.
    #   - Auth env vars come from the Azure runtime.
else
    echo "Running in development mode."
    # start development server with simpler env variables that the
    # production OS will populate with actual values.
    export WEBSITE_HOSTNAME="localhost:8000"

    export SLACK_PROXY_USERNAME=dev
    export SLACK_PROXY_PASSWORD=dev
    export SLACK_VERIFICATION_TOKEN=tk
    export SLACK_EVENT_DB_PATH="/tmp/slack_proxy_queue_db"

    export GENERIC_PROXY_USERNAME=dev
    export GENERIC_PROXY_PASSWORD=dev
    export GENERIC_EVENT_DB_PATH="/tmp/generic_proxy_queue_mapping_db"

fi

# Remove old DB data
rm -rf ${SLACK_EVENT_DB_PATH} ${GENERIC_EVENT_DB_PATH} || true

 # poetry run gunicorn \
#     --bind=0.0.0.0:8000 \
#     --workers 2 \
#     --worker-class uvicorn.workers.UvicornWorker \
#     --log-level info \
#     --log-file /tmp/data-proxy.log \
#     main:app

# Using uvicorn given gunicorn uses multiple proceses and that breaks the
# internal persistant-queue library.
poetry run uvicorn \
    --workers 4 \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    --reload \
    main:app