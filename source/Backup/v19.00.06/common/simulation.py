
from sys import exit

import math
import random
from fractions import Fraction

from common.mypaths import *
from common.dtc_converter import dtc2hex
from common.databases import *



'''
8888888888                            888    d8b                            
888                                   888    Y8P                            
888                                   888                                   
8888888    888  888 88888b.   .d8888b 888888 888  .d88b.  88888b.  .d8888b  
888        888  888 888 "88b d88P"    888    888 d88""88b 888 "88b 88K      
888        888  888 888  888 888      888    888 888  888 888  888 "Y8888b. 
888        Y88b 888 888  888 Y88b.    Y88b.  888 Y88..88P 888  888      X88 
888         "Y88888 888  888  "Y8888P  "Y888 888  "Y88P"  888  888  88888P' 
                                                                            
                                                                            

'''
# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)


# read data from a file
def read_data(path):
    with open(path, "r") as file_object:
        return file_object.read()
    return 



def put_data_can(cmdtype, addr, data):
    '''
    This static method is use for putting hex data into CAN templates 
    There are 2 cases:
    + the number of hex data fits into 1 response
    + the number of hex data exceeds 1 response
    '''
    # CAN prefix and postfix
    if cmdtype=='req':
        CAN_PREFIX = 'INFO_DATABASE = Req>1\t\t\t'
        CAN_POSTFIX = ' \tNONE\t0\t0'
    elif cmdtype=='res':
        CAN_PREFIX =  'INFO_DATABASE = Res<1\t\t\t'
        CAN_POSTFIX = ' \tNONE\t0\t0' 

    # determin byte count
    data_bytecount = len(data) # count the number of data bytes
    bytecount = 2 + data_bytecount # 2 bytes after address + header and data
    
    # create cmd with sandboxes
    if bytecount <= 9: # if data can be put into 1 cmd
        cmd = addr + ' 08 ' + format(data_bytecount, '02x') + ' {} '*data_bytecount # base cmd
        cmd += ' 00 '*(9 - bytecount) # zeros fill
        cmd = CAN_PREFIX + cmd + CAN_POSTFIX # add simulation patterns
    else: # if data exceeds 1 cmd
        bytecount = 3 + data_bytecount # 3 bytes after address + header and data
        #create the first cmd
        cmd = addr + ' 08 10 ' + format(data_bytecount, '02x') + ' {} '*(9 - 3)
        cmd = CAN_PREFIX + cmd + CAN_POSTFIX
        # iter row need to be added to fill data
        for row in range(1,int(math.ceil((bytecount-9)/7)) + 1):  
            if row == int(math.ceil((bytecount-9)/7)): # if the last row
                cmd += ('\n' + CAN_PREFIX + 
                       addr + ' 08 ' + str((20+row)) + ' {} '*(bytecount - 9 - 7*(row-1)) + ' 00 '*(9+7*row-bytecount) +
                       CAN_POSTFIX)
            else: # other rows
                cmd += ('\n' + CAN_PREFIX + 
                       addr + ' 08 ' + str(20+row) + ' {} '*7 +
                       CAN_POSTFIX)

    cmd = cmd.format(*data)  # put data
    while '  ' in cmd: cmd = cmd.replace('  ',' ') # remove duplicate spaces
    
    # return command
    return cmd


def put_bytebit(data, bytepos, bitpos, mode):
    bytepos = int(bytepos)
    bitpos = int(bitpos)
    if bytepos > len(data) - 1: # if bytepos > the max pos
        data.extend(['00' for x in range(0, bytepos-len(data) + 1)])

    if mode=='set':
        data[bytepos] = format(int(data[bytepos], 16)|(1<<bitpos), '02x')

    return data












'''
 .d8888b.  888                            
d88P  Y88b 888                            
888    888 888                            
888        888  8888b.  .d8888b  .d8888b  
888        888     "88b 88K      88K      
888    888 888 .d888888 "Y8888b. "Y8888b. 
Y88b  d88P 888 888  888      X88      X88 
 "Y8888P"  888 "Y888888  88888P'  88888P' 
                                          
                                          

 .d88888b.  888           888  .d8888b.       .d8888b.  d8b               
d88P" "Y88b 888           888 d88P  Y88b     d88P  Y88b Y8P               
888     888 888           888        888     Y88b.                        
888     888 88888b.   .d88888      .d88P      "Y888b.   888 88888b.d88b.  
888     888 888 "88b d88" 888  .od888P"          "Y88b. 888 888 "888 "88b 
888     888 888  888 888  888 d88P"                "888 888 888  888  888 
Y88b. .d88P 888 d88P Y88b 888 888"           Y88b  d88P 888 888  888  888 
 "Y88888P"  88888P"   "Y88888 888888888       "Y8888P"  888 888  888  888 
                                                                          
                                                                          
                                                                                                                                                                                                                                              
'''                                                                                                                         

class IncorrectVinLength(Exception):
    '''
    This exeption is used when items transfered to 
    '''
    def __init__(self):
        super().__init__() 

                                                                                                
