# MIKASA MUSIC — cleaned package

This copy was cleaned from the supplied archive.

- Display/project branding changed to **MIKASA MUSIC**; Python package renamed to `MikasaMusic`.
- Removed supplied `.env`, `.en`, Telegram session, runtime log, Git history/remotes, compiled caches, cache and downloads.
- Removed old owner/admin identifiers, old support channel/group links, hard-coded old chat IDs, old upstream repository references and embedded service/API key strings.
- Added `.env.example`; fill in your own Telegram API credentials, bot token, owner ID, MongoDB URI, log group ID, support links and assistant session before deployment.
- The original archive is not modified.

## Important

The bot will not run until `.env.example` is copied to `.env` and populated with your own values. Rotate/revoke any credentials that were present in the original archive, especially the bot token, Git token, MongoDB URI and session string.

The source includes Telegram voice-chat music playback, YouTube/Spotify/SoundCloud/Telegram/Apple/Resso integrations, playlists, admin controls, group utilities, sudo controls, broadcasting, language files, database backends, assistant clients, deployment files for Docker/Heroku/Render, and an installer script.

Deployment templates were also scrubbed of old API ID/hash, MongoDB URI, owner ID, bot username, support links, and log-group ID.
