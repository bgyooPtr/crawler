from __future__ import annotations
from datetime import datetime
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from copy import deepcopy

import traceback

from line_notify import LineNotify

line = LineNotify()
send_msg = line.send_msg


def init_driver(url):
    # driver = uc.Chrome(version_main=117)
    driver = uc.Chrome()
    driver.get(url)
    return driver


def finder_11st(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="layBodyWrap"]'))
        )
    except Exception as e:
        print(f"11st Exception: {e}")
        return

    targets = {
        "128": "/html/body/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/dl/div[2]/dd[2]/div/div[2]/ul/li[1]/button",
        "256": "/html/body/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/dl/div[2]/dd[2]/div/div[2]/ul/li[2]/button",
    }

    for k, v in targets.items():
        try:
            results = driver.find_element(By.XPATH, v).get_attribute("class")
        except:
            results = ["disabled"]

        if "disabled" in results:
            print("11st: Sold out")
        else:
            send_msg(f"11st {k} !! \n{url}")


@dataclass_json
@dataclass(eq=True)
class CrawlingData:
    name: str = field(compare=True)
    url: str = field(compare=False)

    def __hash__(self):
        return hash(self.name)

    def get(self):
        return (self.name, self.url)

    @staticmethod
    def saves(path: str, data: set[CrawlingData]):
        with open(path, "w") as f:
            f.write(json.dumps([d.to_dict() for d in data], indent=4))

    @staticmethod
    def loads(path: str) -> set[CrawlingData]:
        buf = ""
        with open(path, "r") as f:
            for line in f:
                buf += line
        dict_data = json.loads(buf)

        data = set()
        for d in dict_data:
            name = d.get("name", None)
            url = d.get("url", None)
            if name and url:
                data.add(CrawlingData(name, url))
        return data


def finder_ssg(driver, url):
    driver.get(url)
    db_file = "data.json"

    prev_data: set[CrawlingData] = CrawlingData.loads(db_file)
    data: set[CrawlingData] = set()

    try:
        title = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="_section7000792228"]/div[1]')
            )
        )

        if "iPhone 15 Pro" not in [
            e.text for e in title.find_elements(By.TAG_NAME, "h3")
        ]:
            print("ssg: Could not find iPhone 15 Pro")
            return
    except Exception as e:
        print(f"ssg Exception: {e}")
        return

    items = title.find_element(By.XPATH, "following-sibling::*[1]").find_elements(
        By.TAG_NAME, "li"
    )

    for i in items:
        data.add(
            CrawlingData(i.text, i.find_element(By.TAG_NAME, "a").get_attribute("href"))
        )
    if prev_data == data:
        print(f"ssg is not changed: {len(prev_data)}")
    else:
        send_msg(f"ssg is changed {len(prev_data)}->{len(data)}: {url}")
        prev_data = deepcopy(data)
        CrawlingData.saves(db_file, data)


def finder_wemap(driver, url):
    driver.get(url)

    try:
        lists = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[2]/div[3]/div[4]/div[1]/div/div/div[2]",
        ).find_elements(By.TAG_NAME, "li")
    except Exception as e:
        print("exception", e)
    target = {"128": 44, "256": 40}

    for k, v in target.items():
        item = lists[v - 1]

        if item.find_element(By.TAG_NAME, "a").get_attribute("class") == "soldout":
            print("wemap: soldout")
            continue
        else:
            send_msg(f"wemap:\niPhone {k}\n{url}")


def finder_himart(driver, urls: list[CrawlingData]):
    for data in urls:
        name, url = data.get()
        driver.get(url)

        soldout = []
        try:
            soldout = driver.find_elements(By.XPATH, '//*[@id="detailSoldOut"]')
        except:
            print("himart exception")
        if len(soldout):
            print("himart soldout")
        else:
            send_msg(f"himart\n{name}\n{url}")

        driver.implicitly_wait(1)


def finder_himart2(driver, url):
    driver.get(url)

    # try:
    #     WebDriverWait(driver, 3).until(
    #         EC.presence_of_element_located(
    #             (
    #                 By.XPATH,
    #                 # "/html/body/div[1]/div[4]/div[1]/div[2]/div[2]/ul/li[3]/div/div/div/ul/li[3]/a",
    #                 "/html/body/div[1]/div[4]/div[1]/div[2]/div[2]/ul/li[3]/div/div/div/ul/li[1]/a",
    #             )
    #         )
    #     ).click()
    # except Exception as e:
    #     print(f"himart exception: {e}")
    #     return
    driver.execute_script(
        # "javascript:hideConr('10012774', 'N','10002024@Apple 전문관:10005668@iPhone:10012774@iPhone 15 Pro')"
        "javascript:hideConr('10012796', 'N','10002024@Apple 전문관:10005668@iPhone:10012796@iPhone 15')"
    )

    driver.implicitly_wait(1)
    try:
        lists = driver.find_element(
            By.XPATH, "/html/body/div[1]/div[4]/div[1]/div[2]/div[12]/div[4]"
        ).find_elements(By.TAG_NAME, "li")
    except Exception as e:
        print(f"himart exception: {e}")
        return

    target = {"128": 7, "256": 3}
    driver.implicitly_wait(1)
    for k, v in target.items():
        item = lists[v]
        # print(item.find_element(By.TAG_NAME, "div").get_attribute("goodsnm"))

        try:
            item.find_elements(By.CLASS_NAME, "soldout")
            driver.implicitly_wait(1)
            time.sleep(1)
        except:
            atag = item.find_element(By.TAG_NAME, "a")
            send_msg(f"himart:\niPhone 256\n{atag.get_attribute('href')}")
        else:
            print("himart: soldout")


def main():
    path = "C:\\Users\\BYEONGGIL\\Desktop\\chromium\\chromedriver.exe"

    service = Service(path)
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    driver = webdriver.Chrome(service=service, options=options)

    send_msg("start")

    himart_url = [
        CrawlingData(
            "n128_seconds",
            "http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0021059320&storeTp=15",
        ),
        CrawlingData(
            "n256_seconds",
            "http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0021059324&storeTp=15",
        ),
        # CrawlingData(
        #     "test",
        #     "http://www.e-himart.co.kr/app/goods/goodsDetail?goodsNo=0021059308&storeTp=15",
        # ),
    ]
    while True:
        try:
            finder_11st(driver, "https://www.11st.co.kr/products/pa/6280549932")
            # finder_11st(driver, "https://www.11st.co.kr/products/pa/6280549956")
            finder_ssg(
                driver, "https://www.ssg.com/plan/planShop.ssg?dispCmptId=6000420848"
            )
            # finder_wemap(
            #     driver,
            #     "https://front.wemakeprice.com/deal/629557808?utm_source=linkprice&utm_medium=AF_af&utm_campaign=null",
            # )
            finder_himart(driver, himart_url)
        except Exception as e:
            # traceback.print_exc()
            pass

        print(f'timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        time.sleep(3)


if __name__ == "__main__":
    main()
