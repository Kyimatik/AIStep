from aiogram.types import ReplyKeyboardMarkup , InlineKeyboardMarkup , InlineKeyboardButton , KeyboardButton , ReplyKeyboardRemove

#Проверка все ли верно в вашем профиле!
vseverno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да 🚀",callback_data="yes")
        ]
    ],
    resize_keyboard=True
)

mainkb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1 км"),
            KeyboardButton(text="2 км"),
            KeyboardButton(text="3 км"),
            KeyboardButton(text="4 км"),
            KeyboardButton(text="5 км")
        ],
        [
            KeyboardButton(text="6 км"),
            KeyboardButton(text="7 км"),
            KeyboardButton(text="8 км"),
            KeyboardButton(text="9 км"),
            KeyboardButton(text="10 км")
        ],
        [
            KeyboardButton(text="11 км"),
            KeyboardButton(text="12 км"),
            KeyboardButton(text="13 км"),
            KeyboardButton(text="14 км"),
            KeyboardButton(text="15 км")
        ],
        [
            KeyboardButton(text="16 км"),
            KeyboardButton(text="17 км"),
            KeyboardButton(text="18 км"),
            KeyboardButton(text="19 км"),
            KeyboardButton(text="20 км")
        ]
    ],
    resize_keyboard=True
)



otmena = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена ❌")
        ]
   
    ],
    resize_keyboard=True
)

langs = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="ru-RU"),
            KeyboardButton(text="en-US"),
            KeyboardButton(text="fr-FR"),
            KeyboardButton(text="es-ES")
        ]
    ],
    resize_keyboard=True
)




