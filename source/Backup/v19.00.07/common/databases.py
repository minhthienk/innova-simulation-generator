import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy



import pandas as pd
from pathlib import Path

from fractions import Fraction
import random


from common.mypaths import *
from common.mylog import *
from common.myexceptions import *


pd.set_option('display.max_colwidth', 99999)
pd.set_option('display.max_columns', 20)
pd.options.display.float_format = '{:.0f}'.format





def clean_cmd_string(cmd):
    while ' '*2 in cmd:
        cmd = cmd.replace(' '*2, ' '*1)
    
    if cmd[0:1]==' '*1: cmd = cmd[1:]
    if cmd[-1:]==' '*1: cmd = cmd[0:-1]

    return cmd


def concat_cmds(cmd1, cmd2):
    '''
    cancatenate 2 cmds in to 1 using bitwise operater 'or'
    cmd1 and cmd 2 are string type
    '''

    cmd1 = clean_cmd_string(cmd1)
    cmd2 = clean_cmd_string(cmd2)
    list1 = cmd1.split()
    list2 = cmd2.split()

    unique_list = []
    maxlen = len(list1) if len(list1)>len(list2) else len(list2)
    for x in range(0, maxlen):

        #print('list1[x] = ', list1[x] if x <= (len(list1)-1) else 0, ' ---- ',  'list2[x] = ', list2[x] if x <= (len(list2)-1) else 0)

        a = int(list1[x],16) if x <= (len(list1)-1) else 0
        b = int(list2[x],16) if x <= (len(list2)-1) else 0
        unique_list.append(hex(a|b)[2:].zfill(2))

    cmd = ' '.join(unique_list)
    return cmd







class Manufacturer:
    def __init__(self, mfr_name):
        self.dtbs = {}
        self.dtbs['YMME'] = Ymme(ymme_path[mfr_name])
        self.dtbs['Battery Procedure'] = BatteryProcedure(battery_reset_path[mfr_name])
        self.dtbs['VIN Decode'] = VinDecode(vin_path[mfr_name])

    # filter market
    def filter_market(self, market):
        # iterate all dtbs
        for dtb_name in self.dtbs.keys():
            # iterate all sheets
            for sheet_name in self.dtbs[dtb_name].sheets.keys():
                df = self.dtbs[dtb_name].sheets[sheet_name]
                # iterate all columns to determine which column is the assigned market
                market_filter = None
                for col in df.columns:
                    if df[col].values[1] == market:
                        market_filter = col
                # filter market
                if market_filter != None:
                    df = df[df[market_filter]=='v']

                self.dtbs[dtb_name].sheets[sheet_name] = df
        return self

    # filter all databases to compare to the origin ymme
    def filter_existent_ymme(self):
        cols = ['Year','Make','Model','Engine'] # cols need to compare
        orig_ymme = self.dtbs['YMME'].sheets['YMME'] # original ymme database df
        # iterate all dtbs
        for dtb_name in self.dtbs.keys():
            # iterate all sheets in each dtb
            for sheet_name in self.dtbs[dtb_name].sheets.keys():
                # assign sheet to a valuable df
                df = self.dtbs[dtb_name].sheets[sheet_name]
                # iterate all columns in the sheet to check if the column is year make model engine
                for col in df.columns:
                    if col in cols:
                        # if in the orig ymme at the current column contains  N/A => get all column
                        if orig_ymme[col].isnull().values.sum()>0:
                            break
                        # filter ymme which is in original ymme and is N/A
                        df = df[(df[col].isin(list(orig_ymme[col]))) | (df[col].isnull())]

                self.dtbs[dtb_name].sheets[sheet_name] = df
        return self











