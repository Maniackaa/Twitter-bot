import asyncio

import logging.config
from aiogram import Bot, Dispatcher

from config_data.config import LOGGING_CONFIG, config
from database.db_func import get_last_volume
from handlers import user_handlers, echo

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot_logger')


# session = AiohttpSession(proxy="http://194.67.201.131:9692")


async def timer(bot: Bot):
    """
    Каждые 10 секунд проверяет базу на сумму объемов
    :param bot:
    :return:
    """
    last_msg = ''
    while True:
        last_short = await get_last_volume(config.logic.LAST_TIME_SECONDS,
                                           'short')
        last_long = await get_last_volume(config.logic.LAST_TIME_SECONDS,
                                          'long')
        logger.debug(f'Short/long {last_short}/{last_long}')
        text = (f'Превышен порог в {config.logic.VOLUME_LIMIT}:\n'
                f'Short: {last_short}\n'
                f'Long: {last_long}'
                )
        limit = config.logic.VOLUME_LIMIT
        if (last_short > limit or last_long > limit) and text != last_msg:
            await bot.send_message(config.tg_bot.admin_ids[0], text)
            logger.debug(f'Отправлено сообщение:\n{text}')
            last_msg = text
        await asyncio.sleep(10)


async def main():
    logger.info('Starting bot')
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Регистриуем
    dp.include_router(user_handlers.router)
    dp.include_router(echo.router)
    asyncio.create_task(timer(bot))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(config.tg_bot.admin_ids[0],
                           f'Бот запущен. Лимит {config.logic.VOLUME_LIMIT}')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
