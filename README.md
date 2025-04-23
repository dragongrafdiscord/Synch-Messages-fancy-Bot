
# Synch Messages Bot

This bot syncs messages (including images, GIFs, and videos) from one channel to another using Discord webhooks.

## 📦 Installation

1. Download or clone the repository:
```
git clone https://github.com/dragongrafdiscord/Synch-Messages-Bot.git
cd Synch-Messages-Bot
```

2. First time setup (creates necessary files and folders):
```
first_start.bat
```

3. To start the bot in the future:
```
start.bat
```

## ⚙️ Configuration

Edit `config.json` to set your bot token, source/destination channels, and whitelist user IDs.

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "channel_pairs": {
    "source_channel_id": "destination_channel_id"
  },
  "whitelist": [123456789012345678]
}
```

---

Created by [dragongrafdiscord](https://github.com/dragongrafdiscord)
