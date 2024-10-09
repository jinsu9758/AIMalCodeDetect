import os
import requests
import time
import random
from bs4 import BeautifulSoup

def random_seed():
    now = time.localtime()
    tmp1 = float(time.strftime('%S', now))
    tmp2 = float(time.strftime('%M', now))
    sec = tmp1 * tmp2
    sec -= sec
    sec = sec * 100 // 10
    random.seed(sec)


def login(session, username, password):
    login_url = 'https://www.hybrid-analysis.com/login'
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    token_input = soup.find('input', {'name': 'login[_token]'})
    login_token = token_input['value'] if token_input else ''

    login_data = {
        'login[username]': username,
        'login[password]': password,
        'login[remember_me]': '1',
        'login[_token]': login_token
    }

    login_response = session.post(login_url, data=login_data)
    return login_response.status_code == 200

def extract_hash_data(session, headers, num_pages):
    base_url = 'https://www.hybrid-analysis.com/submissions/quick-scan/files?page={}'
    all_hash_data = []

    for page in range(1, num_pages + 1):
        url = base_url.format(page)
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr')

            for row in rows:
                submission_name_span = row.find('span', id='submission-name')
                submission_name = submission_name_span.text.strip() if submission_name_span else 'Unknown'

                hash_span = row.find('span', class_='lowprio compact')
                if hash_span:
                    hash_value = hash_span.text.strip()

                    
                    pe_type_span = row.find('span', class_='compact') 
                    is_pe = 'PE' in pe_type_span.text if pe_type_span else False

                    timestamp_td = row.find('td', class_='submission-timestamp hidden-xs')
                    timestamp = timestamp_td.text.strip() if timestamp_td else 'Unknown'

                    if is_pe: 
                        all_hash_data.append((submission_name, hash_value, timestamp))

        else:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")

    return all_hash_data

def download_samples(session, hash_data, log_filename, train_filename):
    os.makedirs('sample', exist_ok=True)
    download_url = 'https://www.hybrid-analysis.com/download-sample/{}'
    
    download_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'id=CHANGE_COOKIE_VALUE;'  
    }

    for submission_name, hash_value, timestamp in hash_data:
        random_seed()

        file_download_url = download_url.format(hash_value)
        download_response = session.get(file_download_url, headers=download_headers)

        if download_response.status_code == 200:
            file_path = os.path.join('sample', f'{hash_value}.gz')
            with open(file_path, 'wb') as file2:
                file2.write(download_response.content)
            file2.close()

            with open(log_filename, 'a') as file0:
                file0.write(f'{timestamp},{submission_name},{hash_value}\n')
            file0.close()
            with open(train_filename, 'a') as file1:
                file1.write(f'{hash_value}\n')
            file1.close()
            print(f'{file_path} 다운로드 완료')
        else:
            print(f"{hash_value} 샘플 다운로드 실패. 상태 코드: {download_response.status_code}")
            return
        time.sleep(random.uniform(1.5, 3.5))

def main():
    session = requests.Session()
    username = 'USER_NAME'
    password = 'PASSWORD'

    if login(session, username, password):
        print("로그인 성공")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        num_pages = 10
        hash_data = extract_hash_data(session, headers, num_pages)

        if hash_data:
            download_samples(session, hash_data, 'log/000_extracted_hash_time_log.txt', 'train_bak.txt')
    else:
        print("로그인 실패")

if __name__ == '__main__':
    main()