class Database:
    # Contructor
    def __init__(self, path, sheet_names):
        self.sheets = self.load_dtb(path, sheet_names) # a dict to contain all sheets data frame
    # load dtb from excel or pickle files
    @staticmethod
    def load_dtb(path, sheet_names):
        # create data frames from pickle files if not create pickle files
        sheets = {}
        filename = Path(path).stem # get file name of ymme path
        for sheet_name in sheet_names:
            # print('Processing ' + filename + '_sheet_' + sheet_name)
            # read pickle data
            try: 
                pickled_fpath = str(pickled_dir_path) + '\\' + filename + '_sheet_' + sheet_name
                print('read picked files: ', pickled_fpath)
                sheets[sheet_name] = pd.read_pickle(pickled_fpath)
            
            # if failed to read => read excel file and write pickle
            except FileNotFoundError as e:
                print('read excel files: ', path)
                sheets[sheet_name] = pd.read_excel(path, 
                                                   sheet_name=sheet_name, 
                                                   header=1, 
                                                   na_values='#### not defined ###', 
                                                   keep_default_na=False)

                pickled_fpath = str(pickled_dir_path) + '\\' + filename + '_sheet_' + sheet_name
                print('write picked files', pickled_fpath)
                sheets[sheet_name].to_pickle(pickled_fpath)
        return sheets

    def print_dtb(self, sheetname):
        df = self.sheets[sheetname].to_string()
        print(df)


    @classmethod
    def filter_ymme(cls,
                    dtb_df,
                    year=None, 
                    make=None,
                    model=None,
                    engine=None,
                    trim=None,
                    transmission=None):
        '''
        filter ymme of dtb dataframe

        CODE NOTES:
        need to add more filter for other makes  (trim, transmission, ...)
        '''
        # filter YMME
        df = dtb_df
        df = df[df['Year'].isin([str(year), year, 'N/A', ''])] if year != None else df
        df = df[df['Make'].isin([str(make), make, 'N/A', ''])] if make != None else df
        df = df[df['Model'].isin([str(model), model, 'N/A', ''])] if model != None else df

        try:
            df = df[df['Engine'].isin([str(engine), engine, 'N/A', ''])] if engine != None else df
        except KeyError as e:
            print('skip filtering engine')


        try:
            df = df[df['Trim'].isin([str(trim), trim, 'N/A', ''])] if trim != None else df
        except KeyError as e:
            print('skip filtering trim')        
        try:
            df = df[df['Transmission'].isin([str(transmission), transmission, 'N/A', ''])] if transmission != None else df
        except KeyError as e:
            print('skip filtering Transmission')  

        
        
        # filter US default
        # to-do: filter other market
        try:
            df = df[df['Market1'].isin(['v', 'V'])]
        except Exception as e:
            df = df[df['Market 1'].isin(['v', 'V'])]
        


        return df



class Obd2_Monitors(Database):
    # Contructor
    sheet_names = ['Monitors'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)

    # 10 random samples in html format
    def get_html(self):
        # filter market and get 10 samples
        ymme_df = self.sheets['Item ID']
        ymme_df = ymme_df.sample((10 if len(ymme_df) > 10 else len(ymme_df)))

        return ymme_df.to_html(index=False)





class Ymme(Database):
    # Contructor
    sheet_names = ['YMME'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)

    # 10 random samples in html format
    def get_html(self):
        # filter market and get 10 samples
        ymme_df = self.sheets['YMME']
        ymme_df = ymme_df.sample((10 if len(ymme_df) > 10 else len(ymme_df)))
        # column list to show
        cols = ['Year', 'Make', 'Model', 'Engine']
        return ymme_df.to_html(index=False)



class BatteryProcedure(Database):
    sheet_names = ['YMME', 'Procedure Type'] # list excel sheet to import
    # Contructor
    def __init__(self, path):
        Database.__init__(self, path, self.sheet_names) # call Database constructor

    # print 10 random samples
    def get_html(self):
        # get veh df and filter market
        veh_df = self.sheets['YMME']
        # get procedure
        proc_df = self.sheets['Procedure Type']

        # get all sets of procedure types and put into a df
        cols = ['General Information', 'Before Battery Disconnection', 'Before Battery Connection', 'After Battery Connection']
        temp_df = veh_df
        temp_df = temp_df[cols] # get the set of procedure types
        temp_df = temp_df.drop_duplicates(keep='first', inplace=False) # drop dups
        proc_cases_df = temp_df.sort_values(by=cols) # sort

        # iterate procedure set cases and print html
        case_count = 0
        html = ''
        for index, row in proc_cases_df.iterrows():
            case_count += 1
            cols = ['Year', 'Make', 'Model', 'Engine','General Information','Before Battery Disconnection','Before Battery Connection','After Battery Connection']

            temp_df = veh_df
            temp_df = temp_df[temp_df['General Information'] == row['General Information']]
            temp_df = temp_df[temp_df['Before Battery Disconnection'] == row['Before Battery Disconnection']]
            temp_df = temp_df[temp_df['Before Battery Connection'] == row['Before Battery Connection']]
            temp_df = temp_df[temp_df['After Battery Connection'] == row['After Battery Connection']]
            vehicle_display_list = temp_df

            html += '<br>' + '<b>' + 'CASE ' + str(case_count) + '</b>' + '<br>' 
            html += '<ul>'
            html += vehicle_display_list[cols].head(3 if len(vehicle_display_list) > 3 else len(vehicle_display_list)).to_html(index=False)
            html += '<br>'*2
            html += proc_df[proc_df['Procedure Type'].isin(list(row))].to_html(index=False)
            html += '</ul>'
            html += '<br>'*2
        
        return html.replace(r'\n','<br>')




