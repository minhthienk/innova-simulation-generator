
import pandas as pd
from pathlib import Path
from common.path_management import *
from common.log_writer import *

from fractions import Fraction
import numpy as np

pd.set_option('display.max_colwidth', 99999)
pd.set_option('display.max_columns', 20)
pd.options.display.float_format = '{:.0f}'.format


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
                sheets[sheet_name] = pd.read_excel(path, sheet_name=sheet_name, header = 1)

                pickled_fpath = str(pickled_dir_path) + '\\' + filename + '_sheet_' + sheet_name
                print('write picked files', pickled_fpath)
                sheets[sheet_name].to_pickle(pickled_fpath)
        return sheets







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


class LiveDataJ1979(Database):
    '''
    CODE NOTE
    Cần check thêm trường hợp table value là N/A, hex = default
    Cần tạo command được gọp lại từ nhiều PID cùng command
    Tính Total datasize từ các PID cùng command
    #Kiểm tra tính hợp lệ của byte bite trong database
    #Check trường hợp khoảng trắng dư trong getcmdvalue
    check lại công thức Signed and unsigned
    '''
    # Contructor
    sheet_names = ['VehicleInfo','Profile ID','Item ID','Table ID','Text Translation'] # list excel sheet to import
    def __init__(self, path):
        super().__init__(path, self.sheet_names)
        self.sheets['Item ID'] = self.sheets['Item ID']#.set_index('ItemID')


    def request_command(self, itemid):
        df = self.sheets['Item ID']
        #cmd = df.loc[itemid, 'GetValueCmd']
        cmd = df[df['ItemID']==itemid]['GetValueCmd'].to_list()[0]
        return cmd

    def response_command(self, itemid, value):
        item_df = self.sheets['Item ID']

        formula_lst = ['f(x)= x&a', 
                      'f(x)= a*x+b', 
                      'f(x) = (x/60) hrs, (x%60) min', 
                      'f(x) = (x/3600) hrs, ((x%3600)/60) min']

        formula = item_df[item_df['ItemID']==itemid]['Formula'].to_list()[0]
        tableid = item_df[item_df['ItemID']==itemid]['TableID'].to_list()[0]
        total_data_size = int(item_df[item_df['ItemID']==itemid]['TotalDataSize'].to_list()[0])
        byte_position = int(item_df[item_df['ItemID']==itemid]['BytePosition'].to_list()[0])
        byte_size = int(item_df[item_df['ItemID']==itemid]['Bytesize'].to_list()[0])
        bit_position = 0 if isinstance(item_df[item_df['ItemID']==itemid]['BitPosition'].to_list()[0], float) else int(item_df[item_df['ItemID']==itemid]['BitPosition'].to_list()[0])
        bit_size = int(byte_size)*8 if isinstance(item_df[item_df['ItemID']==itemid]['BitSize'].to_list()[0], float) else int(item_df[item_df['ItemID']==itemid]['BitSize'].to_list()[0])
        sign = item_df[item_df['ItemID']==itemid]['Sign'].to_list()[0]

        a = str(item_df[item_df['ItemID']==itemid]['a'].to_list()[0])
        a = None if a == 'nan' else float(Fraction(a))
        b = str(item_df[item_df['ItemID']==itemid]['b'].to_list()[0])
        b = None if b == 'nan' else float(Fraction(b))

        if isinstance(tableid, float): 
        # if the PID is NOT table type
            value = float(Fraction(value))

            if formula in formula_lst:

                if formula == 'f(x)= a*x+b':
                    # get raw x value then check sign
                    x = (value - b)/a
                    if sign == 'Signed': 
                        print('Before: ' + itemid + '    ' + str(x))
                        x = x if x >= 0 else x + (int('FF'*byte_size,16)+1)
                        print('After: ' + itemid + '    ' + str(x))

 
                    hexnum = hex(int(x)).replace('0x','')

            else:
                write_missing_enum('LiveDataJ1979 fomula: ' + formula)
                hexnum = 'Sorry The Formula Is Not Yet Implemented'
        else: 
        # if the PID is table type
            if formula in formula_lst:
                if formula == 'f(x)= x&a':
                    table_df = self.sheets['Table ID']
                    try:
                        # filter => get HEX_VAL col => get list of 1 item => get first string => dop '0x'
                        hexnum = table_df[(table_df['TableID']==tableid) & (table_df['TABLE_TEXT']==value)]['HEX_VAL'].to_list()[0].replace('0x','').replace(' ','')

                    except KeyError as e:
                        hexnum = 'KeyError'
                        print(e)
                    
            else:
                write_missing_enum('LiveDataJ1979 fomula: ' + formula)
                hexnum = 'Sorry The Formula Is Not Yet Implemented'

        hexnum = hex((int(hexnum,16)<<int(bit_position)))[2:].zfill(byte_size*2) + '00'*(total_data_size-(byte_size+byte_position))


        value_data_list = ['00']*byte_position
        for i in range(0, len(hexnum)):
            if i%2 == 0 and i != len(hexnum):
                value_data_list.append(hexnum[i:i+2])

        sid = item_df[item_df['ItemID']==itemid]['GetValueCmd'].to_list()[0].replace('01','41')
        sid_data_list = sid.split()
        
        cmd = ' '.join(LiveDataJ1979.unique_data_lists(value_data_list, sid_data_list))

        return cmd

    def unique_data_lists(list1, list2):
        unique_list = []
        maxlen = len(list1) if len(list1)>len(list2) else len(list2)
        for x in range(0, maxlen):


            print('list1[x] = ', list1[x] if x <= (len(list1)-1) else 0, ' ---- ',  'list2[x] = ', list2[x] if x <= (len(list2)-1) else 0)



            a = int(list1[x],16) if x <= (len(list1)-1) else 0
            b = int(list2[x],16) if x <= (len(list2)-1) else 0
            unique_list.append(hex(a|b)[2:].zfill(2))
        return unique_list





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