from telegram._utils.defaultvalue import DEFAULT_80 ,DEFAULT_IP ,DEFAULT_NONE ,DEFAULT_TRUE ,DefaultValue
from telegram._utils.types import SCT, DVType, ODVInput
from typing import TYPE_CHECKING,Any,AsyncContextManager,Awaitable,Callable,Coroutine,DefaultDict,Dict,Generator,Generic,List,Mapping,NoReturn,Optional,Sequence,Set,Tuple,Type,TypeVar,Union

from telegram.ext import Application , ContextTypes , CallbackContext , filters , CommandHandler , MessageHandler , CallbackQueryHandler , InlineQueryHandler , MessageReactionHandler , ChatJoinRequestHandler

from ._handlers import HANDLERS , MessagesHandlers




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
            TOKEN: str, 
            PORT: DVType[int] = DEFAULT_80,
            WEBHOOK_URL:  Optional[str] = None,
            HANDLERS: HANDLERS = {},
    ):
    
        self.token = TOKEN
        self.port = PORT
        self.webhook_url = WEBHOOK_URL
        self.handlers = HANDLERS
        self.app = Application.builder().token(self.token).build()

        if self.handlers == {}:
            raise "No Handlers found , please set handlers to start bot"
        
        commands = (HANDLERS.commands).items()
        messages:MessagesHandlers = HANDLERS.messages
        callback = HANDLERS.callback
        inline = HANDLERS.inline
        join_request = HANDLERS.join_request
        reaction = HANDLERS.reaction
        error = HANDLERS.error


        for command , cmd_func in commands:
            self.app.add_handler(CommandHandler(command , cmd_func))

        if messages.TEXT:self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,messages.TEXT))
        if messages.POLL:self.app.add_handler(MessageHandler(filters.POLL,messages.POLL))
        if messages.REPLY:self.app.add_handler(MessageHandler(filters.REPLY,messages.REPLY))
        if messages.AUDIO:self.app.add_handler(MessageHandler(filters.AUDIO,messages.AUDIO))
        if messages.VIDEO:self.app.add_handler(MessageHandler(filters.VIDEO,messages.VIDEO))
        if messages.VOICE:self.app.add_handler(MessageHandler(filters.VOICE,messages.VOICE ))
        if messages.CAPTION:self.app.add_handler(MessageHandler(filters.CAPTION,messages.CAPTION))
        if messages.CONTACT:self.app.add_handler(MessageHandler(filters.CONTACT,messages.CONTACT))
        if messages.LOCATION:self.app.add_handler(MessageHandler(filters.LOCATION,messages.LOCATION))
        if messages.STICKER:self.app.add_handler(MessageHandler(filters.Sticker.ALL,messages.STICKER))
        if messages.DOCUMENT:self.app.add_handler(MessageHandler(filters.ATTACHMENT,messages.DOCUMENT))
        if messages.ALLSTATUS:self.app.add_handler(MessageHandler(filters.StatusUpdate.ALL,messages.ALLSTATUS))
        if messages.NEW_CHAT_PHOTO:self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_PHOTO,messages.NEW_CHAT_PHOTO))
        if messages.NEW_CHAT_MEMBERS:self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS,messages.NEW_CHAT_MEMBERS))
        if messages.LEFT_CHAT_MEMBER:self.app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER,messages.LEFT_CHAT_MEMBER))
        if messages.PINNED_MESSAGE:self.app.add_handler(MessageHandler(filters.StatusUpdate.PINNED_MESSAGE,messages.PINNED_MESSAGE))
        if messages.MESSAGE_AUTO_DELETE_TIMER_CHANGED:self.app.add_handler(MessageHandler(filters.StatusUpdate.MESSAGE_AUTO_DELETE_TIMER_CHANGED,messages.MESSAGE_AUTO_DELETE_TIMER_CHANGED))

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

        
    def start(
            self,
            drop_pending_updates:Optional[bool] = None,
            ):
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
                print("running polling..")
                self.app.run_polling(
                    drop_pending_updates = drop_pending_updates,
                )
        except Exception as e:
            print(e)
        print("Bot Stoped")
