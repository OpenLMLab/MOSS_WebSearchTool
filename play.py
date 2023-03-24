import time

start_time = time.time()

while True:
    if (time.time() - start_time) % 5 == 0:
        print(1)


