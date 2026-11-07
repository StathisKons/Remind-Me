# Potpal deployment (Discord Contest Reminder)

This branch is independent from the upstream `main` branch. It uses Python 3.12 and a non-root Docker container, and does not auto-update code.

## One-time preparation

The host must have Docker Compose v2 and the Linux system account `bots` with UID 110 and GID 119.

On **potpal**:

```bash
sudo install -d -o bots -g bots -m 0750 /srv/discord-bots/remind
sudo install -d -o bots -g bots -m 0750 /srv/discord-bots/remind/data /srv/discord-bots/remind/logs
```

Create the local file `/srv/discord-bots/remind/environment` owned by `bots:bots` mode `0600`, with these lines (fill in values **locally**, never commit the file):

```dotenv
BOT_TOKEN_REMIND="your_separate_discord_bot_token"
CLIST_API_USERNAME="your_clist_username"
CLIST_API_KEY="your_clist_api_key"
SUPER_USERS="your_numeric_discord_user_id"
```

Enable **Server Members Intent** and **Message Content Intent** in the Discord application's Developer Portal, invite the separate bot to your guild, and grant only the required permissions.

## Run and inspect

```bash
cd ~/discord-bots/Remind-Me
git switch --track origin/potpal-deployment
sudo docker compose -f compose.potpal.yaml config --quiet
sudo docker compose -f compose.potpal.yaml up -d --build
sudo docker compose -f compose.potpal.yaml ps
sudo docker compose -f compose.potpal.yaml logs --tail=80
```

Quick Discord smoke test: `t;meta ping`. The Clist contest list is `t;clist future`. New instances need the guild settings configured via `t;help remind`.

## Updates

```bash
cd ~/discord-bots/Remind-Me
git pull --ff-only
sudo docker compose -f compose.potpal.yaml up -d --build
```

## Notes

- Persistent runtime state lives in `/srv/discord-bots/remind/data`, and logs in `/srv/discord-bots/remind/logs`. Back these up to NAS.
- This bot has no inbound TCP ports; all Discord/Clist traffic is outbound.
- The image build/runtime does not require the private token file to be in Git.
- `t;meta restart` exits with code 42; Docker restarts the container because of its restart policy, but does not download or build updated code.
- Do not run the original `run.sh` on the server; it automatically pulls and installs dependencies during each restart.
