print('Initializing ...')

from flask import Flask, redirect, url_for, request, send_file
from simulation_generate import create_obd2
from dtc_converter import *
from html_source import *
from sys import exit
from flask import render_template
from cls_databases import *



utils = {'dtc-convert':'DTC Convert', 'create-obdii-sim':'Create OBDII Sim'}
mfrs = {'ford':'Ford', 'gm':'GM', 'mazda':'Mazda', 'honda':'Honda'}
tests = {'ymme':'YMME', 'vin':'VIN Decode', 'battery-procedure':'Battery Procedure'}


mfr_dtb = {}
for mfr in  mfrs.keys():
    mfr_dtb[mfr] = VehicleManufacturer(mfr)
    break


app = Flask(__name__)


@app.route('/')
def show_root_page():
    html_mfr_menu = ''
    for mfr, disp in  mfrs.items():
        html_mfr_menu += button.format(href='/'+mfr, style='button_base', display=disp)

    html_util_menu = ''
    for util, disp in  utils.items():
        html_util_menu += button.format(href='/util/'+util, style='button_base button_util', display=disp)

    html_menu = html_mfr_menu + '<br>'*3 + html_util_menu
    return head + html_menu



@app.route('/<mfr>')
def show_mfr_page(mfr):
    if mfr in mfrs.keys():
        html_menu = button.format(href='/..', style='button_base', display='Back')
        for test, disp in tests.items():
            html_menu += button.format(href='/{}/{}'.format(mfr,test), style='button_base', display=mfrs[mfr]+' '+disp)
        return head + html_menu



@app.route('/<mfr>/ymme')
def show_ymme_page(mfr):
    html_menu =  (
        button.format(href='/..', style='button_base button_control', display='Back') +
        button_prefresh.format('Get Ramdon YMME') + '<br>'*2)
    html_content = mfr_dtb[mfr].ymme.get_html(market='US')
    return head + html_menu + html_content




@app.route('/<mfr>/battery-procedure', methods=['GET', 'POST'])
def show_battery_procedure_page(mfr):
    menu = (
        button.format(href='/..', style='button_base button_control', display='Back') +
        submit_button.format(style='button_base', val='Get Ramdom YMME') +
        '&nbsp;'*20 +
        submit_button.format(style='button_base button_lang',val='English') +
        submit_button.format(style='button_base button_lang',val='Spanish') +
        submit_button.format(style='button_base button_lang',val='French') +
        '<br>'*2)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Get Ramdom YMME':
            content = battery_procedure[mfr].get_html('US', None, True)
        else:
            lang_selected = request.form['submit_button']
            content = battery_procedure[mfr].get_html('US', lang_selected, False)
        
    elif request.method == 'GET':
        content = battery_procedure[mfr].get_html('US', 'English', True)

    return head + menu + content









@app.route('/<mfr>/vin', methods=['GET', 'POST'])
def show_vin_page(mfr):
    menu =  (
        button.format(href='/..', style='button_base', display='Back') +
        button_prefresh.format('Get Ramdon YMME') + '<br>'*2)
    if request.method == 'POST':
        # assign vin database display to a df
        df = vin[mfr].database_display['main']
        # iterate the index index
        for index in df.index.to_list():
            if request.form['submit_button'] == df.loc[index,'VIN']:
                # file name of simulation file
                year = str(df.loc[index,'Year'])
                mfr = str(df.loc[index,'mfr'])
                model = str(df.loc[index,'Model'])
                engine = str(df.loc[index,'Engine'])
                vinfull = str(df.loc[index,'VIN'])
                filename =  year + ' ' + mfr + ' ' + model + ' ' + engine + ' (' + vinfull + ')' + '.sim'
                if create_obd2(filename, vinfull)==True:
                    try:
                        return send_file(str(simulation_dir_path) + '\\' + filename, attachment_filename=filename, as_attachment=True)
                    except Exception as e:
                        return str(e)

    elif request.method == 'GET':
        content = vin[mfr].get_html(market='US')
    return head + menu + content














@app.route('/util/create-obdii-sim', methods=['GET', 'POST'])
def show_create_obdii_sim_page():
    menu = button.format(href='/..', style='button_base button_control', display='Back') + '<br>'*2
    if request.method == 'POST':
        if request.form['submit_button'] == 'Get VIN Decode Sim':
            vin = request.form['vin-input']

            filename = vin + '.sim'
            if create_obd2(filename, vin)==True:
                try:
                    return send_file(str(simulation_dir_path) + '\\' + filename, attachment_filename=filename, as_attachment=True)
                except Exception as e:
                    return str(e)

            content = input_form.format(placeholder='Enter VIN', name='vin-input', btn_val='Get VIN Decode Sim', input_val='')

    elif request.method == 'GET':
        content = input_form.format(placeholder='Enter VIN', name='vin-input', btn_val='Get VIN Decode Sim', input_val='')

    return head + menu + content    




@app.route('/util/dtc-convert', methods=['GET', 'POST'])
def show_dtc_hex_page():
    menu = button.format(href='/..', style='button_base button_control', display='Back') + '<br>'*2
    if request.method == 'POST':
        if request.form['submit_button'] == 'Convert To Hex':
            dtc = request.form['dtc-input']
            content = (
                input_form.format(placeholder='Enter DTC', name='dtc-input', btn_val='Convert To Hex', input_val=dtc) + '<br>'*2 +
                input_form.format(placeholder='Enter Hex Number', name='hex-input', btn_val='Convert To DTC', input_val=dtc2hex(dtc)))

        if request.form['submit_button'] == 'Convert To DTC':
            hexnum = request.form['hex-input']
            content = (
                input_form.format(placeholder='Enter DTC', name='dtc-input', btn_val='Convert To Hex', input_val=hex2dtc(hexnum)) + '<br>'*2 +
                input_form.format(placeholder='Enter Hex Number', name='hex-input', btn_val='Convert To DTC', input_val=hexnum))

    elif request.method == 'GET':
        content = (
            input_form.format(placeholder='Enter DTC', name='dtc-input', btn_val='Convert To Hex', input_val='') + '<br>'*2 +
            input_form.format(placeholder='Enter Hex Number', name='hex-input', btn_val='Convert To DTC', input_val=''))

    return head + menu + content












import webbrowser
#url = 'http://192.168.0.149:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
#app.run(host='0.0.0.0', port=5010, debug=False) # run the server

url = 'http://localhost:5000/'
webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
app.run(host='localhost', port=5000, debug=False) # run the server



