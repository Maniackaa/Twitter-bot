import logging.config

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from config_data.config import LOGGING_CONFIG
from services.func import get_browser

#
# def get_logger():
#     logger = logging.getLogger(__file__)
#     logger.setLevel(logging.DEBUG)
#     format_log = logging.Formatter(u'%(filename)s:%(lineno)d #%(levelname)-8s '
#                u'[%(asctime)s]: %(message)s')
#
#     file_handler = logging.FileHandler(f"{__name__}.log", mode='w', encoding='UTF-8')
#     file_handler.setFormatter(format_log)
#     file_handler.setLevel(logging.DEBUG)
#
#     std_handler = logging.StreamHandler()
#     std_handler.setFormatter(format_log)
#     std_handler.setLevel(logging.DEBUG)
#
#     logger.addHandler(file_handler)
#     logger.addHandler(std_handler)
#     return logger


# logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


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