class VinDecode(Database):
    sheet_names = [str(x) for x in range(1996, 2019)]
    #constructor
    def __init__(self, path):
        super().__init__(path, self.sheet_names)
        # concatenate all years data frames
        self.sheets['Years'] = pd.concat([self.sheets[str(x)] for x in range(1996, 2019)])
        # assign a parameter to keep the sample dtb which will be used outside

    # cnovert year number to VIN code position 10
    @staticmethod
    def convert_vin10(year):
        vin10_list = 'TVWXY123456789ABCDEFGHJK'
        year_range = [str(x) for x in range(1996,2019+1)]
        count = 0
        for x in year_range:
            if str(int(year)) == year_range[count]:
                return str(vin10_list[count])
            count += 1

    # 10 random samples in html format
    def get_html(self):

        # filter market and get sample(10)
        vin_df = self.sheets['Years'].sample(10)

        # set new index to the data frame
        new_index = [str(x) for x in range(0, len(vin_df))] # create an index column
        vin_df.insert(0, 'Index', new_index) # insert the index column
        vin_df = vin_df.set_index('Index') # set the index column

        # insert a column to contain Vin full
        vin_df.insert(len(vin_df.columns), 'VIN', '')

        # insert a column to put download button to download vin decode
        vin_df.insert(len(vin_df.columns), 'VIN Sim', '')

        # add download button html to the new column of df
        for i, row in vin_df.iterrows(): # iter rows
            # get vin full
            vin8 = row['Vin(8 First Digits)'] # get the VIN in each row
            vin10 = self.convert_vin10(row['Year'])
            vinfull = vin8 + 'F'  + vin10 + 'F'*7
            vin_df.at[i,'VIN'] = vinfull # replace the cell in new column by the html code

            new_val = download_vin_button.replace('\n','').format(val=vinfull) # html code of a download button, name = vin_num
            vin_df.at[i,'VIN Sim'] = new_val # replace the cell in new column by the html code
        
        # column list to show
        cols = ['Year', 'Make', 'Model', 'Engine', 'VIN', 'VIN Sim']
        
        # the dtb use to display as html
        self.sheets['Display'] = vin_df[cols]

        # return a df as html, escape=false means show '<', '>'
        return self.sheets['Display'].to_html(index=False, escape=False)



class FordNWS(Database):
    # Contructor
    sheet_names = ['Ymme','Profile','FordStatus'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)

    # 10 random samples in html format
    def get_html(self):
        # filter market and get 10 samples
        ymme_df = self.sheets['Item ID']
        ymme_df = ymme_df.sample((10 if len(ymme_df) > 10 else len(ymme_df)))

        return ymme_df.to_html(index=False)


class FordDTC(Database):
    # Contructor
    sheet_names = ['DTC','Ford-Sub'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)

    # 10 random samples in html format
    def get_html(self):
        # filter market and get 10 samples
        ymme_df = self.sheets['Item ID']
        ymme_df = ymme_df.sample((10 if len(ymme_df) > 10 else len(ymme_df)))

        return ymme_df.to_html(index=False)



class MazdaNWS(Database):
    # Contructor
    sheet_names = ['Ymme','Profile','FordStatus'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)

class MazdaDTC(Database):
    # Contructor
    sheet_names = ['DTC','Mazda-Sub'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)






class FormulaMissing(Exception):
    '''
    Raise this exception when formla is missing
    '''
    def __init__(self, msg):
        super().__init__(msg) 

class IncorrectInputType(Exception):
    '''
    Raise this exception when formla is missing
    '''
    def __init__(self, msg):
        super().__init__(msg) 
        

