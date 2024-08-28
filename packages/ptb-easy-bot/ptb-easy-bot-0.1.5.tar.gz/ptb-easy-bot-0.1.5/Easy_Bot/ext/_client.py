from telegram._utils.defaultvalue import DEFAULT_80 ,DEFAULT_IP ,DEFAULT_NONE ,DEFAULT_TRUE ,DefaultValue
from telegram._utils.types import SCT, DVType, ODVInput
from typing import TYPE_CHECKING,Any,AsyncContextManager,Awaitable,Callable,Coroutine,DefaultDict,Dict,Generator,Generic,List,Mapping,NoReturn,Optional,Sequence,Set,Tuple,Type,TypeVar,Union
from telegram import Bot
from telegram.ext import Application , ContextTypes , CallbackContext , filters , CommandHandler , MessageHandler , CallbackQueryHandler , InlineQueryHandler , MessageReactionHandler , ChatJoinRequestHandler

from ._handlers import HANDLERS , MessagesHandlers
from ._commands import get_commands_data
import asyncio
from Easy_Bot.error import NoHandler


LOGO = """
........................................
.#####...####...##...##...####...#####..
.##..##.##..##..###.###..##..##..##..##.
.#####..######..##.#.##..##..##..##..##.
.##.....##..##..##...##..##..##..##..##.
.##.....##..##..##...##...####...#####..
........................................    
   ├ ᴄᴏᴘʏʀɪɢʜᴛ © 𝟸𝟶𝟸𝟹-𝟸𝟶𝟸𝟺 ᴘᴀᴍᴏᴅ ᴍᴀᴅᴜʙᴀsʜᴀɴᴀ. ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ.
   ├ ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ  ɢᴘʟ-𝟹.𝟶 ʟɪᴄᴇɴsᴇ.
   └ ʏᴏᴜ ᴍᴀʏ ɴᴏᴛ ᴜsᴇ ᴛʜɪs ғɪʟᴇ ᴇxᴄᴇᴘᴛ ɪɴ ᴄᴏᴍᴘʟɪᴀɴᴄᴇ ᴡɪᴛʜ ᴛʜᴇ ʟɪᴄᴇɴsᴇ.
"""

def built_in_error(update, context):
    print(f'Update {update} \n\nCaused error {context.error}')

class Client(Application):
    def __init__(
            self, 
            token: str, 
            port: DVType[int] = DEFAULT_80,
            webhook_url:  Optional[str] = None,
            handlers: HANDLERS = {},
    ):
        """
        Client Class for Easy_Bot

        Args:
            token (str): Telegram Bot Token
            port (int, optional): Webhook Port. Defaults to 80.
            webhook_url (str, optional): Webhook URL. Defaults to None.
            handlers (HANDLERS, optional): Handlers for Bot. Defaults to {}.
        """
        self.token = token
        self.port = port
        self.webhook_url = webhook_url
        self.handlers = handlers
   
        self.app = super().builder().token(self.token).build()

        if self.handlers == {} or self.handlers ==  None:
            raise NoHandler
        
        messages:MessagesHandlers = handlers.messages
        commands = handlers.commands
        callback = handlers.callback
        inline = handlers.inline
        join_request = handlers.join_request
        reaction = handlers.reaction
        error = handlers.error
        self.start_function = handlers.start_function

        if commands:
            commands_dir = commands
            commands = get_commands_data(commands_dir)
            for command , cmd_func in commands:
                self.app.add_handler(CommandHandler(command , cmd_func))

        if messages.text:self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,messages.text))
        if messages.poll:self.app.add_handler(MessageHandler(filters.POLL,messages.poll))
        if messages.reply:self.app.add_handler(MessageHandler(filters.REPLY,messages.reply))
        if messages.audio:self.app.add_handler(MessageHandler(filters.AUDIO,messages.audio))
        if messages.video:self.app.add_handler(MessageHandler(filters.VIDEO,messages.video))
        if messages.voice:self.app.add_handler(MessageHandler(filters.VOICE,messages.voice ))
        if messages.caption:self.app.add_handler(MessageHandler(filters.CAPTION,messages.caption))
        if messages.contact:self.app.add_handler(MessageHandler(filters.CONTACT,messages.contact))
        if messages.location:self.app.add_handler(MessageHandler(filters.LOCATION,messages.location))
        if messages.sticker:self.app.add_handler(MessageHandler(filters.Sticker.ALL,messages.sticker))
        if messages.document:self.app.add_handler(MessageHandler(filters.ATTACHMENT,messages.document))
        if messages.new_chat_photo:self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_PHOTO,messages.new_chat_photo))
        if messages.new_chat_title:self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_TITLE,messages.new_chat_title))
        if messages.new_chat_member:self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS,messages.new_chat_member))
        if messages.left_chat_memeber:self.app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER,messages.left_chat_memeber))
        if messages.pinned_message:self.app.add_handler(MessageHandler(filters.StatusUpdate.PINNED_MESSAGE,messages.pinned_message))
        if messages.message_auto_delete_timer_changed:self.app.add_handler(MessageHandler(filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED,messages.message_auto_delete_timer_changed))
        if messages.all_status:self.app.add_handler(MessageHandler(filters.StatusUpdate.ALL,messages.all_status))

        if callback:
            self.app.add_handler(CallbackQueryHandler(callback))

        if inline:
            self.app.add_handler(InlineQueryHandler(inline))

        if join_request:
            self.app.add_handler(ChatJoinRequestHandler(join_request))

        if reaction:
            self.app.add_handler(MessageReactionHandler(reaction))

        if error:
            self.app.add_error_handler(error)
        else:
            self.app.add_error_handler(built_in_error)


    async def trigger_callback(self):
        await asyncio.sleep(5)
        asyncio.create_task(self.start_function())

    async def set_webhook(self):
        if self.webhook_url:
            bot = Bot(self.token)
            await bot.set_webhook(self.webhook_url + "/" + self.token)
        if self.start_function:
            asyncio.create_task(self.trigger_callback())
        
    def stop(self):
        """
        Stop the bot. This method will stop the bot.
        """
        self.app.stop()



    def start(
            self,
            drop_pending_updates:Optional[bool] = None,
            ):
        """
        Start the bot. This method will start the bot in either webhook or polling mode,
        depending on whether a webhook_url is provided.

        Args:
            drop_pending_updates (bool, optional): Whether to drop pending updates. Defaults to None.

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.set_webhook())
        print(LOGO + "\n\n" )
        print("Bot Started")
        
        try:
            if self.webhook_url != None:
                print("running webhook...")
                self.app.run_webhook(
                    port=self.port,
                    listen="0.0.0.0",
                    webhook_url=self.webhook_url,
                    drop_pending_updates = drop_pending_updates,
                )
            else:
                print("Bot polling..")
                self.app.run_polling(
                    drop_pending_updates = drop_pending_updates,
                )
        except Exception as e:
            print(e)
            raise
        print("Bot Stoped")

