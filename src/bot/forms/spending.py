from aiogram.fsm.state import State, StatesGroup


class SpendingForm(StatesGroup):
    name = State()
    category = State()
    description = State()
    cost = State()
    currency = State()
    source = State()
    datetime = State()
    confirmation = State()
