# Sageware Books

The theme and deployment for [books.sageware.io](https://books.sageware.io), a Calibre-Web library.

The stock `lscr.io/linuxserver/calibre-web:0.6.27-ls406` image runs unchanged; the Sageware theme is
a set of template overrides and static files bind-mounted on top of it.

- `overrides/templates/` replaces (or adds) Calibre-Web templates. Element ids that Calibre-Web's
  JavaScript binds to are kept; see the comment at the top of each file.
- `overrides/static/sageware/` holds the stylesheet, the Inter font and a Lucide icon sprite
  (`tools/build_icons.py`, same Lucide version as Talaria).
- `docker-compose.yml` is the production compose Dokploy deploys from this repo.
- `docker-compose.dev.yml` runs the same image locally on <http://localhost:8083>.
- `bootstrap/init_books.py` seeds an empty library and admin on a first-ever start.

## Working on the theme

```bash
docker compose -f docker-compose.dev.yml up -d
python3 dev/seed.py   # upload any EPUBs you put in dev/epubs (git-ignored)
```

Flask caches templates: restart the container after editing one. After adding or removing a template
override, run `python3 tools/gen_compose.py` so both compose files mount it.

Bump `version` in `overrides/templates/sageware_macros.html` when shipping CSS or icon changes, so
browsers drop their cached copies.

## Deploying

Push to `main`, then trigger a deploy of the `books` compose service in Dokploy (pushing alone doesn't
deploy). After every deploy, stop and start the service: the deploy re-clones the repo but keeps the
running container, whose theme bind mounts then point at the deleted checkout and the site loses its
styling. The full steps and checks are in [.agents/skills/deploy/SKILL.md](.agents/skills/deploy/SKILL.md).
Secrets live in Dokploy's Environment tab, never in the repo. The data volumes are `sageware_books_config` and
`sageware_books_library`: never deploy with "Fresh Volumes".
