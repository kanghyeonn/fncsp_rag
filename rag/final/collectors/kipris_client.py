import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time

def open_kipris(download_dir):
    # Chrome 옵션 설정
    options = uc.ChromeOptions()

    # 자동화 탐지 최소화 옵션
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
    )

    # ✅ 다운로드 경로 설정 (핵심)
    prefs = {
        "download.default_directory": download_dir,   # 저장 경로
        "download.prompt_for_download": False,        # 다운로드 창 제거
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # 필요 시 헤드리스 (KIPRIS는 headless에서 막힐 수 있음)
    # options.add_argument("--headless=new")

    # 브라우저 실행
    driver = uc.Chrome(
        options=options,
        use_subprocess=True
    )

    # KIPRIS 접속
    driver.get("https://www.kipris.or.kr/khome/main.do")

    # 페이지 로딩 대기
    time.sleep(3)

    return driver

def click_detail_search(driver, timeout=10):
    """
    KIPRIS 메인 페이지에서 '상세검색' 버튼 클릭
    """

    wait = WebDriverWait(driver, timeout)

    detail_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "btnOpenSearchDetail"))
    )

    detail_btn.click()

def input_ipc_keyword(driver, keyword: str, timeout: int = 10):
    """
    KIPRIS 상세검색 - IPC 입력창에 검색어 입력
    (ID 중복 이슈 대응: id + class 조합 사용)
    """

    wait = WebDriverWait(driver, timeout)

    ipc_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input#sd01_g05_text_01.f-control")
        )
    )

    # # 스크롤 보정 (겹침 방지)
    # driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ipc_input)
    #
    # # 포커스 + 기존 값 제거
    # ipc_input.click()
    # ipc_input.send_keys(Keys.CONTROL, "a")
    # ipc_input.send_keys(Keys.DELETE)

    # 값 입력
    ipc_input.send_keys(keyword)

    # JS 기반 값 세팅 (KIPRIS 내부 바인딩 보정)
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """,
        ipc_input,
        keyword
    )

def click_detail_search_button(driver, timeout: int = 10):
    """
    KIPRIS 상세검색 - '검색하기' 버튼 클릭
    """

    wait = WebDriverWait(driver, timeout)

    search_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.btn-search[onclick='doDetailSearch()']")
        )
    )

    # 스크롤 보정 (고정 헤더/레이어 대비)
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        search_btn
    )

    try:
        # 1차: 일반 클릭
        search_btn.click()
    except Exception:
        # 2차: JS 클릭 (overlay/차단 대응)
        driver.execute_script("arguments[0].click();", search_btn)

def click_result_statistics_button(driver, timeout: int = 10):
    """
    KIPRIS 검색 결과 페이지 - '결과 분류통계' 버튼 클릭
    """

    wait = WebDriverWait(driver, timeout)

    stat_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.btn-statistics[onclick='openResultStatis()']")
        )
    )

    # 스크롤 보정 (상단 고정 영역/레이어 대비)
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        stat_btn
    )

    try:
        # 1차: 일반 클릭
        stat_btn.click()
    except Exception:
        # 2차: JS 클릭
        driver.execute_script("arguments[0].click();", stat_btn)

def click_excel_download(driver, timeout: int = 10):
    """
    KIPRIS 결과 분류통계 - 엑셀 다운로드 버튼 클릭
    """

    wait = WebDriverWait(driver, timeout)

    excel_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.btn-excel[href^='javascript:excelDownloadByStatis']")
        )
    )

    # 스크롤 보정
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        excel_btn
    )

    try:
        # 1차: 일반 클릭
        excel_btn.click()
        time.sleep(2)
    except Exception:
        # 2차: JS 클릭
        driver.execute_script("arguments[0].click();", excel_btn)
        time.sleep(2)

def download_statistics_data_from_kipris(download_dir, keyword):
    driver = None
    time.sleep(3)
    try:
        driver = open_kipris(download_dir)
        click_detail_search(driver)
        input_ipc_keyword(driver, keyword)
        click_detail_search_button(driver)
        click_result_statistics_button(driver)
        click_excel_download(driver)
        driver.quit()
    except Exception as e:
        raise RuntimeError(
            f"KIPRIS 통계 다운로드 실패 (IPC={keyword})"
        ) from e
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    KIPRIS_DIR = r"/rag/ipc_statistics"
    download_statistics_data_from_kipris(KIPRIS_DIR, "G06Q50/16*G06F17/30*G06Q30/02")