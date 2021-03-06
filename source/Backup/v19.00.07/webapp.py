# Can kiem tra ten duoc dat co sai quy tac dat ten bhay k
# đang code tới chỗ live data obdii


print('initializing ...')
'''
Cần check filter YMME lúc có giá trị KHông và N/A values
'''

from flask import Flask, redirect, url_for, request, send_file, abort
from common import htmllib
from pages.flask_dtc_convert import *
from pages.flask_obd2_simulation import *



utils = {'DTC Convert', 'Create OBDII Sim'}
tests = {'YMME', 'VIN Decode', 'Battery Procedure'}
mfrs = {'Ford':None, 'GM':None, 'Honda':None, 'Mazda':None}


app = Flask(__name__)

@app.route('/')
def show_root():
    html_mfr_menu = ''
    for mfr_name in mfrs.keys():
        html_mfr_menu += htmllib.button.format(href='/'+mfr_name, style='button_base', display=mfr_name)

    html_util_menu = ''
    for util_name in utils:
        html_util_menu += htmllib.button.format(href='/util/'+util_name, style='button_base button_util', display=util_name)

    html_menu = html_mfr_menu + '<br>'*3 + html_util_menu
    return htmllib.head.format() + html_menu




app.register_blueprint(app_dtc_convert)
app.register_blueprint(app_obd2_simulation)



import webbrowser
#url = 'http://192.168.0.132:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
#app.run(host='0.0.0.0', port=5000, debug=False) # run the server

url = 'http://localhost:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
app.run(host='localhost', port=5000, debug=True) # run the server



