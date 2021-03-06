import pandas as pd
from path_management import *
from pathlib import Path
from html_source import *

pd.set_option('display.max_colwidth', 99999)
pd.options.display.float_format = '{:.0f}'.format


class VehicleManufacturer:
    def __init__(self, mfr):
        self.ymme = Ymme(ymme_path[mfr])
        self.battery_procedure = BatteryProcedure(battery_reset_path[mfr])
        self.vin = VinDecode(vin_path[mfr])



class Database:
    # Contructor
    def __init__(self, path, sheets):
        self.database = self.load_database(path, sheets) # a dict to contain all sheets data frame

    # load database from excel or pickle files
    @staticmethod
    def load_database(path, sheets):
        # create data frames from pickle files if not create pickle files
        database = {}
        filename = Path(path).stem # get file name of ymme path
        for sheet in sheets:
            #print('Processing ' + filename + '_sheet_' + sheet)
            # read pickle data of ymme database (sheet ymme)
            try: 
                database[sheet] = pd.read_pickle(str(pickled_dir_path) + '\\' + filename + '_sheet_' + sheet)
            
            # if failed to read => read excel file and write pickle
            except FileNotFoundError as e:
                database[sheet] = pd.read_excel(path, sheet_name=sheet, header = 1)
                database[sheet].to_pickle(str(pickled_dir_path) + '\\' + filename + '_sheet_' + sheet)
        return database

    # filter market
    @staticmethod
    def filter_market(df, market):
        # iterate all columns to determine which column is the assigned market
        for col in df.columns:
            if df[col].values[1] == market:
                market_filter = col
        
        # filter market
        df = df[df[market_filter]=='v']
        return df



class Ymme(Database):
    # Contructor
    def __init__(self, path):
        sheets = ['YMME'] # list excel sheet to import
        super().__init__(path, sheets)
        self.a = '123'

    # 10 random samples in html format
    def get_html(self, market):
        # filter market and get 10 samples
        ymme_df = self.filter_market(self.database['YMME'], market).sample(10)
        # column list to show
        cols = ['Year', 'Make', 'Model', 'Engine']
        return ymme_df[cols].to_html(index=False)




class BatteryProcedure(Database):
    # Contructor
    def __init__(self, path):
        sheets = ['YMME', 'Procedure Type'] # list excel sheet to import
        Database.__init__(self, path, sheets) # call Database constructor

    # print 10 random samples
    def get_html(self, market):
        # get veh df and filter market
        veh_df = self.filter_market(self.database['YMME'], market)
        # get procedure
        proc_df = self.database['Procedure Type']

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
    #constructor
    def __init__(self, path):
        sheets = [str(x) for x in range(1996, 2019)]
        super().__init__(path, sheets)

        # concatenate all years data frames
        self.database['Years'] = pd.concat([self.database[str(x)] for x in range(1996, 2019)])
        # assign a parameter to keep the sample database which will be used outside
        self.database_display = {}

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
    def get_html(self, market):

        # filter market and get sample(10)
        vin_df = self.filter_market(self.database['Years'], market).sample(10)

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
        
        # the database use to display as html
        self.database_display['main'] = vin_df[cols]

        # return a df as html, escape=false means show "<", ">"
        return self.database_display['main'].to_html(index=False, escape=False)