class LiveData(Database):
    '''
    LiveData class create a live data database intance and all common function 
    in livedata

    CODE NOTES:
        - make a method to check the correction of database (dupplicate item id)
        - Other makes have their own filters to get profiles and items => need to update
        - Case when profiles and items are empty
        - check the case 1 profile ID have many different item id, 
          and many different profile id use same itemid
        - check case when there is profile id but no item id
        - case HEX in TPMS ID
        - table id  có default value
        - add text translation
        - converter
        - case: byte position is more than 7 => 2 lines of cmd
        - should have a snippet to check enum when build database => if that enum not exist => drop
    '''
    # list excel sheet to import
    sheet_names = ['VehicleInfo', 'Profile ID', 'Item ID','Table ID'] 

    def __init__(self, path):
        '''
        this will create a dictionary containing all database dataframess
        calling the dataframe by <instance name>.sheets['sheet name']
        '''
        super().__init__(path, self.sheet_names)
        try:
            self.check_missing_formulas()
        except FormulaMissing as e:
            print('\n\nException while check missing formulas. Continue...\n\n')
        


    def check_missing_formulas(self):
        # formula list
        implemented_formulas = ['f(x)= x&a', 
                                'f(x)= a*x+b', 
                                'f(x)=(x+a)b',
                                'f(x) = (x/60) hrs, (x%60) min',
                                'f(x) = (x/3600) hrs, ((x%3600)/60) min',
                                'f(x)=x (HEX)',
                                'f(x)=a*x_offset_b',
                                'f(x)=ax+b',
                                'f(x)=x']

        # get list of formulas
        item_df = self.sheets['Item ID'][2:]
        formulas_df = item_df['Formula']
        imported_formulas = list(set(formulas_df))

        # check if the formula is implemented or not
        for formula in imported_formulas:
            '''
            iterate all formula in the imported list
            '''
            if formula not in implemented_formulas:
                log('class LiveData - formula missing: ' + formula)
                raise FormulaMissing('class LiveData - formula missing: ' + formula)





    def ld_calculate(self, item, *, ld_input_hex=None, ld_output_raw_dec=None):
        '''
        This method calculates input or output value depending on the paramaters
        if "ld_input_hex" transfered (must be hex value as string type):
            => output_raw and output_display will be returned

        if "ld_output" transfered:
            => input will be returned as hex number string type
            ld_output mus be raw float value
        

        CODE NOTES:
            - check sign
            - check a,b = N/A
        '''

        df = self.sheets['Item ID'].set_index('ItemID')

        formula = str(df.loc[item, 'Formula'])
        byte_size = int(df.loc[item, 'Bytesize'])
        sign = str(df.loc[item, 'Sign'])

        unit = str(df.loc[item, 'Unit(Original)'])
        unit = '' if unit in ['N/A', ''] else '( {})'.format(unit)


        a = str(df.loc[item, 'a'])
        a = None if a in ['N/A', ''] else float(Fraction(a))
        b = str(df.loc[item, 'b'])
        b = None if b in ['N/A', ''] else float(Fraction(b))


        if ld_input_hex!=None:
            if type(ld_input_hex)!=str or ('0x' in ld_input_hex):
                log('class LiveData - ld_calculate - Incorrect Input Type')
                raise IncorrectInputType(ld_input_hex)

            xhex = ld_input_hex

            # check sign, convert to int
            if sign == 'Signed': 
                xdec_temp = int(xhex, 16)
                xdec =  xdec_temp if xdec_temp >=0 else xdec_temp - (int('FF'*byte_size,16)+1)
            else:
                xdec = int(xhex, 16)

            # output
            if formula == 'f(x)= a*x+b' or formula == 'f(x)=ax+b':
                try:
                    output_raw = a*xdec + b # output is a number
                except TypeError as e:
                    output_raw = xdec
                
                output_display = str(output_raw) + unit

            elif formula == 'f(x)=(x+a)b': 
                output_raw = (xdec+a)*b # output is a number

            elif formula == 'f(x)= x&a': 
                output_raw = xdec # output is a number

            elif formula == 'f(x)=x (HEX)': 
                output_raw = xdec

            elif formula == 'f(x) = (x/60) hrs, (x%60) min': 
                output_raw = xdec

            elif formula == 'f(x) = (x/3600) hrs, ((x%3600)/60) min': 
                output_raw = xdec

            elif formula == 'f(x)=a*x_offset_b':
                output_raw = xdec*a
                if output_raw <= b:
                    output_raw = 0
                else:
                    output_raw = xdec*a

            elif formula == 'f(x)=x': 
                output_raw = xdec

            return output_raw

            #Todo: rút gọn code cho formula, kiểm tra thiếu đủ formula



        if ld_output_raw_dec!=None:
            #print(item, '--------------', ld_output_raw_dec)
            value = float(ld_output_raw_dec)

            # find x

            if formula == 'f(x)= a*x+b' or formula == 'f(x)=ax+b': 
                try:
                    x = (value - b)/a
                except TypeError as e:
                    x = value
            elif formula == 'f(x)=(x+a)b': x = value/b - a
            elif formula == 'f(x)= x&a': x = value
            elif formula == 'f(x)=x (HEX)': x = value
            elif formula == 'f(x) = (x/60) hrs, (x%60) min': x = value
            elif formula == 'f(x) = (x/3600) hrs, ((x%3600)/60) min': x = value

            elif formula == 'f(x)=a*x_offset_b': x = value/a
            elif formula == 'f(x)=x':  x = value





            print(formula)
            # check sign
            if sign == 'Signed': 
                x = x if x >= 0 else x + (int('FF'*byte_size,16)+1)

            return hex(int(x))[2:]



    def get_profiles(self,
                     year=None,
                     make=None,
                     model=None,
                     engine=None,
                     trim=None,
                     transmission=None):
        '''
        get the profile list of a vehicle
        '''

        # filter YMME
        df = self.sheets['VehicleInfo'][2:] # exclude 2 first rows
        df = Database.filter_ymme(df, year, make, model, engine, trim, transmission)

        # get profile list
        profiles = df['MsgID/ECUID/ProfileID'].to_list()
