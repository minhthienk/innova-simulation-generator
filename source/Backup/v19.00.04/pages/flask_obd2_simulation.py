from flask import Flask, request, send_file, abort

from common import htmllib
from common.databases import *
from common.simulation import Obd2Simulation


from flask import Blueprint
app_obd2_simulation = Blueprint("app_obd2_simulation", __name__)


def add_monitors_html():
    # general monitors
    monitors = [['MIS','Misfire monitoring'],
                ['FUE','Fuel monitoring'],
                ['CCM','Comprehensive component monitoring']]
    general_monitors = ''
    for monitor in monitors:
        general_monitors += monitor_html.format(monitor=monitor[0], name=monitor[1]) + '\n'
    # gasoline
    monitors = [['CAT','Catalyst monitoring'], 
                ['HCA','Heated catalyst monitoring'],
                ['EVA','Evaporative system monitoring'],
                ['AIR','Secondary air system monitoring'],
                ['O2S','Oxygen sensor monitoring'],
                ['HTR','Oxygen sensor heater monitoring'],
                ['EGR_Gas','EGR and/or VVT system monitoring']]
    gasoline_monitors = ''
    for monitor in monitors:
        gasoline_monitors += monitor_html.format(monitor=monitor[0], name=monitor[1]) + '\n'
    # diesel
    monitors = [['HCC','NMHC catalyst monitoring'], 
                ['NOx','NOx/SCR aftertreatment monitoring'],
                ['BPS','Boost pressure system monitoring'],
                ['EGS','Exhaust gas sensor monitoring'],
                ['DPF','PM filter monitoring'],
                ['EGR_Die','EGR and/or VVT system monitoring']]
    diesel_monitors = ''
    for monitor in monitors:
        diesel_monitors += monitor_html.format(monitor=monitor[0], name=monitor[1]) + '\n'
    # return all monitors
    return general_monitors,gasoline_monitors,diesel_monitors



@app_obd2_simulation.route('/util/Create OBDII Sim', methods=['GET', 'POST'])
def show_obd2_simulation():
    general_monitors,gasoline_monitors,diesel_monitors = add_monitors_html()

    if request.method == 'GET':
        print('print tracking: GET show_obd2_simulation ')
        return obd2_simulation_html.format(result='',
                                           general_monitors=general_monitors,
                                           gasoline_monitors=gasoline_monitors,
                                           diesel_monitors=diesel_monitors)
    elif request.method =='POST':
        print('print tracking: POST show_obd2_simulation')
        inputs = {}
        inputs['filename'] = request.form['filename']
        inputs['protocol'] = request.form['protocol']
        inputs['vin'] = 'F'*17 if request.form['vin']=='' else request.form['vin']
        inputs['dtcs_mode03'] = request.form['dtcs_mode03']
        inputs['dtcs_mode07'] = request.form['dtcs_mode07']
        inputs['dtcs_mode0A'] = request.form['dtcs_mode0A']
        
        monitors = ['MIS',  'FUE',  'CCM',  'CAT',  'HCA',  'EVA',  'AIR',  'O2S',  'HTR',  'EGR_Gas',  'HCC',  'NOx',  'BPS',  'EGS',  'DPF', 'EGR_Die']

        monitor_inputs = {}
        monitor_inputs['MIL'] = request.form['MIL']
        monitor_inputs['Comp'] = request.form['Comp']
        for monitor in monitors:
            monitor_inputs[monitor] = request.form[monitor]
            monitor_inputs[monitor + '-complete'] = request.form[monitor + '-complete']

        obd2 = Obd2Simulation(inputs, monitor_inputs)

        if obd2.create_sim_file()==True:
            try:
                return send_file(str(simulation_dir_path) + '\\' + inputs['filename']+'.sim', attachment_filename=inputs['filename']+'.sim', as_attachment=True)
            except Exception as e:
                return str(e)
        else:
            return obd2_simulation_html.format(result=obd2.result.replace('\n','<br>'),
                                               general_monitors=general_monitors,
                                               gasoline_monitors=gasoline_monitors,
                                               diesel_monitors=diesel_monitors)



