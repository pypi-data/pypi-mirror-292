import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_hj3415.miscraper.mis.spiders.mi import MiSpider
from scraper_hj3415.miscraper.mis.spiders.mihistory import MIHistory
from webdriver_hj3415 import drivers


# 웹드라이버는 실험상 크롬드라이버가 제일 안정적이고 멀티테스킹도 가능하였다.
# 크롬 드라이버의 headless 여부 결정
headless = True
driver_version = None
browser = "chrome"


def chcwd(func):
    """
    scrapy는 항상 프로젝트 내부에서 실행해야 하기 때문에 일시적으로 현재 실행 경로를 변경해주는 목적의 데코레이션 함수
    이 함수는 run.py에 속해있어야지 작동한다
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        before_cwd = os.getcwd()
        after_cwd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(after_cwd)
        func(*args, **kwargs)
        os.chdir(before_cwd)
    return wrapper


@chcwd
def mi():
    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(MiSpider)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림


@chcwd
def mihistory(years: int):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(MIHistory, webdriver=webdriver, years=years)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()