#       print('\n\nprofile list: \n', profiles)

        return profiles


    def get_items(self, profiles):
        '''
        get the item list of a vehicle
        '''
        # filter profiles
        profile_df = self.sheets['Profile ID']

        items = []
        for profile in profiles:
            df = profile_df[profile_df['MsgID/ECUID/ProfileID'].isin([profile])]
            items.extend(df['ItemID'].to_list())


        return items


    def get_item_groups(self, items):
        '''
        group items into a list which have same command
        example: groups = [[id1,id2], id3, [id4, id5], id6, id7]
        '''
        # filter items to get command list
        df = self.sheets['Item ID']
        df = df[df['ItemID'].isin(items)]

        cmds_list = []
        for item in items:
            df2 = df[df['ItemID'].isin([item])]
            cmds_list.extend(df2['GetValueCmd'].to_list())



        cmds_unique = []
        for cmd in cmds_list:
            if cmd not in cmds_unique:
                cmds_unique.append(cmd)
            else:
                continue

        print('--------------------- cmds_unique')
        print(cmds_unique)


        # create groups dict
        df = self.sheets['Item ID'].set_index('ItemID')
        groups = []
        for cmd in cmds_unique:
            temp_list = []
            for item in items:
                if df.loc[item, 'GetValueCmd']== cmd:
                    temp_list.append(item)

            groups.append(temp_list)

