import subprocess
import threading


def main():
    command_twitter = ["python", "twitter.py"]
    subprocess.call(command_twitter)


def other():
    command_analysis = ["python", "analysis.py"]
    subprocess.call(command_analysis)


if __name__ == "__main__":
    thread_obj = threading.Thread(target=other)
    thread_obj.start()
    main()
