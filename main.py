import asyncio
import logging.config
import time


from config_data.config import LOGGING_CONFIG
from database.db_func import add_new_tweets
from services.func import get_tweet

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


async def main():
    logger.info('Запуск скрипта')
    url = 'https://twitter.com/WhaleBotRektd/with_replies'
    while True:
        try:
            scanned_tweets = get_tweet(url)
            print(scanned_tweets)
            if scanned_tweets:
                await add_new_tweets(scanned_tweets)
            time.sleep(1)
        except Exception as error:
            logger.critical('Ошибка', exc_info=True)
            time.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())

