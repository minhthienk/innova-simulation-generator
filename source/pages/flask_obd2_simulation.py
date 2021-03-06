import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy


from flask import Flask, request, send_file, abort, render_template
from common.mypaths import *
from common.databases import *
from common.simulation import Obd2Simulation


from flask import Blueprint
app_obd2_simulation = Blueprint("app_obd2_simulation", __name__)




@app_obd2_simulation.route('/util/Create OBDII Sim', methods=['GET', 'POST'])
def show_obd2_simulation():
    # monitor
    monitors_dtb = Obd2_Monitors(obd2_monitors_fp)
    general_monitors = monitors_dtb.get_monitors(engine_type='Both')
    gasoline_monitors = monitors_dtb.get_monitors(engine_type='Gasoline')
    diesel_monitors = monitors_dtb.get_monitors(engine_type='Diesel')

    # create j1979 live data database object and get 2 sheets of data
    obd2_ld = LiveDataOBD2(obd2_ld_fp)
    item_df = obd2_ld.sheets['Item ID']
    table_df = obd2_ld.sheets['Table ID']

    if request.method == 'GET':
        print('print tracking: GET show_obd2_simulation ')
        #return generic_ld
        return render_template('obd2.html', general_monitors=general_monitors,
                                            gasoline_monitors=gasoline_monitors,
                                            diesel_monitors=diesel_monitors,
                                            item_df=item_df,
                                            table_df=table_df
                                            )
    elif request.method =='POST':
        print('print tracking: POST show_obd2_simulation')

        # general form input data
        inputs = {}
        inputs['filename'] = request.form['filename']
        inputs['protocol'] = request.form['protocol']
        inputs['vin'] = 'F'*17 if request.form['vin']=='' else request.form['vin']
        inputs['dtcs_mode03'] = request.form['dtcs_mode03']
        inputs['dtcs_mode07'] = request.form['dtcs_mode07']
        inputs['dtcs_mode0A'] = request.form['dtcs_mode0A']
        
        # monitor form input data
        monitors = ['MIS',  'FUE',  'CCM',  'CAT',  'HCA',  'EVA',  'AIR',  'O2S',  'HTR',  'EGR_Gas',  'HCC',  'NOx',  'BPS',  'EGS',  'DPF', 'EGR_Die']
        monitor_inputs = {}
        monitor_inputs['MIL'] = request.form['MIL']
        monitor_inputs['Comp'] = request.form['Comp']
        for monitor in monitors:
            monitor_inputs[monitor] = request.form[monitor]
            monitor_inputs[monitor + '-complete'] = request.form[monitor + '-complete']

        # generic live data form input data
        ld_inputs = {}
        ld_inputs['itemid_auto_setting'] = request.form['itemid_auto_setting']

        profiles = obd2_ld.get_profiles()
        items = obd2_ld.get_items(profiles)
        for itemid in items:
            ld_inputs[itemid] = request.form[itemid]



        # create a Obd2Simulation object
        obd2 = Obd2Simulation(inputs, monitor_inputs, ld_inputs)

        # send simulation file after calculating or return result of failure
        if obd2.create_sim_file()==True:
            try:
                return send_file(str(simulation_dir_path) + '\\' + inputs['filename']+'.sim', attachment_filename=inputs['filename']+'.sim', as_attachment=True)
            except Exception as e:
                return str(e)
        else:
            return obd2_simulation_html.format(result=obd2.result.replace('\n','<br>'),
                                               general_monitors=general_monitors,
                                               gasoline_monitors=gasoline_monitors,
                                               diesel_monitors=diesel_monitors,
                                               generic_ld=generic_ld)







