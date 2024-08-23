import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper_hj3415.nfscraper.nfs.spiders.c101 import C101Spider
from scraper_hj3415.nfscraper.nfs.spiders.c106 import C106Spider
from scraper_hj3415.nfscraper.nfs.spiders.c103 import C103YSpider, C103QSpider
from scraper_hj3415.nfscraper.nfs.spiders.c104 import C104YSpider, C104QSpider
from scraper_hj3415.nfscraper.nfs.spiders.c108 import C108Spider
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
def c101(*args):
    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C101Spider, codes=args)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림


@chcwd
def c106(*args):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C106Spider, codes=args, webdriver=webdriver)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()


@chcwd
def c103y(*args):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C103YSpider, codes=args, webdriver=webdriver)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()


@chcwd
def c103q(*args):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C103QSpider, codes=args, webdriver=webdriver)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()


@chcwd
def c104y(*args):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C104YSpider, codes=args, webdriver=webdriver)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()


@chcwd
def c104q(*args):
    webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C104QSpider, codes=args, webdriver=webdriver)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    print('Retrieve webdriver...')
    webdriver.quit()


@chcwd
def c108(*args):
    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    process.crawl(C108Spider, codes=args)
    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림


@chcwd
def all_spider(*args):
    spiders = (C101Spider, C106Spider, C103YSpider, C103QSpider, C104YSpider, C104QSpider, C108Spider)
    wedrivers = []

    # Scrapy 설정 가져오기
    settings = get_project_settings()
    # CrawlerProcess 인스턴스 생성
    process = CrawlerProcess(settings)
    # 스파이더 추가 및 실행
    for Spider in spiders:
        if Spider == C101Spider or Spider == C108Spider:
            process.crawl(Spider, codes=args)
        else:
            webdriver = drivers.get(browser=browser, driver_version=driver_version, headless=headless)
            process.crawl(Spider, codes=args, webdriver=webdriver)
            wedrivers.append(webdriver)

    process.start()  # 블로킹 호출, 스파이더가 완료될 때까지 기다림

    for webdriver in wedrivers:
        print('Retrieve webdriver...')
        webdriver.quit()
