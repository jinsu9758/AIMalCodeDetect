import gzip
import shutil
import os

def decompress_gz(input_file, output_file):
    with gzip.open(input_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

binary_path = 'sample/'
binary_name = os.listdir(binary_path)

for filename in binary_name:
    if '.gz' in filename:
        input_gz_file = f'{binary_path}{filename}'
        filename = filename.split('.')
        filename = filename[0].upper()
        output_file = f'{binary_path}{filename}'

        decompress_gz(input_gz_file, output_file)
        os.remove(input_gz_file)


file = open('./train.txt', 'w')

for i in binary_name:
    i = i.split('.')
    file.write(i[0].lower() + '\n')
