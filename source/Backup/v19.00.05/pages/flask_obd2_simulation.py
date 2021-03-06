from flask import Flask, request, send_file, abort
from common.path_management import *
from common import htmllib
from common.databases import *
from common.simulation import Obd2Simulation


from flask import Blueprint
app_obd2_simulation = Blueprint("app_obd2_simulation", __name__)


# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)

def add_ld_html(j1979_ld_db):
    '''
    this function will create a j1979 object 
    then using the database to create html of showing PIDs
    '''
    # df from j1979 object
    item_df = j1979_ld_db.sheets['Item ID']
    table_df = j1979_ld_db.sheets['Table ID']
    html = ''

    for index, row in item_df.iterrows():   
        # check if the row contains data
        if not isinstance(row['ItemID'], str): continue
        #
        if isinstance(row['TableID'], float): # if the PID is not table value type
            input_type_html = ('Value must be from Min: ' + str(row['Min']) + ' to ' + 'Max: ' + str(row['Max']) + '<br>'+
                               '<input placeholder="(input value...)" class="inputtext" type="text" name="{itemID}">'.format(itemID=str(row['ItemID'])))
        else: # if the PID is table type
            options_html = ''

            options_df = table_df[table_df['TableID'] == row['TableID']] # sub df containing data of a tableID
            options = ['(select value...)'] + list(options_df['TABLE_TEXT']) # create a list of table values

            # create a html drop down box 
            for option in options:
                options_html += '<option value="{option}">{option}</option>'.format(option=option)
            input_type_html = '<select class="inputtext" name="{itemID}"><{options}></select>'.format(itemID=str(row['ItemID']), options=options_html)
            
        # create html of PIDs
        html += ('<br>'*2 +
                '<div style="margin-left: 30px;">' +
                'PID ' + str(row['GetValueCmd']) + ' --- ' + str(row['ItemName']) + ' (' + str(row['ItemDescription']) + ') ' + '<br>' +
                input_type_html +
                '</div>')
        
    html = ('<div style="height:300px; width:70%; border:1px solid #ccc; overflow:auto;">' + 
            '<p style="color:Blue; width:70%; padding: 5px 30px;">If any PID which is not provided a user-input value, an auto-generated value will be taken or the PID will not be supported depending on the setting of auto value generation</p>' +
            html + '<br>'*5 +'</div>')
    #write_data(r'C:\Users\ThienNguyen\Desktop\test.html', htmllib.head.format() + html)
    return html




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
    # create j1979 live data database object and crate ld html
    j1979_ld_db = LiveDataJ1979(j1979_ld_path)
    generic_ld = add_ld_html(j1979_ld_db)

    # create obdii monitors html
    general_monitors,gasoline_monitors,diesel_monitors = add_monitors_html()
    
    if request.method == 'GET':
        print('print tracking: GET show_obd2_simulation ')
        return  obd2_simulation_html.format(result='',
                                           general_monitors=general_monitors,
                                           gasoline_monitors=gasoline_monitors,
                                           diesel_monitors=diesel_monitors,
                                           generic_ld=generic_ld)
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
        item_df = j1979_ld_db.sheets['Item ID']
        itemid_lst = [x for x in list(item_df['ItemID']) if isinstance(x, str)]
        for itemid in itemid_lst:
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
    <b style="font-size:20px;"">Mode $01 - Monitors</b><br><br>
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
    
    <br><br>
    <b style="font-size:20px;">Mode $01 - Live Data</b><br><br>
    Please input PIDs you want to generate values automatically:<br>
    Example: 03-1F or 03-06,08-1F or 03,05,08,09 or 03,05,08,09,1A-1F<br>
    <input type="text" class="inputtext" placeholder="Default: 03-4C" name="itemid_auto_setting" value=""><br><br><br>
    You can input your disired values below:<br>
    {generic_ld}

    <br><br><br>
    <input type="submit" class="button_base button_input_submit"  name="submit_button" value="Submit">
    
    <br><br><br>



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

