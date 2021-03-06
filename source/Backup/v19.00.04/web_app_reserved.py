print('Initializing ...')


'''
Cần check filter YMME lúc có giá trị KHông và N/A values
'''




from flask import Flask, redirect, url_for, request, send_file, abort
from simulation_generate import Obd2Simulation
from dtc_converter import *
from html_templates import *
from sys import exit
from flask import render_template
from cls_databases import *



utils = {'DTC Convert', 'Create OBDII Sim'}
tests = {'YMME', 'VIN Decode', 'Battery Procedure'}
mfrs = {'Ford':None, 'GM':None, 'Honda':None, 'Mazda':None}



for mfr_name in  mfrs.keys():
    mfrs[mfr_name] = Manufacturer(mfr_name).filter_market('VN').filter_existent_ymme()
    break



app = Flask(__name__)


@app.route('/')
def show_root_page():
    html_mfr_menu = ''
    for mfr_name in mfrs.keys():
        html_mfr_menu += button.format(href='/'+mfr_name, style='button_base', display=mfr_name)

    html_util_menu = ''
    for util_name in utils:
        html_util_menu += button.format(href='/util/'+util_name, style='button_base button_util', display=util_name)

    html_menu = html_mfr_menu + '<br>'*3 + html_util_menu
    return head + html_menu




@app.route('/<mfr_name>')
def show_mfr_page(mfr_name):
    if mfr_name not in mfrs.keys(): abort(404)

    html_menu = button.format(href='/..', style='button_base button_control', display='Back')
    for test_name in tests:
        html_menu += button.format(href='/{}/{}'.format(mfr_name,test_name), style='button_base', display=mfr_name+' '+test_name)
    return head + html_menu



@app.route('/<mfr_name>/YMME')
def show_ymme_page(mfr_name):
    if mfr_name not in mfrs.keys(): abort(404)

    html_menu = (
        button.format(href='/..', style='button_base button_control', display='Back') +
        button_prefresh.format('Get Ramdon YMME') + '<br>'*2)

    html_content = mfrs[mfr_name].dtbs['YMME'].get_html()
    return head + html_menu + html_content



@app.route('/<mfr_name>/Battery Procedure', methods=['GET', 'POST'])
def show_battery_procedure_page(mfr_name):
    if mfr_name not in mfrs.keys(): abort(404)

    html_menu = (
        button.format(href='/..', style='button_base button_control', display='Back') +
        submit_button.format(style='button_base', val='Get Ramdom YMME'))
    html_content = mfrs[mfr_name].dtbs['Battery Procedure'].get_html()
    return head + html_menu + '<br>'*2 +html_content



@app.route('/<mfr_name>/VIN Decode', methods=['GET', 'POST'])
def show_vin_page(mfr_name):
    if mfr_name not in mfrs.keys(): abort(404)

    html_menu =  (
        button.format(href='/..', style='button_base button_control', display='Back') +
        button_prefresh.format('Get Ramdon YMME') + '<br>'*2)
    if request.method == 'POST':
        # assign vin database display to a df
        df = mfrs[mfr_name].dtbs['VIN Decode'].sheets['Display']
        # iterate the index index
        for index in df.index.to_list():
            if request.form['submit_button'] == df.loc[index,'VIN']:
                # file name of simulation file
                year = str(df.loc[index,'Year'])
                make = str(df.loc[index,'Make'])
                model = str(df.loc[index,'Model'])
                engine = str(df.loc[index,'Engine'])
                vinfull = str(df.loc[index,'VIN'])
                filename =  year + ' ' + make + ' ' + model + ' ' + engine + ' (' + vinfull + ')' + '.sim'
                if create_obd2(filename, vinfull)==True:
                    try:
                        return send_file(str(simulation_dir_path) + '\\' + filename, attachment_filename=filename, as_attachment=True)
                    except Exception as e:
                        return str(e)

    elif request.method == 'GET':
        html_content = mfrs[mfr_name].dtbs['VIN Decode'].get_html()
    return head + html_menu + html_content









#=========================================================================
#=========================================================================
#=========================================================================
#=========================================================================
#=========================================================================A
@app.route('/util/Create OBDII Sim', methods=['GET', 'POST'])
def show_create_obdii_sim_page():
    if request.method == 'GET':
        return head + create_obdii_sim_page.format(result='')
    elif request.method =='POST':
        dict = {}
        dict['filename'] = request.form['filename']
        dict['protocol'] = request.form['protocol']
        dict['vin'] = 'F'*17 if request.form['vin-input']=='' else request.form['vin-input']
        dict['dtcs_mode03'] = request.form['dtc03s-input']
        dict['dtcs_mode07'] = request.form['dtc07s-input']
        dict['dtcs_mode0A'] = request.form['dtc0As-input']

        obd2 = Obd2Simulation(**dict)
        if obd2.result=='':
            return obd2.create_mode9()
        else:
            return head + create_obdii_sim_page.format(result=obd2.result)
        







@app.route('/util/Create OBDII Sim2', methods=['GET', 'POST'])
def show_create_obdii_sim_page2():
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




@app.route('/util/DTC Convert', methods=['GET', 'POST'])
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
#url = 'http://192.168.1.80:5000/'
#webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
#app.run(host='0.0.0.0', port=5000, debug=False) # run the server

url = 'http://localhost:5000/'
webbrowser.open(url,new=2) # new = 2 => open in a new tab, if possible
app.run(host='localhost', port=5000, debug=False) # run the server