class Obd2Simulation:
    '''
    this class is to create an intance of OBDII Simulation
    if inputs is not transfer default values will be uses
    inputs = 'default'
        - filename = 'default simulation name'
    '''
    print('create OBD2 object')
    def __init__(self, 
                 inputs='default',
                 monitor_inputs='default', 
                 ld_inputs='default'):

        # unpack kwargs
        #for key, value in kwargs.items():
        #    setattr(self, key, value)
        if inputs=='default':
            inputs = {}
            inputs['filename'] = 'default'
            inputs['protocol'] = 'default'
            inputs['vin'] = 'default'
            inputs['dtcs_mode03'] = 'default'
            inputs['dtcs_mode07'] = 'default'
            inputs['dtcs_mode0A'] = 'default'



        self.error = ''
        self.inputs = inputs
        self.monitor_inputs = monitor_inputs
        self.ld_inputs = ld_inputs
    

    @staticmethod
    def create_obd2_mode09(vin='default'):
        '''
        take a parameter vin in ascii type
        convert to hex
        then return a string of simulation mode 9
        '''
        # check VIN length

        if vin=='default': vin='F'*17

        vin = str(vin).replace(' ', '')
        if len(vin) != 17:
            raise IncorrectVinLength
            
        vin_hex = []
        for c in vin:
            vin_hex.append(hex(ord(c))[2:])

        simdata = ('//NOTE:\n' +
                  '//NOTE:===== MODE $09 =====\n' + 
                  '//NOTE:. . . . . VIN: ' + vin +
                  obd2_mode09.format(*vin_hex))
        return simdata


    @staticmethod
    def create_obd2_dtcs(mode, dtcstring='default'):
        '''
        create simulation of mode dtcs
        if dtcstring = defualt => no dtcs
        mode = 03 or 07 or 0A
        '''

        # default dtc string
        if dtcstring=='default': dtcstring =''

        # refine raw string
        dtcstring = dtcstring.replace(' ','') 
        
        if dtcstring == '': # if there is no data input => return dtcs
            dtcs_sae = []
        else: # split the string input into a list of dtcs
            dtcs_sae = dtcstring.split(',')
            dtcs_sae = list(set(dtcs_sae)) # remove duplicate
            dtcstring = ', '.join(dtcs_sae)

        # convert dtcs sae => dtc hex type => data hex bytes
        data_hex = []
        for dtc in dtcs_sae:
            try: data_hex.extend(dtc2hex(dtc).split(' '))
            except Exception as e: raise e

        # request command
        data = [hex(int(str(mode),16)+int('0',16))[2:].zfill(2)]
        simdata = put_data_can(cmdtype='req', addr='000007DF', data=data)  + '\n'

        # put data in to CAN template, format(dtccount, '02x') => hex with zero
        dtccount = int(len(data_hex)/2) # number of dtcs
        data = [hex(int(str(mode),16)+int('40',16))[2:].zfill(2), '{dtccount}'.format(dtccount=format(dtccount, '02x'))]

        data.extend(data_hex)
        simdata += put_data_can(cmdtype='res', addr='000007E8', data=data) + '\n'
        
        simdata = ('//NOTE:\n'+
                   '//NOTE:===== MODE $' + mode + '=====\n' + 
                   '//NOTE:. . . . . DTCs Parsed: ' + dtcstring + '\n' +
                   simdata)

        return simdata


    @staticmethod
    def create_obd2_monitors(monitor_inputs='default'):
        '''
        TO-DO: 
            - need to check monitor list in simulation.py 
              and flask_obd2_simulation.py => shorten
        '''

        # default monitor data
        if monitor_inputs=='default':
            # monitor form input data
            monitors = ['MIS',  'FUE',  'CCM',  
                        'CAT',  'HCA',  'EVA',  
                        'AIR',  'O2S',  'HTR',  
                        'EGR_Gas',  'HCC',  'NOx',  
                        'BPS',  'EGS',  'DPF', 'EGR_Die']

            monitor_inputs = {}
            monitor_inputs['MIL'] = 'off'
            monitor_inputs['Comp'] = 'not support'
            for monitor in monitors:
                monitor_inputs[monitor] = 'support'
                monitor_inputs[monitor + '-complete'] = 'complete'


        status_inputs = {}
        for key in monitor_inputs.keys():
            if key not in ['MIL', 'Comp']:
                if '-complete' not in key:
                    checksupport = monitor_inputs[key]
                    checkcomplete = monitor_inputs[key+'-complete']
                    status_inputs[key]=[checksupport,checkcomplete]
            else:
                checksupport = monitor_inputs[key]
                status_inputs[key] = [checksupport]
        print(status_inputs)

        obd2_monitors = Obd2_Monitors(obd2_monitors_fp)
        df = obd2_monitors.sheets['Monitors']
        df = df.set_index('Monitor')

        # fiter engine by monitor compression
        if monitor_inputs['Comp']=='support':
            engine_filter = ['Both','Diesel']
        else:
            engine_filter = ['Both','Gasoline']

        data = ['41', '01'] # SID and PID

        # initial NOTE
        note = ('//NOTE:\n'+
                  '//NOTE:===== MODE $01 =====\n' + 
                  '//NOTE:. . . . . I/M Monitors: \n')


        for key, status in status_inputs.items():
            # if the engine type is not in engine filter => continue
            if df.loc[key,'Engine Type'] not in engine_filter: continue

            print(str(key) + ': ' + str(status))
            supbytepos = df.loc[key,'Support Byte Pos']
            supbitpos = df.loc[key,'Support Bit Pos']
            compbytepos = df.loc[key,'Complete Byte Pos']
            compbitpos = df.loc[key,'Complete Bit Pos']

            if key=='MIL':
                if status[0]=='on':
                    data = put_bytebit(data, compbytepos, compbitpos, mode='set') # set bit on
                    note += ('//NOTE:. . . . . . . . . . MIL: On\n')
                else:
                    data = put_bytebit(data, compbytepos, compbitpos, mode='noset') # set bit on
                    note += ('//NOTE:. . . . . . . . . . MIL: Off\n')

            elif key=='Comp':
                if status[0]=='support':
                    data = put_bytebit(data, supbytepos, supbitpos, mode='set') # set bit on
                else:
                    data = put_bytebit(data, supbytepos, supbitpos, mode='noset') # set bit on

            else: # key not MIL or Comp
                if status[0]=='support':
                    data = put_bytebit(data, supbytepos, supbitpos, mode='set') # set bit support
                    if status[1]=='complete':
                        data = put_bytebit(data, compbytepos, compbitpos, mode='noset') # not set bit complete
                        note += ('//NOTE:. . . . . . . . . . '+key+': complete\n')
                    else: # not complete
                        data = put_bytebit(data, compbytepos, compbitpos, mode='set') # set bit complete
                        note += ('//NOTE:. . . . . . . . . . '+key+': not complete\n')
                else: # not support
                    data = put_bytebit(data, supbytepos, supbitpos, mode='noset') # set bit support

        simdata = put_data_can(cmdtype='req', addr='000007DF', data=['01', '01']) + '\n'
        simdata += put_data_can(cmdtype='res', addr='000007E8', data=data)


        return note + simdata


    @staticmethod
    def get_pid_input_list(ld_inputs='default'):

        DEFAULT_PID_STR = '03-4C'

        #default
        if ld_inputs=='default':
            ld_inputs = {}
            ld_inputs['itemid_auto_setting'] = DEFAULT_PID_STR


        # get auto setting pid (03-1F or 03-06,08-1F or 03,05,08,09 or 03,05,08,09,1A-1F)
        auto_pid_str = ld_inputs['itemid_auto_setting'].replace(' ','')
        auto_pid_str = auto_pid_str if auto_pid_str != '' else DEFAULT_PID_STR # if no data input => use default 03-4C


        auto_pid_raw_list = auto_pid_str.split(',')
        auto_pid_list = []
        for element in auto_pid_raw_list:
            # if the element is not range
            if '-' not in element:
                auto_pid_list.append(element)
                continue
            # if the element is range
            pidrange = element.split('-')
            pidtop = int(pidrange[0],16)
            pidbot = int(pidrange[1],16)
            for pid in range(pidtop,pidbot+1):
                auto_pid_list.append(hex(pid)[2:].zfill(2))

        # unique list
        auto_pid_list = sorted(list(set(auto_pid_list)))
        return auto_pid_list


    @staticmethod
    def create_obd2_ld(ld_inputs='default'):

        auto_pid_list = Obd2Simulation.get_pid_input_list(ld_inputs)

        # create j1979 database
        obd2_ld = LiveDataOBD2(obd2_ld_fp)
        item_df = obd2_ld.sheets['Item ID'].set_index('ItemID')


        # to-do: check support
        # to-do: get value from user input
        # todo: need to add unit converter
        # each pid can have more than one itemid => need to filter all itemid then iterate


        simdata = ''
        full_pid_list = set(item_df['GetValueCmd'].to_list())
        for pid in auto_pid_list:
            # check if the pid does not exist in the database
            if ('01 ' + pid) not in full_pid_list and ('01 ' + pid.upper()) not in full_pid_list: # case sensitive is important
                simdata += '//NOTE: \n//NOTE: PID "{}" DOES NOT EXIST IN THE DATABASE'.format(pid) + '\n'  + '\n'
                continue

            # filter item id list => remenber case sensitive
            itemid_list = list(item_df[item_df['GetValueCmd'].isin(['01 ' + pid, '01 '+ pid.upper()])].index.values)
            
            res_concat_cmd = None
            for itemid in itemid_list:
                '''
                iter all itemid having the same PID request cmd
                '''
                raw_value = obd2_ld.get_random_raw_value(itemid)

                display_value = obd2_ld.raw_to_readable(itemid, raw_value)


                itemname = item_df.loc[itemid,'ItemName']
                itemdes = item_df.loc[itemid,'ItemDescription']

                req_cmd = obd2_ld.request_command(itemid)
                res_cmd = obd2_ld.response_command(itemid, raw_value)

                if res_concat_cmd == None: 
                    res_concat_cmd = res_cmd
                else:
                    res_concat_cmd = concat_cmds(res_concat_cmd, res_cmd)

                simdata += ('//NOTE: "{}" -- "{}"\n' +
                            '//NOTE: PID: {} --- Value: {}\n' +
                            '//NOTE: \n').format(itemname,itemdes,req_cmd,display_value)
            


            req_split = req_cmd.split()
            res_split = res_concat_cmd.split()


            simdata += put_data_can(cmdtype='req', addr='000007DF', data=req_split) + '\n'
            simdata += put_data_can(cmdtype='res', addr='000007E8', data=res_split) + '\n'  + '\n'


        # initial NOTE
        note = ('//NOTE:\n'+
                '//NOTE:===== MODE $01 =====\n' + 
                '//NOTE:. . . . . Generic Live Data: \n')

        return note + simdata

    @staticmethod
    def create_obd2_ld_support(ld_inputs='default'):
        auto_pid_list = Obd2Simulation.get_pid_input_list(ld_inputs)

        obd2_ld = LiveDataOBD2(obd2_ld_fp)
        profile_df = obd2_ld.sheets['Profile ID'].set_index('ItemID')
        item_df = obd2_ld.sheets['Item ID'].set_index('ItemID')


        #to-do: cho nay lap lại method cu, thêm monitor icon, thêm check support cho PID check support
        full_pid_list = set(item_df['GetValueCmd'].to_list())
        for pid in auto_pid_list:
            if ('01 ' + pid) not in full_pid_list and ('01 ' + pid.upper()) not in full_pid_list: # case sensitive is important
                continue



            # create itemid_list first time
            if 'itemid_list' not in locals(): itemid_list = []
            # filter item id list => remenber case sensitive
            itemid_list.extend(list(item_df[item_df['GetValueCmd'].isin(['01 ' + pid, '01 '+ pid.upper()])].index.values))

        if 'itemid_list' not in locals(): 
            return None
        for itemid in itemid_list:
            if 'support_cmds' not in locals(): support_cmds = {'01 00': '41 00 80 00 00 00'}

            req, res = obd2_ld.get_support_cmds(itemid)

            if req not in support_cmds.keys(): support_cmds[req] = ''
            support_cmds[req] = concat_cmds(support_cmds[req], res)
            

            # support the bit for the next check support cmd 01 20 ...
            if req!='01 00':
                pre_req = req[0:3] + hex(int(req[3:5],16) - 32)[2:].zfill(2)
                pre_res = concat_cmds(support_cmds[pre_req], '00 00 00 00 00 01')
                support_cmds[pre_req] = pre_res


        for req,res in support_cmds.items():
            if 'simdata' not in locals(): simdata = ''

            req_split = req.split()
            res_split = res.split()
            simdata += put_data_can(cmdtype='req', addr='000007DF', data=req_split) + '\n'
            simdata += put_data_can(cmdtype='res', addr='000007E8', data=res_split) + '\n'  + '\n'


        # initial NOTE
        note = ('//\n'+
                '//===== MODE $01 - Check support =====\n')

        return note + simdata



    def create_obd2_ff(ff_inputs='default'):
        # add ld check support
        simdata += Obd2Simulation.create_obd2_ld_support(self.ld_inputs) + '\n\n\n'

        # add monitor icons
        simdata += Obd2Simulation.create_obd2_monitors(self.monitor_inputs) + '\n\n\n'

        # add live data
        # temp = obd2_ld
        try: simdata += Obd2Simulation.create_obd2_ld(self.ld_inputs) + '\n\n\n\n'
        except Exception as e: error += e + '\n'



    def create_sim_file(self):
        #init error val
        error = ''

        # if default
        if self.inputs['filename'] == 'default': self.inputs['filename'] = 'noname_specified'

        # if name = ''
        if self.inputs['filename'] == '': self.inputs['filename'] = 'noname_specified'

        # first create sim text with config
        simdata = can614500_config + '\n\n\n\n' + obd2_mode02_nofreeframe + '\n\n\n\n' # + obd2_ld_check_support + '\n\n\n\n'

        # add mode 09
        try: simdata += Obd2Simulation.create_obd2_mode09(self.inputs['vin']) + '\n\n\n\n'
        except Exception as e: error += e + '\n'

        # add mode 03
        try: simdata += Obd2Simulation.create_obd2_dtcs(mode='03', dtcstring=self.inputs['dtcs_mode03']) + '\n\n\n\n'
        except Exception as e: error += e + '\n'

        # add mode 07
        try: simdata += Obd2Simulation.create_obd2_dtcs(mode='07', dtcstring=self.inputs['dtcs_mode07']) + '\n\n\n\n'
        except Exception as e: error += e + '\n'

        # add mode 0A
        try: simdata += Obd2Simulation.create_obd2_dtcs(mode='0A', dtcstring=self.inputs['dtcs_mode0A']) + '\n\n\n\n'
        except Exception as e: error += e + '\n'

        # add ld check support
        simdata += Obd2Simulation.create_obd2_ld_support(self.ld_inputs) + '\n\n\n'

        # add monitor icons
        simdata += Obd2Simulation.create_obd2_monitors(self.monitor_inputs) + '\n\n\n'

        # add live data
        # temp = obd2_ld
        try: simdata += Obd2Simulation.create_obd2_ld(self.ld_inputs) + '\n\n\n\n'
        except Exception as e: error += e + '\n'


        # check error
        if error != '': return False

        path = str(simulation_dir_path) + '\\' + self.inputs['filename'] + '.sim'
        write_data(path, simdata)
        print('Simulation created successfully')

        return True


























