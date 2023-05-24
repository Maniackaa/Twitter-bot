import asyncio
import datetime
import logging.config
import re
import time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from config_data.config import config, LOGGING_CONFIG
from database.db import Tweet, engine, BotSettings
from services.func import find_start_period



logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger('my_logger')
bot_log = logging.getLogger('bot_logger')

def response_tweet(tweet_text: str):
    """Читает твит и возвращает объем если BTCUSDT|BTCUSD|XBTUSDT|XBTUSD|XBTUSDT"""
    logger.debug(f'Распознаем {tweet_text}')
    pattern = '([Ss]hort|[Ll]ong).+(BTCUSDT|BTCUSD|XBTUSD|XBTUSDT) @ \$(.+):.+\$(\S+)$'
    search = re.findall(pattern, tweet_text)
    if search:
        operation = search[0][0]
        coin = search[0][1]
        price = search[0][2]
        price = float(price.replace(',', ''))
        volume = search[0][3]
        volume = float(volume.replace(',', ''))
        # if operation.lower() == 'long':
        #     volume = volume * -1
        logger.debug(f'Тип: {operation} Валюта: {coin} Цена: {price} Объем: {volume}')
        return volume


async def add_new_tweets(data: list):
    """Добавляет новые твиты в базу
    [('2023-05-20T09:24:38.000Z', 'Binance Liquidated Short on 1000PEPEUSDT @ 0.00: Buy $50,502'),]"""
    for row in data:
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            tweet_date = row[0][:-1]
            tweet_text = row[1]
            new_tweet = Tweet()
            new_tweet.date = tweet_date
            new_tweet.text = tweet_text
            volume = response_tweet(new_tweet.text)
            if volume:
                new_tweet.volume = volume
            try:
                # Ищем есть ли такой твит
                result = await session.execute(select(Tweet).filter(
                    Tweet.text == new_tweet.text,
                    Tweet.date == new_tweet.date).limit(1))
                result = result.scalars().one_or_none()
                if result:
                    logger.debug(f'Запись есть в базе: {new_tweet} ')
                    continue
                session.add(new_tweet)
                await session.commit()
                logger.debug(f'Запись {new_tweet} ДОБАВЛЕНА в базу')
            except IntegrityError:
                logger.error(f'Проблема добавления запси {new_tweet}')

#
# def read_db():
#     with Session(engine) as session:
#         query = select(Tweet).order_by(Tweet.text)
#         result = session.execute(query).scalars()
#         for tweet in result:
#             print(tweet.text)
#             response_tweet(tweet.text)


async def report():
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        sart_period = find_start_period(0)
        long_query = select(Tweet.volume).filter(
            Tweet.text.contains('Sell'),
            Tweet.volume.is_not(None),
            Tweet.date > sart_period
            )
        long_rows = await session.execute(long_query)
        long = long_rows.scalars().all()
        print(long)
        long_values = [x for x in long]
        long_sum = sum(long_values)

        short_query = select(Tweet.volume).filter(
            Tweet.text.contains('Buy'),
            Tweet.volume.is_not(None),
            Tweet.date > sart_period
        )
        short = await session.execute(short_query)
        short = short.scalars().all()
        short_values = [x for x in short]
        short_sum = sum(short_values)

        way = long_sum - short_sum
        way_word = 'Рынок вверх' if way < 0 else 'Рынок вниз'
        report_message = (
            # f'Отчет за период\n'
            f'с  {sart_period}\n'
            f'по {str(datetime.datetime.now())[:-7]}\n\n'
            # f'BTCUSDT|BTCUSD|XBTUSD|XBTUSDT\n\n'
            f'Сумма Long: {long_sum:,.0f}\n'
            # f'{long_values}\n\n'
            f'Сумма Short: {short_sum:,.0f}\n\n'
            # f'{short_values}\n\n'
            f'{way_word}\n{way:,.0f}'
        )
        return report_message


async def get_last_value():
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        query = select(Tweet).order_by(Tweet.date.desc()).limit(1)
        last = await session.execute(query)
        last = last.scalars().one_or_none()
        report_message = 'empty'
        if last:
            report_message = (
                f'Последняя запись:\n'
                f'{last.date}\n'
                f'{last.text}\n'
                f'{last.volume or "-"}'
            )
        return report_message