#       print('\n\ngroup item list: \n', groups)
        return groups



    def get_hex_from_table(self, tableid, input_val):
        '''
        get hex number from filtering table id and value
        '''
        df = self.sheets['Table ID']

        try:
            hexnum = df[(df['TableID']==tableid) & \
                        (df['TABLE_TEXT'].isin([input_val, str(input_val)]))]['HEX_VAL'] \
                        .to_list()[0].replace('0x','').replace(' ','')

        except KeyError as e:
            hexnum = 'KeyError'
            log(('class LiveData - get_hex_from_table - KeyError, \
                 tableid = {}, input_val = {}') \
                 .format(tableid, input_val))
            print(e)

        return hexnum

            
    def raw_to_readable(self, item, output_raw=None):
        print(output_raw)
        print(type(output_raw))

        '''
        convert raw value of live data into readable format to display
        output_raw can be:
            - table value text
            - dec raw value
        '''
        df = self.sheets['Item ID'].set_index('ItemID')

        formula = str(df.loc[item, 'Formula'])
        tableid = str(df.loc[item, 'TableID'])


        floating = str(df.loc[item, 'Floating'])
        floating = None if floating in ['N/A', ''] else int(floating)

        unit = str(df.loc[item, 'Unit(Original)'])
        unit = '' if unit in ['N/A', ''] else ' ({})'.format(unit)

        if tableid in ['N/A', '']: 

            # if floating is defined => round out_raw
            if floating != None: output_raw = round(output_raw, floating)
            

            if formula == 'f(x)= a*x+b' or formula == 'f(x)=ax+b': 
                output_display = str(output_raw) + unit

            elif formula == 'f(x)=(x+a)b': 
                output_display = str(output_raw) + unit

            elif formula == 'f(x)= x&a': 
                output_display = str(output_raw) + unit

            elif formula == 'f(x)=x (HEX)':

                output_display = str(hex(output_raw))[2:].upper()
                print(output_display)

            elif formula == 'f(x) = (x/60) hrs, (x%60) min': 
                output_display = '{} (hrs), {} (min)'.format(str(output_raw//60), str(round(output_raw%60,0)))

            elif formula == 'f(x) = (x/3600) hrs, ((x%3600)/60) min': 
                output_display = '{} (hrs), {} (min)'.format(str(output_raw//3600), str(round((output_raw%3600)/60,1)))
        

            elif formula == 'f(x)=a*x_offset_b': 
                output_display = str(output_raw) + unit
            elif formula == 'f(x)=x':  
                output_display = str(output_raw) + unit


        else:
            output_display = output_raw

        print(item)
        print(item, '--------------', output_display)
        return output_display



    def get_random_raw_value(self, item):
        '''
        '''

        item_df = self.sheets['Item ID'].set_index('ItemID')
        tableid = str(item_df.loc[item, 'TableID'])

        byte_size = int(item_df.loc[item, 'Bytesize'])
        bit_size = int(byte_size)*8 if str(item_df.loc[item, 'BitSize']) in ['N/A',''] else int(item_df.loc[item, 'BitSize'])

        xmin = '00'
        xmax = hex(2**bit_size-1)[2:].zfill(byte_size*2)


        if tableid in ['N/A', '']: 
            # if the PID is NOT table type
            '''
            CODE NOTE: need to add a case when min max is N/A => use byte size and bit size instead
            need to put all same pid to one command
            check if filter data frame case sensitive
            '''

            minval = str(item_df.loc[item, 'Min'])
            minval = self.ld_calculate(item, ld_input_hex=xmin) if minval in ['N/A', ''] else float(Fraction(minval))
            maxval = str(item_df.loc[item, 'Max'])
            maxval = self.ld_calculate(item, ld_input_hex=xmax) if maxval in ['N/A', ''] else float(Fraction(maxval))

            value = ((maxval - minval)/100)*random.randint(1,100) + minval

            # the value was just calculated is not exactly in the step of a bit scaling
            # need to calculate the more correct one
            x_hex = self.ld_calculate(item, ld_output_raw_dec=value)
            value = self.ld_calculate(item, ld_input_hex=x_hex)

            #if item_df.loc[item, 'Formula'] == 'f(x)=x (HEX)':
            #    value = hex(int(value))[2:].zfill(byte_size*2)

        else: 
            # if the PID is table type
            table_df = self.sheets['Table ID']


            print('--------')
            print(item)
            print(tableid)
            print('--------')

            value = table_df[(table_df['TableID']==tableid) & (table_df['HEX_VAL']!='DEFAULT')]['TABLE_TEXT'].sample(1).to_list()[0]

        return value

    def request_command(self, item):
        '''
        transfer items to this method, it will return the command of the item
        the items which is transfered to this method must have cmd
        if not, an error log will be written to "debuglog.txt"
        '''
        item_df = self.sheets['Item ID'].set_index('ItemID')
        cmd = item_df.loc[item, 'GetValueCmd']

        # CODE NOTE: phan biet CAN va Non CAN
        # tam thoi lam cho Ford, cac make khac phai co cach phan biet protocol
        cmd = clean_cmd_string(cmd)
        if cmd[0:3] == '03 ': cmd = cmd[3:].replace(' 00 00 00 00', '')
        print(cmd)
        return cmd


    def response_command(self, item, value):
        '''
        CODE NOTES:
            - handle missing formula
        '''
        # if value is not passed => get auto

        item_df = self.sheets['Item ID'].set_index('ItemID')

        total_data_size = int(item_df.loc[item, 'TotalDataSize'])
        byte_position = int(item_df.loc[item, 'BytePosition'])
        byte_size = int(item_df.loc[item, 'Bytesize'])
        bit_position = 0 if str(item_df.loc[item, 'BitPosition']) in ['N/A',''] else int(item_df.loc[item, 'BitPosition'])
        bit_size = int(byte_size)*8 if str(item_df.loc[item, 'BitSize']) in ['N/A',''] else int(item_df.loc[item, 'BitSize'])

        tableid = str(item_df.loc[item, 'TableID'])

        if tableid in ['N/A', '']: 
            # if the PID is NOT table type
            hexnum = self.ld_calculate(item, ld_output_raw_dec=value)
            
        else: 
            # if the PID is table type
            hexnum = self.get_hex_from_table(tableid, value)
            hexnum = self.ld_calculate(item, ld_output_raw_dec=int(hexnum,16))

        hexnum = hex((int(hexnum,16)<<int(bit_position)))[2:].zfill(byte_size*2) + '00'*(total_data_size-(byte_size+byte_position))


        data = '00 '*byte_position
        for i in range(1, len(hexnum)+1):
            if i%2 == 0:
                data += ' ' + hexnum[i-2:i]



        sid = clean_cmd_string(item_df.loc[item, 'GetValueCmd'])
        if sid[0:2] == '01':
            #OBDII
            sid = sid.replace('01','41')
        else:

            # Ford
            ## CODE NOTE: phan biet CAN va Non CAN
            # tam thoi lam cho Ford, cac make khac phai co cach phan biet protocol
            sid = sid.replace('22','62')
            if sid[0:3] == '03 ': sid = sid[3:]

        cmd = concat_cmds(sid, data)

        return cmd


    def get_all(self,
                year=None,
                make=None,
                model=None,
                engine=None,
                trim=None,
                transmission=None):
        '''
        get the profile list of a vehicle
        '''
        item_df = self.sheets['Item ID'].set_index('ItemID')

        profiles = self.get_profiles(year, make, model, engine, trim, transmission)
        items = self.get_items(profiles)
        item_groups = self.get_item_groups(items)

        data_d = {}
        data_d['profiles'] = profiles
        data_d['items'] = items
        data_d['item_groups'] = item_groups
        

        '''
        TO-DO:
            - add more information to the simulation file
              profile, system, protocol, pins
        '''

        item_infor = {}
        for item in items:
            try:
                raw_value = self.get_random_raw_value(item)
                readable_value = self.raw_to_readable(item, raw_value)

                req_cmd = self.request_command(item)
                res_cmd = self.response_command(item, raw_value)

                item_infor[item]=[]
                item_infor[item].append(item)
                item_infor[item].append(item_df.loc[item,'ItemDescription'])
                item_infor[item].append(readable_value)
                item_infor[item].append(item_df.loc[item,'Unit(Original)'])
                item_infor[item].append(req_cmd)
                item_infor[item].append(res_cmd)
            except Exception as e:
                raise e
                print('\n\n' + str(e) + '\n\n')
                item_infor[item]=[]
                item_infor[item].append(item)
                item_infor[item].append(item_df.loc[item,'ItemDescription'])
                item_infor[item].append('Error! Please check')
                item_infor[item].append(item_df.loc[item,'Unit(Original)'])
                item_infor[item].append('Error! Please check')
                item_infor[item].append('Error! Please check')



        data_d['item_infor'] = item_infor
        return data_d

'''                                                                        
====================================================================================================
====================================================================================================
====================================================================================================
'''
class FordLiveData(LiveData):
    '''
    FordLiveData class to create an instance of Ford LD Database inherited 
    variables and methods from class LiveData
    '''
    def __init__(self, path):
        super().__init__(path)


'''                                                                        
====================================================================================================
====================================================================================================
====================================================================================================
'''
class MazdaLiveData(LiveData):
    '''
    FordLiveData class to create an instance of Ford LD Database inherited 
    variables and methods from class LiveData
    '''
    def __init__(self, path):
        super().__init__(path)


'''                                                                        
====================================================================================================
====================================================================================================
====================================================================================================
'''
class LiveDataOBD2(LiveData):
    '''
    LiveDataJ1979 class to create an instance of OBDII LD Database inherited 
    variables and methods from class LiveData
    '''
    # Contructor
    def __init__(self, path):
        super().__init__(path)

    def get_support_cmds(self, item):

        # CODE NOTE: phan biet CAN va Non CAN
        # tam thoi lam cho Ford, cac make khac phai co cach phan biet protocol
        

        profile_df = self.sheets['Profile ID'].set_index('ItemID')
        req = clean_cmd_string(profile_df.loc[item, 'SupReQ1'])

        sid = req.replace('01','41')

        byte_size = int(profile_df.loc[item, 'SupByteSize1'])
        bit_size = int(profile_df.loc[item, 'SupBitSize1'])
        byte_position = int(profile_df.loc[item, 'SupBytePos1'])
        bit_position = int(profile_df.loc[item, 'SupBitPos1'])
        total_data_size = 6




        hexnum = '01'
        hexnum = hex((int(hexnum,16)<<int(bit_position)))[2:].zfill(byte_size*2) + '00'*(total_data_size-(byte_size+byte_position))

        data = '00 '*byte_position
        for i in range(1, len(hexnum)+1):
            if i%2 == 0:
                data += ' ' + hexnum[i-2:i]

        res = concat_cmds(sid, data)

        return req, res







'''


def convert_unit(value, floating, converter_id):
    value = float(value)

    if converter_id=='UnitConvertID_0001':
        return str(round(value*9/5+32, floating)) + ' (°F)'

    elif converter_id=='UnitConvertID_0002':
        return str(round(value*0.145037738, floating + 1)) + ' (psi)'

    elif converter_id=='UnitConvertID_0003':
        return str(round(value*0.295333727, floating + 1)) + ' (inHg)'

    elif converter_id=='UnitConvertID_0004':
        return str(round(value*0.621371192, floating + 1)) + ' (mph)'

    elif converter_id=='UnitConvertID_0005':
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'

    elif converter_id=='UnitConvertID_0006':
        return str(round(value*0.621371192, floating + 1)) + ' (miles)'

    elif converter_id=='UnitConvertID_0007':
        return str(round(value*0.00401463078662309, floating + 3)) + ' (InH2O)'

    elif converter_id=='UnitConvertID_0008':
        return str(round(value*4.01474213311, floating)) + ' (InH2O)'

    elif converter_id=='UnitConvertID_0009':
        return str(round(value*0.737562149277, floating + 1)) + ' (lbf ft)'

    elif converter_id=='UnitConvertID_0010':
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 kilogram/hour  =  0.0006123952 pound/second
    
    elif converter_id=='UnitConvertID_0011'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 bar = 14.5037738 pounds per square inch
    elif converter_id=='UnitConvertID_0012'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 Mpa = 145 psi
    elif converter_id=='UnitConvertID_0013'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 centimeter = 0.393700787 inches
    elif converter_id=='UnitConvertID_0014'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 kilogram = 2.20462262 lbs
    elif converter_id=='UnitConvertID_0015'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 kW = 1.34 hp 
    elif converter_id=='UnitConvertID_0016'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 liter = 61.0237441 cubic inches
    elif converter_id=='UnitConvertID_0017'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 gram = 0.00220462262 pounds
    elif converter_id=='UnitConvertID_0018'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 l / kilometer = 2.35214583 Miles per gallon
    elif converter_id=='UnitConvertID_0019'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 l / kilometer = 0.425143707 US gallons / mile
    elif converter_id=='UnitConvertID_0020'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 l/s = 15.850372483753 US gpm
    elif converter_id=='UnitConvertID_0021'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 liter = 0.264172052 US gallons
    elif converter_id=='UnitConvertID_0022'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 pound = 0.45359237 kilograms
    elif converter_id=='UnitConvertID_0023'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 meter = 3.2808399 feet
    elif converter_id=='UnitConvertID_0024'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 m/s² = 3.2808399 ft/s²
    elif converter_id=='UnitConvertID_0025'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 g = 32.174049 ft/s2
    elif converter_id=='UnitConvertID_0026'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 millimeter = 0.0393700787 inches
    elif converter_id=='UnitConvertID_0027'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 ml = 0.0610237441 cubic inches
    elif converter_id=='UnitConvertID_0028'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 cubic millimeter = 6.10237441 × 10-5 cubic inches
    elif converter_id=='UnitConvertID_0029'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 mile per hour = 1.46666667 feet / second
    elif converter_id=='UnitConvertID_0030'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 Mpa = 145 psi (lbf/in2) 
    elif converter_id=='UnitConvertID_0031'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 N = 0.2248 lb
    elif converter_id=='UnitConvertID_0032'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        1 l = 0.0353146667 cubic feet
    elif converter_id=='UnitConvertID_0033'
        return str(round(value*0.132277357, floating + 1)) + ' (lb/min)'        (1 l) / h = 0.264172052 gal / h










'''