'''
 .d8888b.  888                            
d88P  Y88b 888                            
888    888 888                            
888        888  8888b.  .d8888b  .d8888b  
888        888     "88b 88K      88K      
888    888 888 .d888888 "Y8888b. "Y8888b. 
Y88b  d88P 888 888  888      X88      X88 
 "Y8888P"  888 "Y888888  88888P'  88888P' 
                                          
                                          
                                          
8888888888                     888      .d8888b.  d8b               
888                            888     d88P  Y88b Y8P               
888                            888     Y88b.                        
8888888   .d88b.  888d888  .d88888      "Y888b.   888 88888b.d88b.  
888      d88""88b 888P"   d88" 888         "Y88b. 888 888 "888 "88b 
888      888  888 888     888  888           "888 888 888  888  888 
888      Y88..88P 888     Y88b 888     Y88b  d88P 888 888  888  888 
888       "Y88P"  888      "Y88888      "Y8888P"  888 888  888  888 
                                                                      
                                                                      
                                                                      
'''
class FordSimulation:
    '''
    this class is to create an intance of OBDII Simulation
    '''
    print('create NWS object')
    def __init__(self, ymme_dict):
        #self.result = ''
        self.year = ymme_dict['year']
        self.make = ymme_dict['make']
        self.model = ymme_dict['model']
        self.engine = ymme_dict['engine']
        self.name = ymme_dict['name']

    def create_dtc(self):
        '''
        create simulation of mode dtcs
        '''
        year = self.year 
        make = self.make
        model = self.model
        engine = self.engine

        fordnws = FordNWS(ford_nws_fp)
        forddtc = FordDTC(ford_dtc_fp)


        ymme_df = fordnws.sheets['Ymme'][2:]

        ymme_df=Database.filter_ymme(ymme_df,
                                     self.year,
                                     self.make,
                                     self.model,
                                     self.engine)

        profile_df = fordnws.sheets['Profile']
        profile_df = profile_df.set_index('MsgID/ECUID')
        
        dtc_df = forddtc.sheets['DTC'][2:]
        dtc_df = dtc_df[dtc_df['Year'].isin([str(year), year, 'N/A', ''])]
        dtc_df = dtc_df[dtc_df['Model'].isin([model, 'N/A', ''])]
        dtc_df = dtc_df[dtc_df['Option 1'].isin([engine, 'N/A', ''])]

        dtc_status_df = fordnws.sheets['FordStatus']
        dtc_status_df = dtc_status_df[~dtc_status_df['Status'].isna()]

        dtc_sub_df = forddtc.sheets['Ford-Sub']
        dtc_sub_df = dtc_sub_df[~dtc_sub_df['SubCodeDescription-English'].isna()]

        final_simdata = ''

        for index, row in ymme_df.iterrows():
            simdata = ''
            # get information
            profile = row['MsgID/ECUID']
            system = row['System']
            systemstr = row['SystemStr']
            protocol = profile_df.loc[profile, 'Protocol']

            # TO-DO: will code later
            if protocol in ['PROTOCOL_PWM', 'PROTOCOL_ISO9141']: continue


            res_add = str(profile_df.loc[profile, 'CanStart1'])
            print('response address: ' + res_add)
            req_add = str(profile_df.loc[profile, 'TagAddr/CanReq1'])
            selftest = 'Continuous Memory DTCs'

            # filter dtcs
            refined_dtc_df = dtc_df
            refined_dtc_df = refined_dtc_df[refined_dtc_df['System'].isin([system, 'N/A', ''])]
            refined_dtc_df = refined_dtc_df[refined_dtc_df['Protocol'] == protocol] if protocol in ['PROTOCOL_CAN_UDS', 'PROTOCOL_MCAN UDS'] else refined_dtc_df[refined_dtc_df['Protocol'].isin(['N/A',''])]
            refined_dtc_df = refined_dtc_df[refined_dtc_df['Option 3'].isin([selftest, 'N/A', ''])]
            refined_dtc_df = refined_dtc_df[~refined_dtc_df['SAE DTC'].isna()]
            
            # get random dtc list
            dtc_list = list(set(list(refined_dtc_df['SAE DTC'])))
            dtc_list = random.sample(dtc_list, len(dtc_list) if len(dtc_list) < 3 else random.randint(3,8))

            # final dtc dataframe
            refined_dtc_df = refined_dtc_df[refined_dtc_df['SAE DTC'].isin(dtc_list)]

            # print infor
            simdata += '\n\n'
            simdata += '//NOTE:system: ' + systemstr + '\n'
            simdata += '//NOTE:profile: ' + profile + '\n'
            simdata += '//NOTE:protocol: ' + protocol + ' ({}-{}-{})'.format(profile_df.loc[profile, 'CanH/Rx'], profile_df.loc[profile, 'CanL/Tx'], profile_df.loc[profile, 'Baudrate']) + '\n'


            # refine raw string
            dtcstring = str(dtc_list).replace('[','').replace(']','').replace("'",'').replace(' ','') 
            simdata += '//NOTE:dtc list: ' + dtcstring + '\n'

            # string to list
            if dtcstring == '': # if there is no data input => return dtcs
                dtcs_sae = []
            else: # split the string input into a list of dtcs
                dtcs_sae = dtcstring.split(',')


            if protocol in ['PROTOCOL_CAN_UDS', 'PROTOCOL_MCAN UDS']:

                # convert dtcs sae => dtc hex type => data hex bytes
                data_hex = []
                simdata += '//NOTE:\n//NOTE:DTC Definitions:\n'
                for dtc in dtcs_sae:
                    status = dtc_status_df[dtc_status_df['Protocol']=='PROTOCOL_CAN_UDS'].sample(1)['Subcode'].to_list()[0]
                    subcode = dtc_sub_df[dtc_sub_df['Protocol']=='PROTOCOL_CAN_UDS'].sample(1)['SAE Sub-DTC (HEX)'].to_list()[0]
                    data_hex.extend(dtc2hex(dtc).split(' '))
                    data_hex.extend([subcode, status])

                    final_dtc_df = refined_dtc_df[refined_dtc_df['SAE DTC']==dtc]
                    dtc_level_set = max(set(final_dtc_df['Option 4']))
                    dtc_def_list = final_dtc_df[final_dtc_df['Option 4']==dtc_level_set]['CodeDescription-English'].to_list()

                    status_def = dtc_status_df[dtc_status_df['Protocol']=='PROTOCOL_CAN_UDS']
                    status_def = status_def[status_def['Subcode']==status]['Status'].to_list()[0]

                    sub_def = dtc_sub_df[dtc_sub_df['Protocol']=='PROTOCOL_CAN_UDS']
                    sub_def = sub_def[sub_def['SAE Sub-DTC (HEX)']==subcode]['SubCodeDescription-English'].to_list()[0]

                    simdata += '//NOTE:\n//NOTE:===' + dtc + '-'+ subcode +  ' (' + status_def + ')\n'
                    for definition in  dtc_def_list:
                        simdata += '//NOTE:  - ' + definition + ' - ' + sub_def + '\n'
                
                # request command
                data = ['19', '02', '8F']
                simdata += put_data_can(cmdtype='req', addr='00000' + req_add, data=data) + '\n'

                # response command
                data = ['59', '02', 'FF']
                data.extend(data_hex)
                simdata += put_data_can(cmdtype='res', addr='00000' + res_add, data=data) + '\n'


            elif protocol in ['PROTOCOL_CAN', 'PROTOCOL_MCAN']:
                # convert dtcs sae => dtc hex type => data hex bytes
                data_hex = []
                simdata += '//NOTE:\n//NOTE:DTC Definitions:\n'
                for dtc in dtcs_sae:
                    subcode_status = dtc_status_df[dtc_status_df['Protocol']=='PROTOCOL_CAN'].sample(1)['Subcode'].to_list()[0]
                    data_hex.extend(dtc2hex(dtc).split(' '))
                    data_hex.extend([subcode_status])

                    final_dtc_df = refined_dtc_df[refined_dtc_df['SAE DTC']==dtc]
                    print(dtc)
                    print(final_dtc_df.to_string())

                    dtc_level_set = min(set(final_dtc_df['Option 4']))
                    dtc_def_list = final_dtc_df[final_dtc_df['Option 4']==dtc_level_set]['CodeDescription-English'].to_list()

                    status_def = dtc_status_df[dtc_status_df['Protocol']=='PROTOCOL_CAN']
                    status_def = status_def [status_def['Subcode']==subcode_status]['Status'].to_list()[0]

                    print(subcode_status)
                    sub_def = dtc_sub_df[dtc_sub_df['Protocol']=='PROTOCOL_CAN']
                    sub_def = sub_def[sub_def['SAE Sub-DTC (HEX)']==subcode_status]['SubCodeDescription-English'].to_list()
                    try:
                        sub_def = sub_def[0]
                    except Exception as e:
                        sub_def = '(No subcode definition)'


                    simdata += '//NOTE:\n//NOTE:===' + dtc + '-'+ subcode_status +  ' (' + status_def + ')\n'
                    for definition in  dtc_def_list:
                        simdata += '//NOTE:  - ' + definition + ' - ' + sub_def + '\n'


                # request command
                data = ['18', '00', 'FF', '00']
                simdata += put_data_can(cmdtype='req', addr='00000' + req_add, data=data) + '\n'

                # response command
                data = ['58', '0F']
                data.extend(data_hex)
                simdata += put_data_can(cmdtype='res', addr='00000' + res_add, data=data) + '\n'

            else:
                print('not supported protocol')
            final_simdata += simdata + '\n\n'
        return final_simdata

    
    def create_livedata(self, path):
        '''
        
        '''

        year = self.year 
        make = self.make
        model = self.model
        engine = self.engine

        ford_ld = FordLiveData(path)



        data = ford_ld.get_all(year, make, model)
        item_infor = data['item_infor']

        #CODE NOTES: change address by database
        final_simdata = ''


        for key,infor in item_infor.items():
            item = infor[0]
            itemdes = infor[1]
            value = infor[2]
            unit = infor[3]
            request_command = infor[4]
            req = infor[4].split()
            res = infor[5].split()

            print(key)
            print(infor)


            simdata = ''
            simdata += ('//NOTE: "{}" -- "{}"\n' +
                        '//NOTE: PID: {} --- Value: {}({})\n' +
                        '//NOTE: \n').format(item,itemdes,request_command,value,unit)

            simdata += put_data_can(cmdtype='req', addr='00 00 07 xx', data=req) + '\n'
            simdata += put_data_can(cmdtype='res', addr='00 00 07 +08', data=res) + '\n'  + '\n'

            final_simdata += simdata + '\n\n'

        return final_simdata


    def create_sim_file(self):
        # first create sim text with config
        simdata = can614500_config + can_init + obd2_mode01 + '\n\n'

        # add oem dtcs
        simdata += self.create_dtc() + '\n\n'

        path = str(simulation_dir_path) + '\\' + self.name + '.sim'
        write_data(path, simdata)
        

        write_data(path, simdata)

        print(simdata)
        print('Simulation created successfully')
        return True





                                                                      

