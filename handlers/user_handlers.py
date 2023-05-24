from aiogram import Dispatcher, types, Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, URLInputFile

from aiogram.fsm.context import FSMContext

from database.db_func import report, get_last_value

router: Router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    text = (f'Привет!\n'
            f'Команды:\n'
            f'/report - Получить отчет\n'
            f'/last - Последний твит из базы\n'
            )
    await message.answer(text)


@router.message(Command(commands=["report"]))
async def process_start_command(message: Message):
    text = await report()
    await message.answer(text)


@router.message(Command(commands=["last"]))
async def process_start_command(message: Message):
    text = await get_last_value()
    await message.answer(text)
