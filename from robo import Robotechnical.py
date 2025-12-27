# main.py
from Robotech import robotech
import numpy as np
import requests

@robotech.develop.optimize
def fast_sum(arr):
    return np.sum(arr)

@robotech.develop.optimize
def get_google_status():
    r = requests.get("https://www.google.com")
    return r.status_code

fast_sum(np.arange(100000))
get_google_status()

robotech.mechanics.try_execute("print(10/0)")
