from celery import Celery
import time

app = Celery('tasks', broker='redis://127.0.0.1:6379/0')

@app.task
def add(x, y):
    return x + y

@app.task
def CheckFun():
    print("Sleeping")
    time.sleep(2)
    print("Awaked")

