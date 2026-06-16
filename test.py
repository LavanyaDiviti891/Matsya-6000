import urllib.request
import time
for i in range(10):
    try:
        urllib.request.urlopen("http://127.0.0.1:5001")
        print("Server is up!")
        break
    except Exception as e:
        time.sleep(1)
