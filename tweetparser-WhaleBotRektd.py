import asyncio
import logging.config
import time


from config_data.config import LOGGING_CONFIG
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
            await asyncio.sleep(5)
        except Exception as error:
            print(error)
            logger.critical('Ошибка', exc_info=True)
            try:
                await send_message_tg(f'Критическая ошибка в боте tweetparser-WhaleBotRektd:\n{str(error)}', '585896156')
            except Exception:
                pass
        time.sleep(1)


if __name__ == '__main__':
    print('Запуск парсера https://twitter.com/WhaleBotRektd/with_replies')
    asyncio.run(main())

