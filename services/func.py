import datetime
import logging
import requests

from seleniumwire import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import re

from config_data.config import config

logger = logging.getLogger('my_logger')


def send_message_tg(message: str, chat_id: str):
    """Отправка сообщения через чат-бот телеграмма"""
    url = (f'https://api.telegram.org/'
           f'bot{config.tg_bot.token}/'
           f'sendMessage?'
           f'chat_id={chat_id}&'
           f'text={message}')
    requests.get(url)


def find_weth(text):
    res = re.findall('WETH liquidity: (\d+) ', text)
    return int(res[0])


def get_browser():
    proxy = {'http': f'http://{config.proxy.user}:{config.proxy.password}@'
                     f'{config.proxy.adress}:{config.proxy.port}',
             'https': f'https://{config.proxy.user}:{config.proxy.password}@'
                      f'{config.proxy.adress}:{config.proxy.port}',
             }
    s_options = {
        'proxy': proxy
    }
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1200,1000")
    options.add_argument('--headless')
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    user_agent = 'Mozilla/5.0 (Linux; arm_64; Android 13; SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.48 YaBrowser/21.3.4.59 Mobile Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(seleniumwire_options=s_options, options=options)
    driver.set_page_load_timeout(60)
    return driver


def get_tweet(page_url):
    """Читает первые твиты со ссылки"""
    logger.debug(f'Читаем твиты с {page_url}')
    with get_browser() as browser:
        browser.get(page_url)
        xpatch = '//article[@data-testid="tweet"]'
        logger.debug('Ждем')
        try:
            WebDriverWait(browser, 20).until(
            expected_conditions.visibility_of_element_located(
                (By.XPATH, xpatch)))
        except TimeoutException as error:
            logger.warning(f'{error}')
            logger.warning(f'Не нашли блок {xpatch} в {page_url}')
            return
        logger.debug(f'Нашли блок {xpatch}')
        tweet_blocks = browser.find_elements(By.XPATH, xpatch)
        data = []
        for tweet_block in tweet_blocks:
            tweet_time = tweet_block.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            text = tweet_block.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]').text
            logger.debug(f'{tweet_time} {text}')
            data.append((tweet_time, text))
        logger.debug(data)
        return data


def find_start_period(
        target_day: int,
        current_day: datetime = datetime.datetime.now()) -> datetime:
    """Возвращает datetime прошлонедельного заданного дня недели"""
    delta_to_day = target_day - current_day.weekday()
    if delta_to_day > 0:
        res_delta_day = 7 - delta_to_day
    else:
        res_delta_day = delta_to_day
    result_day = current_day + datetime.timedelta(days=res_delta_day)
    result_day = result_day.replace(hour=0, minute=0, second=0, microsecond=0)
    return result_day

# x = find_start_period(0, datetime(2023, 5, 15, 0, 0, 0, 0))
# print(x)
