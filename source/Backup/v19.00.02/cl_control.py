
class Control:
    'control class'
    

    def __init__(self, ymme_path):
        self.ymme_path= ymme_path
        self.ymme_df = pd.read_excel(self.ymme_path, sheet_name='YMME', header = 1)       
        self.us_ymme_df = self.ymme_df[self.ymme_df.Market1 == 'v']
    
    # print 5 first rows
    def printTest(self):
        print(self.us_ymme_df.head(5)[['Year', 'Make', 'Model', 'Engine']].to_string())

    # print 10 random samples
    def printSample(self, num):
        print('\n***** 10 random YMME *****')
        print(self.us_ymme_df.sample(5)[['Year', 'Make', 'Model', 'Engine']].to_string())



