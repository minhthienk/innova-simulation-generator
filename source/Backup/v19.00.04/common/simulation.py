from common.path_management import *
from common.dtc_converter import dtc2hex
from common.databases import Obd2_Monitors
from common.path_management import obd2_monitors_path
import math





# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)


# read data from a file
def read_data(path):
    with open(path, "r") as file_object:
        return file_object.read()
    return 


def vin2hex(vin_ascii):
    vin_hex = []
    for c in vin_ascii:
        vin_hex.append(hex(ord(c))[2:])
    return vin_hex


def create_obd2(vehicle_name, vin='F'*17):
    vin = str(vin).replace(' ', '')
    if len(vin) != 17:
        print('Simulation created failed')
        return False

    simdata = (
        can614500_config +
        obd2_mode1 +
        obd2_mode37A +
        obd2_mode2 +
        obd2_mode9.format(*vin2hex(vin)))

    path = str(simulation_dir_path) + '\\' + vehicle_name
    write_data(path, simdata)
    print('Simulation created successfully')
    return True


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


class Obd2Simulation:
    '''
    this class is to create an intance of OBDII Simulation
    '''
    print('create OBD2 object')
    def __init__(self, inputs, monitor_inputs):
        # unpack kwargs
        #for key, value in kwargs.items():
        #    setattr(self, key, value)
        self.result = ''
        self.inputs = inputs
        self.monitor_inputs = monitor_inputs
    
    @staticmethod
    def create_obd2_mode09(vin):
        '''
        take a parameter vin in ascii type
        convert to hex
        then return a string of simulation mode 9
        '''
        # check VIN length
        vin = str(vin).replace(' ', '')
        if len(vin) != 17:
            return 'Error: incorrect VIN length'
            
        vin_hex = []
        for c in vin:
            vin_hex.append(hex(ord(c))[2:])

        simdata = ('//NOTE:\n' +
                  '//NOTE:===== MODE $09 =====\n' + 
                  '//NOTE:. . . . . VIN: ' + vin + '\n' +
                  obd2_mode09.format(*vin_hex))
        return simdata

    @staticmethod
    def create_obd2_dtcs(mode, dtcstring):
        '''
        create simulation of mode dtcs
        '''
        # refine raw string
        dtcstring = dtcstring.replace(' ','') 
        
        if dtcstring == '': # if there is no data input => return dtcs
            dtcs_sae = []
        else: # split the string input into a list of dtcs
            dtcs_sae = dtcstring.split(',')

        # convert dtcs sae => dtc hex type => data hex bytes
        data_hex = []
        for dtc in dtcs_sae:
            print('DTC')
            print(dtc)
            if 'Error' in dtc2hex(dtc):
                return 'Error: incorrect DTC input format'
            else:
                data_hex.extend(dtc2hex(dtc).split(' '))

        # request command
        data = [hex(int(str(mode),16)+int('0',16))[2:].zfill(2)]
        simdata = put_data_can(cmdtype='req', addr='000007DF', data=data)  + '\n'

        # put data in to CAN template, format(dtccount, '02x') => hex with zero
        dtccount = int(len(data_hex)/2) # number of dtcs
        data = [hex(int(str(mode),16)+int('40',16))[2:].zfill(2), '{dtccount}'.format(dtccount=format(dtccount, '02x'))]

        data.extend(data_hex)
        simdata += put_data_can(cmdtype='res', addr='000007E8', data=data) + '\n'
        print(simdata)
        
        simdata = ('//NOTE:\n'+
                  '//NOTE:===== MODE $' + mode + '=====\n' + 
                  '//NOTE:. . . . . DTCs Parsed: ' + dtcstring + '\n' +
                  simdata)

        print(simdata)
        return simdata

    @staticmethod
    def create_obd2_monitors(monitor_inputs):
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

        obd2_monitors = Obd2_Monitors(obd2_monitors_path)
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


        return note + '\n' + simdata


    def create_obd2_ld():
        pass


    def create_sim_file(self):
        self.result=''
        if self.inputs['filename'] == '': self.result = 'Error: no file name input\n'
        # first create sim text with config
        simdata = can614500_config + '\n\n' + obd2_ld + '\n\n' + obd2_mode02_nofreeframe
        # add mode 09
        temp = Obd2Simulation.create_obd2_mode09(self.inputs['vin'])
        if 'Error' not in temp:
            simdata += '\n\n' + temp
        else:
            self.result += '\n' + temp
        # add mode 03
        temp = Obd2Simulation.create_obd2_dtcs(mode='03', dtcstring=self.inputs['dtcs_mode03'])
        if 'Error' not in temp:
            simdata += '\n\n' + temp
        else:
            self.result += '\n' + temp
        # add mode 07
        temp = Obd2Simulation.create_obd2_dtcs(mode='07', dtcstring=self.inputs['dtcs_mode07'])
        if 'Error' not in temp:
            simdata += '\n\n' + temp
        else:
            self.result += '\n' + temp
        # add mode 0A
        temp = Obd2Simulation.create_obd2_dtcs(mode='0A', dtcstring=self.inputs['dtcs_mode0A'])
        if 'Error' not in temp:
            simdata += '\n\n' + temp
        else:
            self.result += '\n' + temp

        # add monitor icons
        temp = Obd2Simulation.create_obd2_monitors(self.monitor_inputs)
        simdata += '\n\n' + temp


        # check result
        if self.result != '': return False

        path = str(simulation_dir_path) + '\\' + self.inputs['filename'] + '.sim'
        write_data(path, simdata)
        print('Simulation created successfully')

        return True


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

INFO_DATABASE = Req>1\t\t\t000007DF 08 02 01 00 xx xx xx xx xx \tNONE\t0\t0
INFO_DATABASE = Res<1\t\t\t000007E8 08 06 41 00 BE 3F A8 13 00 \tNONE\t0\t0
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