# data-proxy

REST based data proxy server to facilitate data exchange between services in private networks and sporadic inter-service network connectivity.

## Deployment

Code depoyed via Azure web application free tier. REST server accepts data in POST calls and makes it available via authenticated GET calls. See OpenAPI spec by running the server locally.

```bash
debug=1 ./start-proxy.sh
# Navigate to localhost:8000/docs
```

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

- Adopt test github workflow and lint+test in build script from https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker.
- Disable FTP based file access for repo. Prevents protected information from leaking.
