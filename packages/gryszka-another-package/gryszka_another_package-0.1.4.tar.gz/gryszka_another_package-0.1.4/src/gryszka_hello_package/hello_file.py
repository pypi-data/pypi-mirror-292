import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def hello():
    print("Hello World")
    return "hello world returned"


def imported_another_hello():
    from gryszka_another_package.another_hello_file import another_hello
    return another_hello()

if __name__ == '__main__':
    imported_another_hello()