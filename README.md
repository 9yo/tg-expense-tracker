## Setup Google Sheets Api Auth
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project
3. Create a new service account
4. Download the json file
5. Copy the json file to `./service_credentials.json`
6. **Give access to the service account to the spreadsheet**

## Setup Telegram Bot
1. Go to [BotFather](https://t.me/botfather)
2. Create a new bot
3. Get the token

## Setup for local run
```bash
poetry install
poetry run ... # here is depensds on that you want to run
# poetry run python -m src.bot (or CMD + R on any file in PyCharm)
# You must set up env variables also
TELEGRAM_BOT_TOKEN=<your telegram token>
SPREADSHEET_ID=<your spreadsheet ID>
``` 

## Tests
```bash
poetry run pytest
```

## Deta Deploy
```bash
space login
space new
```
### Create your Spacefile

```yaml
# Spacefile Docs: https://go.deta.dev/docs/spacefile/v0
v: 0
icon: src/static/icon.png
micros:
  - name: <your micro name>
    src: .
    engine: python3.9
    primary: true
    public_routes:
      - '/webhook'
    dev: 'make dev'
    presets:
      env:
        - name: TELEGRAM_BOT_TOKEN
          description: Telegram bot token
          default: <your telegram token>
        - name: SPREADSHEET_ID
          description: Google spreadsheet ID
          default: <your spreadsheet ID>
```

``` bash
space deploy
....
🎉  Successfully pushed your code and updated your Builder instance!
Builder instance: https://.....deta.app
# Go to your deployed instance https://.....deta.app/set_webhook
```



## Troubleshooting
If you facing some problems like sending messages to the bot, but not receiving anything.
You can check webhook status by sending GET request to `https://api.telegram.org/bot<your telegram token>/getWebhookInfo`
