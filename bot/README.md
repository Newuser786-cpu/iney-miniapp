# ИНЕЙ Telegram bot runtime

This is a separate, informational Telegram bot service. The existing root GitHub Pages Mini App remains unchanged.

## Deploy
Deploy the `bot/` directory as a Docker service on Railway or a VPS. Set the Dockerfile path to `Dockerfile` when the root directory is `bot`.

Required environment variables:
- `TELEGRAM_BOT_TOKEN`: obtain from BotFather. Never commit the token.
- `MINI_APP_URL`: public HTTPS address of the deployed GitHub Pages Mini App, e.g. `https://newuser786-cpu.github.io/iney-miniapp/`.

The service runs long polling. Run exactly one replica, with an always-on worker (not a static site or scale-to-zero web service). On startup it clears any previously configured webhook without discarding queued updates. Do not run a second polling instance or webhook consumer for the same token.

## Local smoke test
```bash
cd bot
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN='your-token'
export MINI_APP_URL='https://newuser786-cpu.github.io/iney-miniapp/'
python main.py
```

Send `/start` to the bot in Telegram and verify the informational Mini App button opens the hosted page. If it does not, check the worker logs, the GitHub Pages deployment, and BotFather Mini App settings. The button only works in a Telegram client supporting Web Apps.

No purchases, payment processing, orders or customer data storage are implemented.