async def get_last_volume(period, operation):
    """
    Раcчет объема последних операций за период в секундах.
    :param int period: Время в секундах.
    :param str operation: Поиск вхождения в text
    :return: объем за период
    :rtype: float
    """
    try:
        logger.debug(f'get_last_volume Секнуд назад:{period} Операция: {operation}')
        # with Session(engine) as session:
        async_session = async_sessionmaker(engine)
        async with async_session() as session:
            result = await session.execute(select(Tweet).filter(
                Tweet.volume.is_not(None),
                Tweet.text.icontains(operation),
                Tweet.date > datetime.datetime.utcnow() - datetime.timedelta(seconds=period)
                ).order_by(Tweet.date.desc()))
            tweets = result.scalars().all()
            volumes = []
            for row in tweets:
                volumes.append(row.volume)
            logger.debug(f'Объем {operation} за последние {period} секунд: {volumes}. Итого: {sum(volumes)}')
            await session.commit()
            await engine.dispose()
        logger.debug(f'Результат get_last_volume: {volumes}')
        return sum(volumes)
    except Exception as error:
        logger.error(f'Ошибка в функции get_last_volume', exc_info=True)


async def main():
    pass
    # x = await get_last_volume(120000, 'Long')
    # print(x)
    # y = await add_new_tweets([('2023-05-21T15:44:34.000Z', 'Binance Liquidated Long on ETHUSDT @ $1,798: Sell $77,566'), ('2023-05-21T15:44:19.000Z', 'Binance Liquidated Long on DOGEUSDT @ $0.07: Sell $125,512'), ('2023-05-21T15:44:18.000Z', 'Binance Liquidated Long on LDOUSDT @ $2.02: Sell $136,211'), ('2023-05-21T15:44:16.000Z', 'Binance Liquidated Long on ARBUSDT @ $1.13: Sell $51,028'), ('2023-05-21T14:25:47.000Z', 'Binance Liquidated Short on CFXUSDT @ 0.31: Buy $94,865'), ('2023-05-21T14:19:44.000Z', 'Binance Liquidated Short on SUSHIUSDT @ 0.93: Buy $134,087'), ('2023-05-21T14:19:43.000Z', 'Binance Liquidated Long on XMRUSDT @ $147: Sell $275,355'), ('2023-05-21T14:00:21.000Z', 'Binance Liquidated Short on ETHUSDT @ $1,819: Buy $73,504'), ('2023-05-21T11:16:02.000Z', 'Binance Liquidated Long on ETHUSDT @ $1,797: Sell $80,868'), ('2023-05-21T10:45:28.000Z', 'Bybit liquidated Long on BTCUSD @ $26,774: Sell $62,352'), ('2023-05-21T10:45:27.000Z', 'Bitmex Liquidated Long on XBTUSD @ $26,947: Sell $202,000'), ('2023-05-21T06:17:21.000Z', 'Binance Liquidated Long on BTCUSDT @ $26,941: Sell $167,951'), ('2023-05-21T00:50:22.000Z', 'Binance Liquidated Short on MASKUSDT @ 4.70: Buy $77,649'), ('2023-05-20T23:38:18.000Z', 'Binance Liquidated Short on BTCUSDT @ $27,180: Buy $50,364'), ('2023-05-20T17:59:18.000Z', 'Binance Liquidated Short on BNBUSDT @ $314: Buy $50,925'), ('2023-05-20T17:59:06.000Z', 'Binance Liquidated Short on ETHUSDT @ $1,835: Buy $54,516'), ('2023-05-20T17:56:11.000Z', 'Binance Liquidated Short on ETHUSDT @ $1,834: Buy $100,797'), ('2023-05-20T17:47:45.000Z', 'Binance Liquidated Short on XRPUSDT @ 0.48: Buy $97,136'), ('2023-05-20T17:46:24.000Z', 'Binance Liquidated Short on BTCUSDT @ $27,135: Buy $50,497'), ('2023-05-20T17:46:23.000Z', 'Binance Liquidated Short on ETHUSDT @ $1,831: Buy $78,255'), ('2023-05-20T17:44:56.000Z', 'Bitmex Liquidated Short on XBTUSD @ $27,040: Buy $53,100'), ('2023-05-20T17:44:56.000Z', 'Binance Liquidated Short on MASKUSDT @ 4.71: Buy $94,292'), ('2023-05-20T17:35:47.000Z', 'Binance Liquidated Short on XRPUSDT @ 0.47: Buy $78,643'), ('2023-05-20T15:01:31.000Z', 'Binance Liquidated Short on BTCUSDT @ $27,033: Buy $50,336'), ('2023-05-20T09:24:38.000Z', 'Binance Liquidated Short on 1000PEPEUSDT @ 0.00: Buy $50,502')])
    # print(y)
    # x = await report()
    # print(x)
    # y = await get_last_value()
    # print(y)
    # await set_botsettings_value('Etherscanio-parser_report_time', '15')

    # break

if __name__ == '__main__':
    asyncio.run(main())
# report()
# add_new_tweets([('2023-05-19 15:29:55', 'Binance Liquidated Long on BTCUSDT @ $26,728: Sell $246,722')])