class MazdaSimulation:
    '''
    this class is to create an intance of OBDII Simulation
    '''
    print('create NWS object')
    def __init__(self, ymme_dict):
        #self.result = ''
        self.year = ymme_dict['year']
        self.make = ymme_dict['make']
        self.model = ymme_dict['model']
        self.engine = ymme_dict['engine']
        self.name = ymme_dict['name']


    
    def create_livedata(self, path):
        '''
        
        '''

        year = self.year 
        make = self.make
        model = self.model
        engine = self.engine

        mazda_ld = MazdaLiveData(path)



        data = mazda_ld.get_all(year, make, model)
        item_infor = data['item_infor']

        #CODE NOTES: change address by database
        final_simdata = ''


        for key,infor in item_infor.items():
            item = infor[0]
            itemdes = infor[1]
            value = infor[2]
            unit = infor[3]
            request_command = infor[4]
            req = infor[4].split()
            res = infor[5].split()

            print(key)
            print(infor)


            simdata = ''
            simdata += ('//NOTE: "{}" -- "{}"\n' +
                        '//NOTE: PID: {} --- Value: {}({})\n' +
                        '//NOTE: \n').format(item,itemdes,request_command,value,unit)

            simdata += put_data_can(cmdtype='req', addr='00 00 07 xx', data=req) + '\n'
            simdata += put_data_can(cmdtype='res', addr='00 00 07 +08', data=res) + '\n'  + '\n'

            final_simdata += simdata + '\n\n'

        return final_simdata





































