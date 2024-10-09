## 1_malicious_clssification.py

- malicious, undetected를 기준으로 해당 샘플의 malicious 여부를 결정할 예정.
    - malicious >= 2
- 판단이 완료되면 {sample_name} {malicious_indicate} 형식으로 .txt 저장.

- 모든 sample_name이 저장된 train.txt와 json/ 이 필요함.
- **output : train_result.txt**


## 2_final.py

- 위 저장된 .txt 파일을 .csv로 변환.
- 해당 csv 파일이 최종 학습에 들어갈 파일임.
- **output : train.csv**

