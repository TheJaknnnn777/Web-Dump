import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.3 Safari/602.3.12"
]

TELEGRAM_TOKEN = "8173488085:AAHeEmVQNc1E5fVA4fptgvtrBEMBXBVcGmY"
CHAT_ID = "7321328717"

def send_telegram_document(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(file_path, 'rb') as file:
        response = requests.post(url, data={"chat_id": CHAT_ID}, files={"document": file})
    if response.status_code == 200:
        print("File berhasil dikirim ke Telegram.")
    else:
        print(f"Gagal mengirim file ke Telegram. Status code: {response.status_code}, response: {response.text}")

def google_search_dork(query, num_pages=15):
    results = []
    
    for page in range(num_pages):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        start = page * 10
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&start={start}"

        try:
            response = requests.get(search_url, headers=headers, timeout=30, verify=False)
            if response.status_code == 429:
                print(f"Too Many Requests. Waiting before retrying...")
                time.sleep(random.uniform(60, 120))  # Longer, random delay
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch Google results on page {page + 1}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            page_results = []
            for link in soup.select('a[href^=\"http\"]'):
                url = link.get('href')
                if 'google.com' not in url and url.startswith("http"):
                    clean_url = url.split("&")[0]
                    page_results.append(clean_url)
                    results.append(clean_url)

            print(f"Fetched {len(page_results)} results from page {page + 1}.")
        except Exception as e:
            print(f"Error on page {page + 1}: {e}")

        # Add longer, random delay to avoid bot detection
        time.sleep(random.uniform(60, 120))

    return results

def save_results_to_file(dork, results):
    safe_dork_name = urllib.parse.quote_plus(dork)
    file_name = f"{safe_dork_name}.txt"
    with open(file_name, 'w') as f:
        for result in results:
            f.write(result + "\n")
    return file_name

def remove_line_from_file(file_name, line_to_remove):
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != line_to_remove:
                f.write(line)

if __name__ == "__main__":
    with open('dork.txt', 'r') as file:
        dorks = file.readlines()
    
    for dork_query in dorks:
        dork_query = dork_query.strip()
        if not dork_query:
            continue
        
        print(f"Mencari website menggunakan Google dork: {dork_query}...")
        search_results = google_search_dork(dork_query, num_pages=15)

        print(f"Total hasil yang diambil untuk dork '{dork_query}': {len(search_results)}.")

        # Save results to file
        file_name = save_results_to_file(dork_query, search_results)

        # Send file to Telegram
        send_telegram_document(file_name)

        # Remove line that has been processed from dork.txt
        remove_line_from_file('dork.txt', dork_query)

        # Longer delay before processing the next dork
        time.sleep(random.uniform(60, 120))
