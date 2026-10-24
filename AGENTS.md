# Agent guide

Sageware Books: the Calibre-Web theme and deployment for <https://books.sageware.io>. See README.md for the layout.

## Skills

Task playbooks live in `.agents/skills/<name>/SKILL.md` (Agent Skills format: YAML front matter, then
Markdown steps). Read the matching one before starting that kind of task. `.claude/skills/` links to the
same files for Claude Code.

| Skill | Use it for |
| --- | --- |
| [deploy](.agents/skills/deploy/SKILL.md) | Deploying to production through Dokploy, and fixing an unstyled site after a deploy |

## Rules

- Production changes (pushing to `main`, deploying, restarting the Dokploy service) need the user's go-ahead.
- Never deploy with "Fresh Volumes" or rename the data volumes; never commit secrets or print `$DOKPLOY_API_KEY`.
- Theme work: run `docker compose -f docker-compose.dev.yml up -d` (http://localhost:8083) and restart the
  container after editing a template, since Flask caches them. After adding or removing a template override, run
  `python3 tools/gen_compose.py`. Bump `version` in `overrides/templates/sageware_macros.html` when CSS or icons change.
- Keep the element ids that Calibre-Web's JavaScript binds to; each override notes them at the top.
