---
name: deploy
description: Deploy books.sageware.io (this repo) through Dokploy and verify it. Use when asked to deploy, ship, release or push the theme/compose to production, or when the live site looks unstyled after a deploy.
---

# Deploying books.sageware.io

Production is the Dokploy compose service **books** on <https://dokploy.sageware.io>
(composeId `v4K7MqZJdDXACQYtsd37D`). It runs `./docker-compose.yml` from `main` of
github.com/sagewarehq/sageware-books, with the theme bind-mounted from `overrides/`.

Every step below touches production: get the user's go-ahead before pushing, deploying or restarting.

## Before you deploy

- Bump `version` in `overrides/templates/sageware_macros.html` if CSS or icons changed (browsers cache them).
- Added or removed a template override? Run `python3 tools/gen_compose.py` so both compose files mount it.
- Check the change on the dev stack (`docker compose -f docker-compose.dev.yml up -d`, restart after template edits).
- Commit, then `git push origin main`.

## Deploy

Pushing does **not** deploy. Trigger it with the API (the key is in `$DOKPLOY_API_KEY`; never print or commit it):

```bash
curl -s -X POST https://dokploy.sageware.io/api/compose.deploy \
  -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
  -d '{"composeId":"v4K7MqZJdDXACQYtsd37D"}'
```

Wait until the newest deployment is `done`:

```bash
curl -s "https://dokploy.sageware.io/api/compose.one?composeId=v4K7MqZJdDXACQYtsd37D" -H "x-api-key: $DOKPLOY_API_KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); x=max(d['deployments'], key=lambda x: x['createdAt']); print(x['status'], x['createdAt'], x['title'].splitlines()[0])"
```

## Restart after every deploy (required)

A deploy re-clones the repo but leaves the containers running when `docker-compose.yml` is unchanged.
Their bind mounts then point at the deleted checkout: `/static/sageware/*` returns 404 and the site is
unstyled, while pages still render from Flask's template cache. Stop and start the stack so the mounts
re-bind to the new checkout (same path; data volumes are untouched):

```bash
for a in stop start; do
  curl -s -X POST https://dokploy.sageware.io/api/compose.$a \
    -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
    -d '{"composeId":"v4K7MqZJdDXACQYtsd37D"}'; echo
done
```

## Verify

```bash
curl -s -o /dev/null -w "css %{http_code}\n" https://books.sageware.io/static/sageware/sageware.css   # 200
curl -s https://books.sageware.io/login | grep -o 'sageware.css?v=[0-9]*'                             # the new version
curl -s -o /dev/null -w "opds %{http_code}\n" https://books.sageware.io/opds                          # 401 (auth required)
```

The site takes ~15s to come back after the start. Signed-in pages need a login, so ask the user to check
those (and the book count on /stats).

## Never

- Deploy with **Fresh Volumes**, or rename the volumes `sageware_books_config` / `sageware_books_library`:
  that starts an empty library.
- Mount anything at `/init` in the calibre-web container (s6-overlay's entrypoint; it takes the site down).
- Put secrets in the repo. ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD_HASH and LIBRARY_SEED live in
  Dokploy's Environment tab, single-quoted because the hash contains `$`.
