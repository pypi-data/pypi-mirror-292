import re
import time
from typing import Optional, List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from ._webget import get_html
from ..anime.Anime import Anime
from ..search import log

DOMAIN = "https://miobt.com/"
BASE_URL = "https://miobt.com/search.php?"


def get_magnet(script: str) -> str:
    hash_id = re.search(r"hash_id'\] = \"(.+?)\"", script)
    announce = re.search(r"announce'\] = \"(.+?)\"", script)

    if hash_id and announce:
        return f"magnet:?xt=urn:btih:{hash_id.group(1)}&tr={announce.group(1)}"
    else:
        raise ValueError("Failed to extract magnet link")


class Miobt(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    def search(self, keyword: str, collected: bool = True, proxies: Optional[dict] = None,
               system_proxy: bool = False) -> List[Anime]:
        animes: List[Anime] = []
        prev_anime_title = ""
        page = 1

        params = {'keyword': keyword}
        if collected:
            params['complete'] = 1

        while True:
            params['page'] = page
            url = BASE_URL + urlencode(params)

            try:
                html = get_html(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                bs = BeautifulSoup(html, self._parser)
                tbody = bs.find("tbody", id="data_list")

                if not tbody:
                    break

                current_titles = [tr.find_all('td')[2].a.get_text(strip=True) for tr in tbody.find_all('tr')]
                if not current_titles or current_titles[0] == prev_anime_title:
                    break

                prev_anime_title = current_titles[0]

                for tr in tbody.find_all('tr'):
                    tds = tr.find_all('td')
                    release_time = tds[0].get_text(strip=True)
                    try:
                        release_time = time.strftime(self._timefmt, time.strptime(release_time, '%Y/%m/%d'))
                    except ValueError:
                        log.error(f"Invalid time format: {release_time}")
                        continue

                    title = tds[2].a.get_text(strip=True)
                    link = DOMAIN + tds[2].a['href']
                    size = tds[3].string

                    try:
                        link_html = get_html(link, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                        link_bs = BeautifulSoup(link_html, self._parser)
                        script = link_bs.find(id='btm').find(class_='main', id='').script.find_next_siblings('script')[-1].string
                        magnet = get_magnet(script)
                    except (ValueError, AttributeError, IndexError) as e:
                        log.error(f"Failed to get magnet link for {title}: {e}")
                        continue

                    log.debug(f"Successfully got: {title}")
                    animes.append(Anime(release_time, title, size, magnet))

                page += 1

            except Exception as e:
                log.error(f"Error occurred while processing page {page}: {e}")
                break

        log.info(f"This search is complete: {keyword}")
        return animes
