import os
from time import sleep
import pandas as pd
from typing import Optional
import requests
from bs4 import BeautifulSoup


# check
def checkHasHref(a_tag: BeautifulSoup) -> bool:
    return a_tag and a_tag.has_attr("href")


def checkLink(link: str) -> bool:
    try:
        response: requests.Response = requests.get(link, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


# create
def createFolder(folder_name: str) -> None:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# get
def getEnv(key: str) -> Optional[str]:
    value: Optional[str] = os.getenv(key)
    if value is None:
        raise Exception(f"{key} 環境變數不存在")
    return value


# download


def downloadFile(a_tag_href: str, local_filename: str) -> Optional[str]:
    sleep(3)
    createFolder("download_files")
    print(f"下載中: {local_filename}")

    with requests.get(a_tag_href, stream=True) as r:
        r.raise_for_status()
        try:
            with open(os.path.join("download_files", local_filename), "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            print(f"下載失敗: {e} by {local_filename}")
    return local_filename


def downloadByExcel(
    json_data: dict, local_filename: str = "output.xlsx"
) -> Optional[pd.DataFrame]:
    try:
        df: pd.DataFrame = pd.DataFrame(json_data)
        df.to_excel(local_filename, index=False)
        return df
    except Exception as e:
        print(f"下載失敗: {e}")
        return None
