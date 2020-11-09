# data-proxy

REST based data proxy server to facilitate data exchange between services in private networks and sporadic inter-service network connectivity.

## Deployment

Code depoyed via Azure web application free tier. REST server accepts data in POST calls and makes it available via authenticated GET calls. See OpenAPI spec by running the server locally.

```bash
debug=1 ./start-proxy.sh
# Navigate to localhost:8000/docs
```

### Azure

- Add custom start command with Settings > Configuration > General settings > Startup Command

  ```bash
  start-proxy.sh
  ```

- Set env variables for the authentication via Settings > Configuration > "+ Application Setting".
- Goto Configuration > General settings > FTP state > Disable.

## Test

```bash
portal_url="pytestapp.azurewebsites.net"

curl -X POST "https://${portal_url}/slack_poxy/event" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"token\":\"errteddt\",\"team_id\":\"T061EG9RZ\",\"api_app_id\":\"A0FFV41KK\",\"event\":{\"type\":\"reaction_added\",\"user\":\"U061F1EUR\",\"item\":{\"type\":\"message\",\"channel\":\"C061EG9SL\",\"ts\":\"1464196127.000002\"},\"reaction\":\"slightly_smiling_face\",\"item_user\":\"U0M4RL1NY\",\"event_ts\":\"1465244570.336841\"},\"type\":\"event_callback\",\"authed_users\":[\"U061F7AUR\"],\"authorizations\":{\"enterprise_id\":\"E12345\",\"team_id\":\"T12345\",\"user_id\":\"U12345\",\"is_bot\":false},\"event_id\":\"Ev9UQ52YNA\",\"event_context\":\"EC12345\",\"event_time\":1234567890}"
```

## Resources

- https://github.com/windson/fastapi/tree/fastapi-postgresql-azure-deploy
- https://github.com/MicrosoftDocs/azure-dev-docs/blob/master/articles/python/tutorial-deploy-app-service-on-linux-04.md
- https://github.com/MicrosoftDocs/azure-dev-docs/issues/142
- Proper pre-push hooks: https://githooks.com/

  ```bash
  echo "./scripts/format_and_lint.sh" > .git/hooks/pre-commit
  echo "./scripts/test.sh" >> .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
  ```

## TODOs

## CI/CD

- Consider options below (focus on credit card free, no free access expiry and longer daily/monthly quotas). Search for "cloud always free tier comparison 2020":
  - https://www.oracle.com/cloud/free/.
    - Oracle gives free DBs.
  - https://cloud.google.com/free/
    - Might have good ML APIs.
    - Multiple free services.
  - https://www.heroku.com/managed-data-services
  - https://www.ibm.com/cloud/free
  - digitalocean.
  - cloudflare.
  - ...
- Move to dockerfile based deployment method.
- Write CLI based (e.g. `awscli`) scripts to speed up configuration. Stick to auto image deployment from dockerhub.
- Adopt test github workflow and lint+test in build script from https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker.
- Disable FTP based file access for repo. Prevents protected information from leaking.

## Code

- Move all data persistance to data_persistance.py and reuse the mapped queue class for slack endpoints.
- Use single class for basic auth depends and init username/password from object's init.
- Add websocket client support instead of the GET endpoints so downstream applicatins don't so `while true`s.
- Per generic data queue authentication and signed token issuance.

## Testing

- Add `production_tests` with `production_secrets.secret` file to test production instances.
