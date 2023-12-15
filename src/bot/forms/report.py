from aiogram.fsm.state import StatesGroup, State


class ReportFrom(StatesGroup):
    datetime = State()
