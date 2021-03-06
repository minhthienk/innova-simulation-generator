import sys
import traceback


myerror = None
def set_error(err):
    global myerror
    myerror = err

def get_error(err):
    global myerror
    return myerror

class MyException(Exception):
    '''
    This exeption is used when items transfered to 
    '''
    def __init__(self, msg):
        super().__init__(msg) 



def print_traceback():
    try:
        raise MyException(None)
    except MyException as e:
        traceback.print_exc()

def get_traceback():
    try:
        raise MyException(None)
    except MyException as e:
        return traceback.print_tb(sys.exc_info()[2], limit=None, file=None)


