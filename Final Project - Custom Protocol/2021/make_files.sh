base64 /dev/urandom | head -c 10000000 |tr -d '\n' > file_10MB.txt
base64 /dev/urandom | head -c 25000000 |tr -d '\n' > file_25MB.txt
base64 /dev/urandom | head -c 100000000 |tr -d '\n' > file_100MB.txt