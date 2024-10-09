# Hybrid-Analysis 샘플 가공.

- 단계별로 데이터 가공을 나눴음.
    - 1_crawl.py
    - 2_extract_gz.py
    - 3_mal_indicate.py
    - sample/
    - json/

## 1_crawl.py

- https://hybrid-analysis.com/submissions/quick-scan/files 
- 위 사이트에서 샘플 다운로드 해옴. (일 150 ~ 200 개)
- **Cookie** 값이 주기적으로 변경 되기 때문에 파일 다운로드 받을때 requests 잡아서 cookie의 id값을 변경해줘야 함.

- 크롤링하면 sample/ 에 .gz 형태로 sample이 다운로드가 됨.
- PE 파일만 받아오도록 수정 완료.

## 2_extract_gz.py

- 위에서 받아온 샘플 .gz 파일을 압축해제와 동시에 대문자로 바꿔줌.
    - Malconv 데이터셋이 대문자를 인식하는 듯?

## 3_async.py

(requirements.txt → aiofiles, aiohttp)

- 비동기 처리해서 속도 향상함.

| **Access level** | **Limited**, standard free public API[Upgrade to premium](https://www.virustotal.com/gui/contact-us/premium-services) |
| --- | --- |
| **Usage** | **Must not be used in business workflows, commercial products or services.** |
| **Request rate** | 4 lookups / min |
| **Daily quota** | 500 lookups / day |
| **Monthly quota** | 15.5 K lookups / month |

- 여기도 대문자 이름으로 만든 샘플 때려넣음.
- 파일에는 실질적인 벤더사가 판별한 malicious, undetected가 있는 stats 객체만 json/ 경로에 파일로 저장함.


# 위 과정을 거치면 Malconv에 학습시킬 수 있는 데이터셋이 1단계 완성된다.

~머리가 나빠서 중구난방으로 개발한 점 양해바람.~~
