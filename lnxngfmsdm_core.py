#!/usr/bin/python3
# Name:        LNX NG FMS Data Manager
# Description: Navigraph FMS Data Manager alternative for Linux to manage AIRAC cycle databases
# Version:     1.0.1
# Requirement: Google Chrome Webbrowser to use the 'Download' feature via included Selenium WebDriver
# Usage:       Make the AppImage executable and run it
# -----------------------------------------------------------------------------
# Copyright (c) 2024 github.com/berndgz
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import glob
import os
import shutil
import time
import xml.dom.minidom
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By

home_directory = os.path.expanduser('~')
addons = []
conn = None


class Addon:
    download = ""
    username = ""
    password = ""

    def __init__(self, uid, name, archive, path, sim, opsys):
        self.uid = uid
        self.name = name
        self.archive = archive
        self.path = path
        self.sim = sim
        self.opsys = opsys
        self.file = "/path/to/zip/file"
        self.idx = "/path/to/index/file"
        self.cycle = "0"
        self.revision = "0"

    def to_string(self):
        return f"{self.uid}, {self.name}, {self.archive}, {self.path}, {self.sim}, {self.opsys}, {self.cycle} rev {self.revision}"

    @classmethod
    def attr_to_string(cls):
        return f"{cls.download}, {cls.username}, {cls.password}"


