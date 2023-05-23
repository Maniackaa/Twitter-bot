import asyncio
import logging.config
import sys
import time


from config_data.config import LOGGING_CONFIG
from database.db import init_models
from database.db_func import add_new_tweets
from services.func import get_tweet, send_message_tg

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


async def main():
    logger.info('Запуск скрипта')

    url = 'https://twitter.com/WhaleBotRektd/with_replies'
    while True:
        try:
            scanned_tweets = get_tweet(url)
            logger.info(f'Твиты: {scanned_tweets}')
            if scanned_tweets:
                await add_new_tweets(scanned_tweets)
            time.sleep(1)
        except Exception as error:
            logger.critical('Ошибка', exc_info=True)
            try:
                await send_message_tg(f'Критическая ошибка в боте tweetparser-WhaleBotRektd:\n{str(error)}', '585896156')
            except Exception:
                pass
            time.sleep(60)


if __name__ == '__main__':
    if sys.version_info[:2] == (3, 7):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_models())
    loop.close()
    asyncio.run(main())

