import os

def hello():
    current_user = os.getlogin()
    print(f"Hello, {current_user}!, this is a pakage from Operations TCBS")