obd2_simulation_html = htmllib.head + '''
<body>
  <a href="/..">
    <button class="button_base button_control">Back</button>
  </a>

  <br>
  <br>
  <p style="color:Red;">{result}</p>

  <form action="" method="post">
    <b style="font-size:20px;">File Name:</b><br>
    <input type="text" class="inputtext" placeholder="Input filename" name="filename" value=""><br><br><br>

    <b style="font-size:20px;">Protocol Selection</b><br><br>
    <input type="radio" style="margin-left: 30px;" name="protocol" value="CAN" checked> Protocol CAN  
    <input type="radio" style="margin-left: 30px;" name="protocol" value="PWM"> Protocol PWM
    <input type="radio" style="margin-left: 30px;" name="protocol" value="ISO9141"> Protocol ISO9141
    <input type="radio" style="margin-left: 30px;" name="protocol" value="KW2000"> Protocol KW2000
    <br><br><br>

    <b style="font-size:20px;">Mode $09</b><br>
    <input type="text" class="inputtext" placeholder="Input VIN (Default: FFFFFFFFFFFFFFFF)" name="vin" value=""><br><br><br>

    <b style="font-size:20px;">Mode $03</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $03 DTCs (Example: P0001, P1001, P2001, P3001)" name="dtcs_mode03" value=""><br><br><br>

    <b style="font-size:20px;">Mode $07</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $0A DTCs (Example: P0001, P1001, P2001, P3001)" name="dtcs_mode07" value=""><br><br><br>

    <b style="font-size:20px;">Mode $0A</b><br>
    <input type="text" class="inputtext" placeholder="Input mode $0A DTCs (Example: P0001, P1001, P2001, P3001)" name="dtcs_mode0A" value=""><br><br><br>
    
    <!-- Mode 1 -->
    <b style="font-size:20px;">Mode $01</b><br><br>
    <!-- Radio box to select Gasoline or Diesel -->
    Engine type selection: 
    <input type="radio" style="margin-left: 30px;" name="Comp" value="not support" onClick="showGas()" checked> Gasoline
    <input type="radio" style="margin-left: 30px;" name="Comp" value="support" onClick="showDiesel()"> Diesel
    <br><br>

    <!-- General monitors -->
    <div id="general-monitors">
      General monitors for both gasoline engine and diesel engine:<br>
      
      <input type="checkbox" style="margin-left: 30px;" name="MIL" value="on"> MIL On/Off<br>
      <input type="hidden" value="off" name="MIL">
      {general_monitors}
    </div><br>

    <!-- Gasoline monitors -->
    <div id="gasoline-monitors">
      Monitors specified for gasoline engine only:<br>
      {gasoline_monitors}
    </div>

    <!-- Diesel monitors -->
    <div id="diesel-monitors" style="display:None">
      Monitors specified for gasoline engine only:<br>
      {diesel_monitors}
    </div><br>
    <input type="submit" class="button_base button_input_submit"  name="submit_button" value="Submit">
  </form>


  <script language="Javascript">
    function showGas(){{
        document.getElementById("gasoline-monitors").style.display="Block";
        document.getElementById("diesel-monitors").style.display="None";
    }}

    function showDiesel(){{
        document.getElementById("gasoline-monitors").style.display="None";
        document.getElementById("diesel-monitors").style.display="Block";
    }}


    function  showWhenCheck(checkBoxId,targetId){{
        if (document.getElementById(checkBoxId).checked==false) {{
            document.getElementById(targetId).style.display="None";
        }}

        if (document.getElementById(checkBoxId).checked==true) {{
            document.getElementById(targetId).style.display="Block";
        }}
    }}
  </script> 
</body>
''' + '<br>'*10


monitor_html = '''
<input type="checkbox" style="margin-left: 30px;" name="{monitor}" id="{monitor}" value="support" onClick="showWhenCheck('{monitor}','{monitor}-check-complete')"> {monitor}: {name}
<input type="hidden" value="not support" name="{monitor}"">
<div style="display:None" id="{monitor}-check-complete">
  <input type="radio" style="margin-left: 60px;" name="{monitor}-complete" value="complete" checked> complete
  <input type="radio" style="margin-left: 60px;" name="{monitor}-complete" value="not complete"> not complete
</div><br>
'''

