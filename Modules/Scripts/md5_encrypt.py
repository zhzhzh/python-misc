import hashlib
import sys

batch_date = str(sys.argv[1])
file_nm_input = "argus_pde_data_hash_input_" + batch_date + ".txt"
file_nm_output = "argus_pde_data_hash_output_" + batch_date + ".txt"
temp_file = "argus_pde_data_hash_temp_" + batch_date + ".txt"
s = '|'
with open(temp_file, 'w') as out_file:
    with open(file_nm_input, 'r') as in_file:
        for line in in_file:
            out_file.write(line.rstrip('\n') + s + '\n')

num_lines = sum(1 for line in open(temp_file))
line_count = 1
fileHandle = open(temp_file, 'r')
filewrite = open(file_nm_output, "w+")
for line in fileHandle:
    fields = line.split('|')
    line.encode('utf-8')
    hash_token = hashlib.sha256(fields[2].upper().encode('utf-8'))
    hash_email = hashlib.md5(fields[3].upper().encode('utf-16-le'))
    hex_token = hash_token.hexdigest()
    hex_email = hash_email.hexdigest()
    filewrite.write(fields[1] + '|'
                    + hex_token.upper() + '|'
                    + hex_email.upper() + "\n")
    line_count = line_count + 1
filewrite.close()
fileHandle.close()
