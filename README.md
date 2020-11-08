# data-proxy

REST based data proxy server to facilitate data exchange between services in private networks.

## Deployment

Code depoyed via Azure web application. REST server runs in to accept POST calls and make it available via authenticated GET calls.

## Test

```bash
portal_url="pytestapp.azurewebsites.net"

while true; do curl -X POST "https://${portal_url}/slack_poxy/event" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"token\":\"z26uFbvR1xHJEdHE1OQiO6t8\",\"team_id\":\"T061EG9RZ\",\"api_app_id\":\"A0FFV41KK\",\"event\":{\"type\":\"reaction_added\",\"user\":\"U061F1EUR\",\"item\":{\"type\":\"message\",\"channel\":\"C061EG9SL\",\"ts\":\"1464196127.000002\"},\"reaction\":\"slightly_smiling_face\",\"item_user\":\"U0M4RL1NY\",\"event_ts\":\"1465244570.336841\"},\"type\":\"event_callback\",\"authed_users\":[\"U061F7AUR\"],\"authorizations\":{\"enterprise_id\":\"E12345\",\"team_id\":\"T12345\",\"user_id\":\"U12345\",\"is_bot\":false},\"event_id\":\"Ev9UQ52YNA\",\"event_context\":\"EC12345\",\"event_time\":1234567890}" > /dev/null 2>&1; done
```

## Resources

- https://github.com/windson/fastapi/tree/fastapi-postgresql-azure-deploy
- https://github.com/MicrosoftDocs/azure-dev-docs/blob/master/articles/python/tutorial-deploy-app-service-on-linux-04.md
- https://github.com/MicrosoftDocs/azure-dev-docs/issues/142
- Proper pre-push hooks: https://githooks.com/

  ```bash
  echo "./scripts/format_and_lint.sh" > .git/hooks/pre-push
  echo "./scripts/test.sh" >> .git/hooks/pre-push
  chmod +x .git/hooks/pre-push
  ```

## TODOs

- Adopt test github workflow and lint+test in build script from https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker.
- Disable FTP based file access for repo. Prevents protected information from leaking.