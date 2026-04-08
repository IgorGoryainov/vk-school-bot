# vk-school-bot

A VKontakte bot for a school class that answers homework and schedule questions without cluttering the class chat.

Built for class 11A at school №63, Samara. Students subscribe to daily homework/schedule broadcasts and can query them on demand.

## What it does

- Responds to commands like `5` (today's homework), `7` (today's schedule), `8` (tomorrow's schedule)
- Lets subscribed students receive daily homework and schedule broadcasts
- Lets teachers/admins post homework with `101 <day> <text>`
- Resets homework storage each week automatically

## Stack

- Python 3.8+
- [vk-api](https://github.com/python273/vk_api) for VKontakte API access

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`) and set your VK bot token:

```
VK_TOKEN=your_vk_token_here
```

Get a token from [vk.com/dev](https://vk.com/dev) — create a community, then issue a community API token with `messages` permissions.

## Running

```bash
VK_TOKEN=your_token python src/bot.py
```

The bot polls unanswered conversations and responds to the first one each cycle.

## Commands

| Command | Description |
|---------|-------------|
| `help` | List all commands |
| `1` / `2` | Subscribe / unsubscribe from homework broadcasts |
| `3` / `4` | Subscribe / unsubscribe from schedule broadcasts |
| `5` | Today's homework |
| `6` | Tomorrow's homework |
| `7` | Today's schedule |
| `8` | Tomorrow's schedule |
| `9` | Links to class textbooks |
| `101 <day> <text>` | Save homework for a day (1=Mon, 6=Sat) |

## Data

Subscriber lists and homework entries are stored in the `data/` directory as plain text files. These files are not version-controlled — they are created at runtime. Back up the `data/` directory if you redeploy.
