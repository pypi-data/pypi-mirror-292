import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def another_hello():
    print("another Hello World")
    return "another hello World returned"

def imported_hello():
    from gryszka_hello_package.hello_file import hello
    return hello()

if __name__ == '__main__':
    imported_hello()