'''
 .d8888b.  d8b                   88888888888                                 888          888                      
d88P  Y88b Y8P                       888                                     888          888                      
Y88b.                                888                                     888          888                      
 "Y888b.   888 88888b.d88b.          888      .d88b.  88888b.d88b.  88888b.  888  8888b.  888888  .d88b.  .d8888b  
    "Y88b. 888 888 "888 "88b         888     d8P  Y8b 888 "888 "88b 888 "88b 888     "88b 888    d8P  Y8b 88K      
      "888 888 888  888  888         888     88888888 888  888  888 888  888 888 .d888888 888    88888888 "Y8888b. 
Y88b  d88P 888 888  888  888         888     Y8b.     888  888  888 888 d88P 888 888  888 Y88b.  Y8b.          X88 
 "Y8888P"  888 888  888  888         888      "Y8888  888  888  888 88888P"  888 "Y888888  "Y888  "Y8888   88888P' 
                                                                    888                                            
                                                                    888                                            
                                                                    888                                            
'''
can614500_config = '''
###########################################
#         Auto Generated                  #
###########################################
<config sw> Protocol = 29
<config sw> PIN_KRX_CANH = 6
<config sw> TYPE_KRX_CANH = 0
<config sw> VOLT_KRX_CANH = 3
<config sw> PIN_KTX_CANH = 14
<config sw> TYPE_KTX_CANH = 0
<config sw> VOLT_KTX_CANH = 3
<config sw> PIN_LRX_CANH =  6
<config sw> TYPE_LTX_CANH = 0
<config sw> VOLT_LTX_CANH = 3
<config sw> VREF = 0
<config sw> BAUDRATE = 500000
<config sw> DATABIT = 0
<config sw> PARITY = 0
<config sw> TBYTE = 8
<config sw> TFRAME = 10
<config sw> F CAN NUMBER FRAME = 1
<config sw> RANGE =   700,7ff;
###########################################
#         End of config                   #
###########################################
'''

