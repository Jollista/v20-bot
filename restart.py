from time import sleep
from subprocess import run
from sys import argv

sleep(10 + argv[1])
run("python main.py")