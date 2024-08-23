import time
import os
import shutil
import random

import sqlite3
import pandas as pd
from io import StringIO

import selenium.common.exceptions
from webdriver_hj3415 import drivers
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def is_file_old(file_path: str, period: int = 30) -> bool:
    import os
    import datetime

    # 파일의 생성 시간 가져오기
    try:
        creation_time = os.path.getctime(file_path)
    except FileNotFoundError:
        return True
    creation_time_readable = datetime.datetime.fromtimestamp(creation_time)
    now = datetime.datetime.now()

    # print(f"파일 경로: {file_path}")
    # print(f"파일 생성 시간: {creation_time_readable}")
    # print(f"현재 시간: {now}")

    timedelta = now - creation_time_readable
    print(f"{os.path.basename(file_path)}은 {timedelta.days}일 전에 만들어졌습니다.")

    if timedelta.days >= period:
        return True
    else:
        return False


def download_krx300(save_to: str, headless=False):
    """
    tigeretf 사이트에서 krx300 구성종목 파일을 다운로드한다.
    파일다운은 save_to 에 설정된 파일경로를 사용한다.
    :return:
    """
    # 임시폴더 정리
    shutil.rmtree(save_to, ignore_errors=True)

    print(f'Download krx300 file and save to {save_to}.')
    # tiger etf krx300 주소
    url = "https://www.tigeretf.com/ko/product/search/detail/index.do?ksdFund=KR7292160009"

    webdriver = drivers.get_chrome(headless=headless, temp_dir=save_to)

    webdriver.get(url)
    webdriver.implicitly_wait(10)

    # 구성 종목 다운 버튼
    btn_xpath = '//*[@id="formPdfList"]/div[2]/div[1]/div/div/a'

    trying = 0
    while True:
        try:
            trying += 1
            WebDriverWait(webdriver, 10).until(
                EC.element_to_be_clickable((By.XPATH, btn_xpath))
            )
            break
        except selenium.common.exceptions.TimeoutException:
            if trying > 2:
                raise Exception(f"{url} 페이지 로딩에 문제가 있습니다.")
            print("다운로드 버튼이 준비되지 않아서 다시 시도합니다.")
            webdriver.refresh()
            time.sleep(2)

    button = webdriver.find_element(By.XPATH, btn_xpath)
    button.click()

    time.sleep(2)

    webdriver.close()


def get(headless=True, rnd_pick: int | None = None) -> List:
    """
    krx300 종목코드 리스트를 반환한다.
    :param headless: 테스트 상 headless 모드도 가능했다.
    :param rnd_pick: 원하는 갯수를 넣으면 임의 갯수의 종목을 반환한다.
    :return: [종목코드, ....]
    """
    TEMP_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '_down_krx')
    EXCEL_FILE = os.path.join(TEMP_DIR, 'PDF_DATA.xls')

    trying = 0

    # krx 종목구성 파일이 30일이전 것이라면 새로 받는다.
    if is_file_old(EXCEL_FILE, 30):
        download_krx300(TEMP_DIR, headless=headless)

    while True:
        try:
            trying += 1
            # 파일 인코딩을 utf-8로 해야 한글이 제대로 나온다.
            with open(EXCEL_FILE, 'r', encoding='utf-8') as file:
                html_content = file.read()
            break
        except FileNotFoundError:
            if trying > 2:
                raise Exception(f"{EXCEL_FILE} 파일 다운로드에 문제가 있습니다.")
            download_krx300(TEMP_DIR, headless=headless)

    html_content_io = StringIO(html_content)
    # 다운받은 파일이 xls로 엑셀파일 확장자이지만 실제는 html으로 저장됨.
    df = pd.read_html(html_content_io, skiprows=2, header=0, index_col=0)[0]
    # print(df)

    # 데이터프레임을 데이터베이스에 저장
    conn = sqlite3.connect('krx.db')
    tablename = 'krx300'
    df.to_sql(tablename, conn, if_exists='replace', index=False)

    cursor = conn.cursor()

    # 종목코드만 뽑아내는 쿼리. 종목코드는 6자리인 것만 추출한다.
    select_query = f'''
    SELECT 종목코드 FROM {tablename} WHERE 종목코드 LIKE '______'
    '''

    cursor.execute(select_query)
    rows = cursor.fetchall()

    # print(rows)
    codes = []
    for code, in rows:
        codes.append(code)

    cursor.close()
    conn.close()

    if rnd_pick is None:
        return codes
    else:
        return random.sample(codes, rnd_pick)


if __name__ == '__main__':
    print(get(rnd_pick=5))
    print(get())
