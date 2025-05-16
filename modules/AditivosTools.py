from .SharedTools import *
from selenium.webdriver.common.by import By
from pathlib import Path

import subprocess
import colorama
import logging
import time
import sys
import sqlite3
import json

SILENT_MODE = '--silent' in sys.argv

class AditivosTools(object):
    def __init__(self, driver: Chrome):
        self.driver = driver
        self.window_handle = None

    def scrapeAdditives(self):
        exec_js = self.driver.execute_script
        uCE = untilConditionExecute

        logging.info('Opening base URL...')
        self.driver.get('https://www.aditivos-alimentarios.com/')
        uCE(self.driver, "return document.readyState == 'complete'")
        additives = []

        logging.info('Bypassing cookies...')
        console_log('\nBypassing cookies...', INFO, silent_mode=SILENT_MODE)
        uCE(self.driver, f"return {GET_EBCN}('fc-cta-consent')[0] !== null", max_iter=10)
        if uCE(self.driver, f"return {CLICK_WITH_BOOL}({GET_EBCN}('fc-cta-consent')[0])", max_iter=10, raise_exception_if_failed=False):
            logging.info('Cookies successfully bypassed!')
            console_log('Cookies successfully bypassed!', OK, silent_mode=SILENT_MODE)
            time.sleep(1) # Once pressed, you have to wait a little while. If code do not do this, the site does not count the acceptance of cookies
        else:
            logging.info('Cookies were not bypassed (it doesn\'t affect the algorithm, I think :D)')
            console_log("Cookies were not bypassed (it doesn't affect the algorithm, I think :D)", ERROR, silent_mode=SILENT_MODE)

        rows = exec_js(f"return {GET_EBCN}('notranslate')[0].getElementsByTagName('tr')")
        for i in range(len(rows)):
            try:
                uCE(self.driver, f"return {GET_EBCN}('notranslate')[0].getElementsByTagName('tr').length > {i}")
                row = exec_js(f"return {GET_EBCN}('notranslate')[0].getElementsByTagName('tr')[{i}]")
                code = row.find_element(By.TAG_NAME, 'h2').text.strip()
                name = row.find_element(By.TAG_NAME, 'h3').text.strip()
                toxicity = row.find_element(By.TAG_NAME, 'h4').text.strip()
                link = row.find_element(By.TAG_NAME, 'a').get_attribute('href')

                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(link)
                uCE(self.driver, "return document.readyState == 'complete'")

                description = self.extract_description_from_id('descripcion-del-aditivo') or self.extract_description_from_id('descripcion')
                uses = self.extract_description_from_id('usos-del-aditivo') or self.extract_description_from_id('usos-alimentarios')
                sideEffects = self.extract_description_from_id('efectos-secundarios') or self.extract_description_from_id('usos-alimentarios')

                # Añadir la descripción y efectos secundarios al diccionario del aditivo

                # Intentar extraer tabla química
                chem_table = exec_js("return document.getElementsByClassName('quimica').length > 0 ? document.getElementsByClassName('quimica')[0] : null")
                alt_names = {'es': [], 'en': []}

                if chem_table:
                    trs = chem_table.find_elements(By.TAG_NAME, 'tr')
                    for tr in trs:
                        tds = tr.find_elements(By.TAG_NAME, 'td')
                        if len(tds) >= 2:
                            if 'español' in tds[0].text.lower():
                                alt_names['es'] = [s.strip() for s in tds[1].text.split(',')]
                            elif 'inglés' in tds[0].text.lower():
                                alt_names['en'] = [s.strip() for s in tds[1].text.split(',')]

                else:
                    try:
                        alt_title = self.driver.find_element(By.ID, 'otros-nombres')
                        alt_p = alt_title.find_element(By.XPATH, 'following-sibling::*[1]')
                        alt_list = [s.strip().rstrip('.') for s in alt_p.text.split(',')]
                        alt_names['es'] = alt_list
                    except:
                        alt_names['es'] = []

                additives.append({
                    'code': code,
                    'name': name,
                    'description': description,
                    'uses': uses,
                    'sideEffects': sideEffects,
                    'toxicity': toxicity,
                    'alt_names': alt_names
                })

                # Log the result
                console_log(f"Scraped {i + 1} of {len(rows)}: {code} - {name} - {toxicity}", OK, silent_mode=SILENT_MODE)

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                logging.warning(f'Error scraping row {i}: {e}')
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

        return additives

    def extract_description_from_id(self, id_selector: str) -> str:
        description = []
        try:
            desc_title = self.driver.find_element(By.ID, id_selector)
            next_elem = desc_title
            while True:
                next_elem = next_elem.find_element(By.XPATH, 'following-sibling::*[1]')
                tag = next_elem.tag_name.lower()
                if tag == 'p':
                    description.append(next_elem.text.strip())
                elif tag == 'ul':
                    for li in next_elem.find_elements(By.TAG_NAME, 'li'):
                        description.append(li.text.strip())
                else:
                    break
        except Exception:
            pass
        return "\n".join(description)

    def save_to_db(self, additives, db_path='additives.db'):
        console_log(f"Saving {len(additives)} additives to database '{db_path}'...", INFO, silent_mode=SILENT_MODE)
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(errors='ignore')
        cursor = conn.cursor()

        # Create tables if not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS additives (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            uses TEXT,
            side_effects TEXT,
            toxicity TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alt_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            additive_id INTEGER NOT NULL,
            lang TEXT NOT NULL,
            alt_name TEXT NOT NULL,
            FOREIGN KEY(additive_id) REFERENCES additives(id)
            )
        ''')

        for additive in additives:
            cursor.execute('''
                INSERT INTO additives (code, name, description, uses, side_effects, toxicity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                additive['code'],
                additive['name'],
                additive['description'],
                additive['uses'],
                additive['sideEffects'],
                additive['toxicity']
            ))
            additive_id = cursor.lastrowid

            for lang in ['es', 'en']:
                for alt_name in additive['alt_names'].get(lang, []):
                    cursor.execute('''
                        INSERT INTO alt_names (additive_id, lang, alt_name)
                        VALUES (?, ?, ?)
                    ''', (additive_id, lang, alt_name))

        conn.commit()
        conn.close()
        console_log(f"Successfully saved {len(additives)} additives to database.", OK, silent_mode=SILENT_MODE)


