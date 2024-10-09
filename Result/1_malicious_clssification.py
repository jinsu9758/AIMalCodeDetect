import json

with open('./train.txt', 'r') as file0:
    content = file0.readlines()

file1 = open('./train_result.txt', 'w')

for filename in content:
    filepath = 'json/' + filename[:-1].upper() + '.json'
    
    with open(filepath, 'r') as file2:
        data = json.load(file2)

    malicious = data['malicious']
    undetected = data['undetected']

    if malicious >= 2:
        dataset = filename[:-1].upper() + ' 1\n'
        file1.write(dataset)
    else:
        dataset = filename[:-1].upper() + ' 0\n'
        file1.write(dataset)
    file2.close()

file0.close()
file1.close()
