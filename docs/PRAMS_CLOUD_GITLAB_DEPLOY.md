# PRAMS Cloud + GitLab Deployment Guide

PRAMS (Participant Recruitment and Management System) uses **GitLab** as the institutional source of truth for production deploys. Cloud demo hosts (Render, Railway) are optional staging environments.

## Repository strategy

| Remote | URL | Purpose |
|--------|-----|---------|
| **GitHub** | `chriscastille6/prams-system` | Public/shell code, no institutional data |
| **GitLab** | `gitlab.nicholls.edu/chriscastille/prams` | IT review, CI/CD, production deploys |

## Approval workflow

```mermaid
flowchart LR
  Dev[Local changes] --> Push[push-to-gitlab.sh]
  Push --> MR[GitLab Merge Request]
  MR --> CI[CI validate + test]
  CI --> Approve[You approve MR]
  Approve --> Main[Merge to main]
  Main --> Manual[Manual deploy:production]
  Manual --> Prod[bayoupal.nicholls.edu/hsirb]
```

1. **Develop locally** on a feature branch.
2. **Push to GitLab** when ready for review:
   ```bash
   chmod +x scripts/push-to-gitlab.sh
   ./scripts/push-to-gitlab.sh
   ```
3. **Open a merge request** on GitLab. CI runs `validate:django` and `test:django` automatically.
4. **Approve and merge** the MR to `main`.
5. **Deploy to production** — in GitLab → CI/CD → Pipelines, click **Play** on `deploy:production`. This is the manual approval gate before code reaches bayoupal.

### GitLab protected environment (recommended)

In GitLab: **Settings → CI/CD → Protected environments → production**

- Enable **Required approvals** (e.g. 1 approver: you).
- Restrict deploy permissions to Maintainers.

This ensures no one can deploy without your explicit approval.

## One-time GitLab CI setup

Add these **CI/CD variables** (Settings → CI/CD → Variables):

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `DEPLOY_SSH_PRIVATE_KEY` | bayoupal deploy key (private) | Yes | Yes |
| `DEPLOY_HOST` | `bayoupal.nicholls.edu` | Yes | No |
| `DEPLOY_USER` | `ccastille` | Yes | No |
| `DEPLOY_PATH` | `~/hsirb-system` | Yes | No |

Generate a deploy key on bayoupal and add the public key to GitLab (Settings → Repository → Deploy keys) and to `~/.ssh/authorized_keys` on the server.

## Cloud demo (Render)

PRAMS cloud configs use **PRAMS** naming (not SONA):

- Blueprint: `render.yaml` → service `prams-system`, database `prams-database`
- Env template: `env.cloud.template`

### Deploy to Render

1. Connect Render to your GitLab or GitHub repo.
2. Use **Blueprint** deploy with `render.yaml`, or create manually:
   - Web service: `prams-system`
   - PostgreSQL: `prams-database`
3. Set env vars from `env.cloud.template` (`RENDER=true`, `SITE_NAME`, etc.).

### Deploy to Railway

1. Connect Railway to the repo.
2. Railway sets `DATABASE_URL` and `RAILWAY_ENVIRONMENT` automatically.
3. Start command: `bash start.sh` (see `railway.json`).

## Campus production (bayoupal)

Production URL: **https://bayoupal.nicholls.edu/hsirb/**

- App path: `~/hsirb-system`
- Service: `hsirb-system` (systemd + Gunicorn)
- Database: `hsirb_db`

Manual deploy from your laptop (without GitLab CI):

```bash
./deploy-to-server.sh
```

## Naming reference

| Context | Name |
|---------|------|
| Product | **PRAMS** |
| Campus service | **hsirb-system** (historical path `/hsirb/`) |
| Cloud demo | **prams-system** |
| Legacy (do not use for new configs) | SONA |

## Next: MCP data layer

See [MCP_DATA_LAYER.md](./MCP_DATA_LAYER.md) for Google MCP Toolbox for Databases + MindsDB integration planned for PRAMS agents.