def connect_sqlite_db():
    global conn
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS addons (
               id INTEGER PRIMARY KEY, 
               name text NOT NULL, 
               archive text NOT NULL, 
               path text NOT NULL, 
               sim text NOT NULL, 
               opsys text NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS settings (
               id INTEGER PRIMARY KEY, 
               download text NOT NULL, 
               username text NOT NULL, 
               password text NOT NULL
        );""",
        """INSERT OR IGNORE INTO settings(id, download, username, password) 
               VALUES (1, '/home/username/Downloads', 'username', 'cGFzc3dvcmQ=');"""
    ]
    try:
        conn = sqlite3.connect(home_directory + "/.lnxngfmsdm.db")
        print(sqlite3.sqlite_version)
        cur = conn.cursor()
        for statement in sql_statements:
            cur.execute(statement)
        conn.commit()
        print(cur.lastrowid)
    except sqlite3.Error as e:
        print(e)


def get_settings():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM settings WHERE id =?", (1,))
        row = cur.fetchone()
        if row:
            print("setting =>", row)
            Addon.download = row[1]
            Addon.username = row[2]
            Addon.password = row[3]
    except sqlite3.Error as e:
        print(e)
    print("Addon attr. => " + Addon.attr_to_string())


def set_settings():
    Addon.download = "/home/username/Downloads"
    Addon.username = "username"
    Addon.password = "cGFzc3dvcmQ="
    upsert_setting(Addon.download, Addon.username, Addon.password)


def get_addons():
    global addons
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM addons")
        rows = cur.fetchall()
        addons = []
        if len(rows) > 0:
            for row in rows:
                print("addon =>", row)
                addons.append(Addon(row[0], row[1], row[2], row[3], row[4], row[5]))
    except sqlite3.Error as e:
        print(e)
    for addon in addons:
        print("Addon obj. => " + addon.to_string())


def set_addons():
    global addons
    addons.append(Addon(1, "FlightFactor A320Ultimate", "ffa320u_native_*.zip", "/home/bernd/X-Plane11/Aircraft/FlightFactor A320 ultimate", "XP11", "Linux"))
    addons.append(Addon(2, "X-Plane 11 (11.50+)", "xplane11_native_*.zip", "/home/bernd/X-Plane11/Custom Data", "XP11", "Linux"))
    addons.append(Addon(3, "X-Plane GNS430", "xplane_customdata_native_*.zip", "/home/bernd/X-Plane11/Custom Data/GNS430", "XP11", "Linux"))
    for addon in addons:
        upsert_addon(addon.uid, addon.name, addon.archive, addon.path, addon.sim, addon.opsys)


def upsert_setting(downloads, username, password):
    try:
        sql = """INSERT OR REPLACE INTO settings(id, download, username, password) VALUES (?, ?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(sql, (1, downloads, username, password))
        conn.commit()
        print(cur.lastrowid)
    except sqlite3.Error as e:
        print(e)


def upsert_addon(uid, name, archive, path, sim, opsys):
    try:
        sql = """INSERT OR REPLACE INTO addons(id, name, archive, path, sim, opsys) VALUES (?, ?, ?, ?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(sql, (uid, name, archive, path, sim, opsys))
        conn.commit()
        print(cur.lastrowid)
    except sqlite3.Error as e:
        print(e)


def create_addon(name, archive, path, sim, opsys):
    try:
        sql = """INSERT INTO addons(name, archive, path, sim, opsys) VALUES (?, ?, ?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(sql, (name, archive, path, sim, opsys))
        conn.commit()
        print(cur.lastrowid)
    except sqlite3.Error as e:
        print(e)


def delete_addon(uid):
    try:
        sql = """DELETE FROM addons WHERE id = ?"""
        cur = conn.cursor()
        cur.execute(sql, (uid,))
        conn.commit()
        print(cur.lastrowid)
    except sqlite3.Error as e:
        print(e)


def download():
    print("found", len(addons), "addons.")
    if len(addons) > 0:
        for addon in addons:
            print("- " + addon.to_string())
            # - FlightFactor A320Ultimate, ...
            # - X-Plane 11 (11.50+), ...
            # - X-Plane GNS430, ...
        # setup_method
        # prefs = {"profile.default_content_setting_values.notifications": 2}
        prefs = {
            "download.default_directory": Addon.download,
            "download.directory_upgrade": True,
            "profile.managed_default_content_settings.notifications": 2,
            "excludeSwitches": ["disable-popup-blocking"],
            "download_bubble.partial_view_enabled": False
        }
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        options.add_argument("--disable-search-engine-choice-screen")
        driver = webdriver.Chrome(options=options)
        # Step # | name | target | value
        # 1 | open | / |
        driver.get("https://navigraph.com/")
        # 2 | setWindowSize | 1600x900 |
        # driver.set_window_size(1600, 900)
        # 3 | click | linkText=Accept all cookies |
        time.sleep(3)
        # driver.find_element(By.LINK_TEXT, "Accept all cookies").click()
        driver.find_element(By.XPATH, '//*[@id="consent"]/div/div/a[2]').click()
        # 4 | pause | 3000 |
        time.sleep(3)
        # 5 | click | css=.sign-in > span |
        driver.find_element(By.CLASS_NAME, 'login').click()
        # 6 | pause | 3000 |
        time.sleep(3)
        # 7 | type | id=username | username
        driver.find_element(By.ID, "username").send_keys(Addon.username)
        # 8 | type | id=password | password
        driver.find_element(By.ID, "password").send_keys(base64.b64decode(Addon.password).decode('utf-8'))
        # 9 | click | id=login-id |
        driver.find_element(By.ID, "login-id").click()
        # 10 | pause | 5000 |
        time.sleep(5)
        # 11 | click | linkText=Downloads |
        driver.find_element(By.LINK_TEXT, "Downloads").click()
        # 12 | pause | 3000 |
        time.sleep(3)

        for addon in addons:
            # 13 | click | xpath=//*[contains(text(),'X-Plane 11 (11.50+)')]/../td[4]/*[contains(text(),'Linux')] |
            driver.find_element(By.XPATH, "//*[contains(text(),\'" + addon.name + "\')]/../td[4]/*[contains(text(),\'" + addon.opsys + "\')]").click()
            # 14 | pause | 10000 |
            time.sleep(10)

        # 19 | click | css=.sign-in |
        driver.find_element(By.XPATH, '//button[text()="Get Started"]').click()
        # 20 | pause | 3000 |
        time.sleep(3)
        # 21 | click | css=.logout:nth-child(1) |
        driver.find_element(By.LINK_TEXT, 'Sign out').click()
        # 22 | pause | 3000 |
        time.sleep(5)
        # 23 | close |  |
        driver.close()
        # teardown_method
        driver.quit()


def get_archive(addon):
    files = glob.glob(Addon.download + "/" + addon.archive)
    if len(files) == 1:
        addon.file = files[0]
        print("found '" + addon.file + "' addon archive.")
        # found '/home/bernd/Downloads/ffa320u_native_2404.zip' addon archive.
        # found '/home/bernd/Downloads/xplane11_native_2404.zip' addon archive.
        # found '/home/bernd/Downloads/xplane_customdata_native_2404.zip' addon archive.
        return 0
    else:
        addon.file = "/path/to/zip/file"
        return 1


def get_index(addon):
    files = glob.glob(addon.path + "/*.index")
    if len(files) == 1:
        addon.idx = files[0]
        print("found '" + addon.idx + "' addon index.")
        # found '/home/bernd/X-Plane11/Aircraft/FlightFactor A320 ultimate/65cf4439-6c3c-425b-8640-4d77bc17d7aa.index' addon index.
        # found '/home/bernd/X-Plane11/Custom Data/4230ddbd-2639-4c16-a7e3-f3d3f4421dc3.index' addon index.
        # found '/home/bernd/X-Plane11/Custom Data/GNS430/2edd1319-de94-491d-91c5-80b4afd2db6a.index' addon index.
    else:
        addon.idx = "/path/to/index/file"


def get_cycle(addon):
    if addon.idx != "/path/to/index/file":
        doc = xml.dom.minidom.parse(addon.idx)
        root = doc.documentElement
        if root.tagName == "addon":
            addon.cycle = root.getAttribute("cycle")
            addon.revision = root.getAttribute("revision")
        print("- " + addon.to_string())
        # - FlightFactor A320Ultimate, ...
        # - X-Plane 11 (11.50+), ...
        # - X-Plane GNS430, ...


def del_index(addon):
    if addon.idx != "/path/to/index/file" and addon.file != "/path/to/zip/file":
        path = str(addon.idx[:addon.idx.rindex("/")])
        print("path => " + path)
        mapping = {}
        doc = xml.dom.minidom.parse(addon.idx)
        for node1 in doc.getElementsByTagName("mapping"):
            if node1.getAttribute("simulator") == addon.sim:
                mapping = node1
                break
        for node2 in mapping.getElementsByTagName("files"):
            file = path + get_directory(node2) + node2.getAttribute("destination")
            print("delete file '" + file + "' ...")
            os.remove(file)
        os.remove(addon.idx)


def get_directory(node):
    directory = "/"
    while node.nodeName != "mapping":
        node = node.parentNode
        if node.nodeName == "directory":
            directory = "/" + node.getAttribute("name") + directory
    return directory


def install_addon(addon):
    if addon.file != "/path/to/zip/file":
        print("install addon archive '" + addon.file + "' to path '" + addon.path + "' ...")
        shutil.unpack_archive(addon.file, addon.path)


def backup_addon(addon):
    if addon.file != "/path/to/zip/file":
        print("backup addon archive '" + addon.file + "' ...")
        os.rename(addon.file, addon.file + ".bak")


def update(addon):
    result = get_archive(addon)
    get_index(addon)
    del_index(addon)
    install_addon(addon)
    backup_addon(addon)
    return result


def init():
    # set_settings()
    get_settings()
    # set_addons()
    get_addons()
    # get indexes and cycles
    for addon in addons:
        get_index(addon)
        get_cycle(addon)


def main():
    download()
    for addon in addons:
        result = update(addon)
        print(result)


connect_sqlite_db()
init()
# main()