obd2_ld_check_support = '''
//MODE 1 Live Data Check Support
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 00 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 00 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 20 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 20 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 40 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 40 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 60 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 60 FF FF FF FF 00 \tNONE\t0\t0
'''

obd2_mode01 = '''
//MODE 1
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 00 xx xx xx xx xx \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 00 BE 3F A8 13 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 01 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 01 00 07 65 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 01 04 01 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 7F 04 22 00 00 00 00 \tNONE\t0\t0
'''

obd2_mode02_nofreeframe = '''
//MODE 2 (No FreeFrame)
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 00 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 00 00 FF 9F 88 87 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 20 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 20 00 00 07 F1 19 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 40 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 40 00 FE D0 40 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 02 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 02 00 00 00 00 00 \tNONE\t0\t0
'''


obd2_mode02 = '''
//MODE 2
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 xx xx xx xx xx xx \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 00 00 FE 3F 88 03 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 20 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 20 00 00 17 F0 11 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 40 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 40 00 FE D0 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 01 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 01 00 07 E5 E5 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 01 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 01 00 00 07 E5 E5 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 02 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 02 00 12 33 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 03 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 03 00 01 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 04 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 04 00 FF 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 05 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 05 00 16 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 06 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 06 00 80 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 07 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 07 00 80 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 0B 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 0B 00 7B 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 0C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 0C 00 00 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 0D 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 0D 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 0E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 0E 00 94 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 0F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 0F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 10 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 10 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 11 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 11 00 FB 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 15 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 15 00 FF FF 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 1F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 1F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 2C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 2C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 2E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 2E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 2F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 2F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 30 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 30 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 31 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 31 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 32 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 32 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 33 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 33 00 5B 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 34 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 34 00 00 00 80 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 3C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 3C 00 00 DE 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 41 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 07 42 41 00 00 76 00 E5 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 42 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 42 00 29 57 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 43 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 43 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 44 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 05 42 44 00 86 66 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 45 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 45 00 DC 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 46 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 46 00 16 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 47 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 47 00 FD 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 49 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 49 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 4A 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 4A 00 01 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 03 02 4C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 42 4C 00 18 00 00 00 \tNONE\t0\t0
'''

