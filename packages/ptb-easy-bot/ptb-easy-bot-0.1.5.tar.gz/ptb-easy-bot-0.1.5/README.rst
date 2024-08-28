Introduction
============

We’ve built the bot framework you’ve been waiting for!
======================================================

Unlock seamless Telegram bot development with our intuitive, powerful framework. Tap into our thriving community for support and inspiration

Installing
==========

You can install or upgrade ``ptb-easy-bot`` via

.. code:: shell

    $ pip install ptb-easy-bot --upgrade

To install a pre-release, use the ``--pre`` `flag <https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-pre>`_ in addition.


Quick Start
===========
::

    from Easy_Bot import update , InlineReplyMarkup , bot
    from Easy_Bot.ext import Client , HANDLERS , MessagesHandlers , ContextTypes , CallbackContext
    import asyncio
    import os

    TOKEN = os.environ.get('TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
    PORT = int(os.environ.get('PORT', '8443'))

    async def main():
        if WEBHOOK_URL:
            Bot = bot(TOKEN)
            await Bot.set_webhook(WEBHOOK_URL + "/" + TOKEN)
        
    async def start_command(update: update, context: ContextTypes.DEFAULT_TYPE):
        # await update.message.reply_text("Hello..")
        keyboard = [
            ['test - test'],
            ['test 01 - https://t.me/pamod_madubashana','test 02 - test 02'],
            ['test 03 - inline_in_other']
        ]

        reply_markup = InlineReplyMarkup(keyboard)
        await update.message.reply_text(text="hello",reply_markup=reply_markup)

    async def message_handle_func(update: update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(update.effective_message.text)

    Handlers = HANDLERS(
        commands = {
            'start' : start_command,
        },
        messages = MessagesHandlers(TEXT=message_handle_func),

    )

    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        app = Client(TOKEN=TOKEN,PORT=PORT,WEBHOOK_URL=WEBHOOK_URL,HANDLERS=Handlers)
        app.start()
        
