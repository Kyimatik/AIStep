from aiogram.fsm.state import StatesGroup , State
#Получение данных 
class Cordinates(StatesGroup):
    place = State()
    radius = State()
    prefer = State()


