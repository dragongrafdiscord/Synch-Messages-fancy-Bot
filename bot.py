import discord
import asyncio
import aiohttp
import json
import os
import datetime
import traceback
import io 

from discord.ext import commands
from discord import app_commands

CONFIG_FILE = "config.json"
LOG_DIR = "logs"
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

config = json.load(open(CONFIG_FILE))
TOKEN = config["bot_token"]
CHANNEL_PAIRS = {int(k): int(v) for k, v in config["channel_pairs"].items()}
WHITELIST = config["whitelist"]
WEBHOOK_DB_FILE = config["webhook_storage"]
SYNC_LOG_FILE = "synced_messages.json"

def log_error(error_msg):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    archive_path = os.path.join(ARCHIVE_DIR, f"crash_{timestamp}.log")
    
    print("❌ Error:")
    print(error_msg)
    
    with open(ERROR_LOG_FILE, "w") as f:
        f.write(error_msg)
    with open(archive_path, "w") as f:
        f.write(error_msg)


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def is_authorized(interaction: discord.Interaction) -> bool:
    user_id = interaction.user.id
    return user_id in WHITELIST or any(role.permissions.administrator for role in interaction.user.roles)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

async def get_or_create_webhook(channel: discord.TextChannel) -> discord.Webhook:
    webhook_db = load_json(WEBHOOK_DB_FILE)
    channel_id_str = str(channel.id)

    if channel_id_str in webhook_db:
        try:
            return discord.Webhook.from_url(webhook_db[channel_id_str], client=bot)
        except discord.NotFound:
            pass  # If the stored webhook is invalid or deleted

    webhook = await channel.create_webhook(name="SyncBot")
    webhook_db[channel_id_str] = webhook.url
    save_json(WEBHOOK_DB_FILE, webhook_db)
    return webhook

async def send_message_as_user(webhook: discord.Webhook, message: discord.Message):
    files = []
    for attachment in message.attachments:
        fp = io.BytesIO(await attachment.read())
        files.append(discord.File(fp=fp, filename=attachment.filename))

    send_kwargs = {
        "content": message.content or None,
        "username": message.author.display_name,
        "avatar_url": message.author.display_avatar.url,
        "files": files,
        "allowed_mentions": discord.AllowedMentions.none(),
    }

    if message.embeds:
        send_kwargs["embeds"] = message.embeds

    await webhook.send(**send_kwargs)


@tree.command(name="sync", description="Sync messages from source to target channels")
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not is_authorized(interaction):
        await interaction.followup.send("❌ You are not authorized to run this command.")
        return

    try:
        synced_log = load_json(SYNC_LOG_FILE)

        for source_id, target_id in CHANNEL_PAIRS.items():
            print(f"🔄 Syncing from {source_id} to {target_id}")
            source = bot.get_channel(source_id)
            target = bot.get_channel(target_id)

            if not source:
                print(f"⚠️ Source channel {source_id} not found.")
                continue
            if not target:
                print(f"⚠️ Target channel {target_id} not found.")
                continue

            webhook = await get_or_create_webhook(target)
            synced_ids = synced_log.get(str(source_id), [])
            messages = [m async for m in source.history(limit=None, oldest_first=True)]

            print(f"📨 Found {len(messages)} messages in source.")

            for message in messages:
                if message.id in synced_ids:
                    continue
                if message.author.bot or message.webhook_id:
                    continue

                print(f"➡️ Syncing message ID {message.id} from {message.author}")
                await send_message_as_user(webhook, message)
                synced_ids.append(message.id)
                synced_log[str(source_id)] = synced_ids
                save_json(SYNC_LOG_FILE, synced_log)
                await asyncio.sleep(1.5)

        await interaction.followup.send("✅ Sync complete.")
    except Exception as e:
        err = traceback.format_exc()
        log_error(err)
        await interaction.followup.send(f"❌ An error occurred during sync. See logs.")


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
