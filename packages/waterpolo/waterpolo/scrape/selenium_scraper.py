from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from waterpolo.common.logging import get_logger
from waterpolo.scrape.models import Match, TeamMatchStats


class SeleniumChampionsLeagueScraper:
    def __init__(self, base_url: str, option_ids: List[str] | None = None) -> None:
        self.base_url = base_url
        self.option_ids = option_ids or ["optionA01", "optionA02"]
        self.logger = get_logger(self.__class__.__name__)

    def _wait_for(self, driver: webdriver.Chrome, locator: tuple) -> None:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    def _wait_all(self, driver: webdriver.Chrome, locator: tuple):
        return WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

    def _text(self, element) -> str:
        return element.get_attribute("innerText").strip()

    def _parse_stats_table(self, table) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        for row in rows:
            cells = [self._text(cell) for cell in row.find_elements(By.TAG_NAME, "td")]
            if len(cells) < 2:
                continue
            label = cells[0].lower()
            value = cells[1]
            if "/" in value:
                parts = [p.strip() for p in value.split("/")]
                if "total" in label or "shoot" in label:
                    stats["ToG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["ToSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "action" in label:
                    stats["AG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["ASh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "center" in label:
                    stats["CeG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["CeSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "extra" in label:
                    stats["EXG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["EXSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "6" in label:
                    stats["6mG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["6mSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "penalty" in label:
                    stats["PG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["PSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "counter" in label:
                    stats["CoG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["CoSh"] = int(parts[1]) if parts[1].isdigit() else 0
                elif "pso" in label:
                    stats["PSOG"] = int(parts[0]) if parts[0].isdigit() else 0
                    stats["PSOSh"] = int(parts[1]) if parts[1].isdigit() else 0
            else:
                if "assist" in label:
                    stats["As"] = int(value) if value.isdigit() else 0
                elif "turnover" in label:
                    stats["To"] = int(value) if value.isdigit() else 0
                elif "steal" in label:
                    stats["St"] = int(value) if value.isdigit() else 0
                elif "block" in label:
                    stats["Bl"] = int(value) if value.isdigit() else 0
                elif "sprint" in label:
                    stats["SpW"] = int(value) if value.isdigit() else 0
                elif "exclusion drawn" in label:
                    stats["ExCe"] = int(value) if value.isdigit() else 0
                elif "exclusion foul" in label:
                    stats["ExF"] = int(value) if value.isdigit() else 0
                elif "double exclusion" in label:
                    stats["DoEx"] = int(value) if value.isdigit() else 0
                elif "penalties" in label:
                    stats["P"] = int(value) if value.isdigit() else 0
                elif "exclusion finished" in label:
                    stats["ExFin"] = int(value) if value.isdigit() else 0
                elif "4" in label and "exclusion" in label:
                    stats["Ex4min"] = int(value) if value.isdigit() else 0
        return stats

    def fetch_team_match_stats(self) -> pd.DataFrame:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless=new")
        chrome_options.add_argument("ignore-certificate-errors")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.base_url)

        rows = []
        for option_id in self.option_ids:
            self._wait_for(driver, (By.ID, "cmbCalendar"))
            driver.find_element(By.ID, option_id).click()
            matchdays = self._wait_all(driver, (By.XPATH, '//div[@id="tblBottoniDay"]/div'))
            for day_idx in range(1, len(matchdays) + 1):
                self._wait_for(driver, (By.ID, "cmbCalendar"))
                driver.find_element(By.ID, option_id).click()
                day_elem = driver.find_element(By.XPATH, f'//div[@id="tblBottoniDay"][{day_idx}]/div')
                driver.execute_script("arguments[0].click();", day_elem)

                matches = self._wait_all(
                    driver,
                    (By.XPATH, '//div[@class="d-block d-lg-none"]/div[@class="row calendar-event"]/div[@class="col-12 col-lg-2 date"]/span'),
                )
                for match in matches:
                    driver.execute_script("arguments[0].click();", match)
                    home_table = driver.find_element(By.ID, "tdStat1Final")
                    away_table = driver.find_element(By.ID, "tdStat2Final")
                    home_team = driver.find_element(By.XPATH, '//div[@id="tdStat1Final"]//strong')
                    away_team = driver.find_element(By.XPATH, '//div[@id="tdStat2Final"]//strong')

                    rows.append(
                        {
                            "Teams": self._text(home_team),
                            **self._parse_stats_table(home_table),
                        }
                    )
                    rows.append(
                        {
                            "Teams": self._text(away_team),
                            **self._parse_stats_table(away_table),
                        }
                    )

                    driver.find_element(By.XPATH, '//div[@id="tblTabsSotto"]/div/div[@class="col-6 col-sm-6 text-left"]/a').click()

        driver.quit()
        return pd.DataFrame(rows)

    def fetch_rosters(self) -> pd.DataFrame:
        self.logger.info("Roster scraping not implemented for Selenium fallback.")
        return pd.DataFrame()

    def fetch_player_match_stats(self) -> pd.DataFrame:
        self.logger.info("Player stats scraping not implemented for Selenium fallback.")
        return pd.DataFrame()

    def fetch_matches(self) -> List[Match]:
        self.logger.info("Match metadata scraping not implemented for Selenium fallback.")
        return []

    def fetch_match_stats(self, match_id: str) -> List[TeamMatchStats]:
        self.logger.info("Match-level stats scraping not implemented for Selenium fallback.")
        return []
