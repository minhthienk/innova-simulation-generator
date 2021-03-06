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



app = Flask(__name__)

@app.route('/')
def show_root():
     return render_template('home.html')



app.register_blueprint(app_dtc_convert)
app.register_blueprint(app_obd2_simulation)



import webbrowser
#url = 'http://192.168.0.132:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
#app.run(host='0.0.0.0', port=5000, debug=False) # run the server

#url = 'http://localhost:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
app.run(host='localhost', port=5000, debug=True) # run the server




