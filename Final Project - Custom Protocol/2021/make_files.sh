base64 /dev/urandom | head -c 1000000 |tr -d '\n' > file_1MB.txt
base64 /dev/urandom | head -c 20000000 |tr -d '\n' > file_20MB.txt
base64 /dev/urandom | head -c 100000000 |tr -d '\n' > file_100MB.txt