obd2_mode09 = '''
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 09 00 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 49 00 55 40 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 09 08 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 10 2B 49 08 14 02 04 06 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 21 B5 02 3C 02 04 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 22 00 00 02 A8 02 04 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 23 00 00 00 02 B9 02 04 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 24 00 00 00 00 00 B5 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 25 46 02 44 02 04 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 26 00 00 00 00 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 09 02 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 10 14 49 02 01 {} {} {} \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 21 {} {} {} {} {} {} {} \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 22 {} {} {} {} {} {} {} \tNONE\t0\t0
'''

#INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 01 00 00 00 00 00 \tNONE\t0\t0
#INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 01 00 07 E5 E5 00 \tNONE\t0\t0

obd2_ld = '''
//MODE 1 Live Data
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 00 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 00 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 20 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 20 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 40 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 40 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 60 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 60 FF FF FF FF 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 13 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 13 03 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 03 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 03 01 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 04 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 04 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 05 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 05 5F 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 06 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 06 80 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 07 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 07 80 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 0B 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 0B 7B 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 0C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 0C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 0D 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 0D 10 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 0E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 0E 94 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 0F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 0F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 10 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 10 01 20 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 11 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 11 1E 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 15 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 15 FF FF 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 1C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 1C 02 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 1F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 1F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 21 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 21 00 e0 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 2C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 2C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 2E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 2E 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 2F 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 2F 10 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 30 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 30 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 31 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 31 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 32 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 32 41 3A 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 33 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 33 5B 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 34 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 34 00 00 80 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 3C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 3C 00 DE 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 42 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 42 29 57 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 43 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 43 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 44 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 44 86 66 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 45 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 45 DF 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 46 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 46 16 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 47 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 47 FD 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 49 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 49 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 4A 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 4A 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 4C 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 03 41 4C 18 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 4D 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 04 41 4D 18 00 00 00 00 \tNONE\t0\t0
'''


can_init = '''
//Init CAN and CAN UDS
INFO_DATABASE = Req>1\t\t\t00 00 07 xx 08 03 22 02 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t00 00 07 +08 08 04 62 02 00 0F 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t00 00 07 xx 08 03 22 D1 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t00 00 07 +08 08 04 62 D1 00 00 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t00 00 07 xx  08 03 14 FF 00 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t00 00 07 +08 08 01 54 xx xx xx xx xx xx \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t00 00 07 xx 08 03 22 02 02 00 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t00 00 07 +08 08 04 62 02 02 00 00 00 00 \tNONE\t0\t0

INFO_DATABASE = Req>1\t\t\t00 00 07 xx  08 04 14 FF FF FF 00 00 00 \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t00 00 07 +08 08 01 54 00 00 00 00 00 \tNONE\t0\t0
'''













