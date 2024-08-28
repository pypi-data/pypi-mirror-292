from Easy_Bot.error import UnauthorizedCommandError





async def unauthorized(update, context):
    text =  "<b>Unauthorized command detected! </b>\n\nYou do not have permission to use this command."
    await update.message.reply_text(text=text,parse_mode='HTML')
    raise UnauthorizedCommandError