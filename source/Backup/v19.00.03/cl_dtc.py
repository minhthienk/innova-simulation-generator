import pandas as pd


class Dtc :
    'DTC database class'
    
    # Contructor
    def __init__(self, dtc_path):
        try:
            self.dtc_df = pd.read_pickle('dtc_df')
            self.dtc_translate_df = pd.read_pickle('dtc_translate_df')

        except FileNotFoundError as e:
            self.dtc_path= dtc_path
            self.dtc_df = pd.read_excel(self.dtc_path, sheet_name='DTC', header = 1) 
            self.dtc_translate_df = pd.read_excel(self.dtc_path, sheet_name='CodeDescription', header = 1) 
            self.dtc_df.to_pickle('dtc_df')
            self.dtc_translate_df.to_pickle('dtc_translate_df')

    # print 5 first rows
    def printTest(self):
        print(self.dtc_df.head(5)[['Year', 'Manufacturer', 'Model', 'Option 1', 'System', 'Protocol', 'Option 3', 'Option 4', 'SAE DTC', 'CodeDescription-English']].to_string())

    def printHtmlTest(self):
        print(self.dtc_df.head(5)[['Year', 'Manufacturer', 'Model', 'Option 1', 'System', 'Protocol', 'Option 3', 'Option 4', 'SAE DTC', 'CodeDescription-English']].to_html())


