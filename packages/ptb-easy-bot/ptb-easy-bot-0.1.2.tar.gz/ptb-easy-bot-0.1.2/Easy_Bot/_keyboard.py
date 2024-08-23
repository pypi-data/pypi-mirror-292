from telegram import InlineKeyboardButton , InlineKeyboardMarkup


class InlineReplyMarkup:
    """Create a Reply Markup easy 

    Args:
        keyboard (list): keyboard
            A List to create keyboard with line by line 
    
        Example:
            keyboard = [
                ['test - test'],
                ['test 01 - https://t.me/link','test 02 - test 02'],
                ['test 03 - inline_in_other']
            ]
    """
    def __new__(cls, keyboard):
        new_keyboard = []
        for line in keyboard:
            new_line = []
            for data in line:
                text, button = str(data).split(' - ')
                if str(button).startswith('http'):
                    button = InlineKeyboardButton(text=text, url=button)
                elif str(button) =='inline':
                    button = InlineKeyboardButton(text=text, switch_inline_query_current_chat='')
                elif str(button) == 'inline_in_other':
                    button = InlineKeyboardButton(text=text, switch_inline_query='')
                else:
                    button = InlineKeyboardButton(text=text, callback_data=button)
                new_line.append(button)
            new_keyboard.append(new_line)
        return InlineKeyboardMarkup(new_keyboard)