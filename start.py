import subprocess
import threading
import time


def main():
    command_twitter = ["python", "twitter.py"]
    subprocess.call(command_twitter)


def sub():
    command_analysis = ["python", "analysis.py"]
    subprocess.call(command_analysis)


if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    main_thread.start()

    interval = 60 * 240
    time.sleep(interval)
    wait = True
    base_time = time.time()
    next_time = 0
    while True:
        sub_thread = threading.Thread(target=sub)
        sub_thread.start()
        if wait:
            sub_thread.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)
