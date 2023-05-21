from aiogram import Dispatcher, types, Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, URLInputFile

from aiogram.fsm.context import FSMContext

from database.db_func import report

router: Router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    text = 'Привет!'
    await message.answer(text)


@router.message(Command(commands=["отчет"]))
async def process_start_command(message: Message):

    text = await report()
    await message.answer(text)


