from aiogram.fsm.state import State, StatesGroup


class ReportFrom(StatesGroup):
    datetime = State()
