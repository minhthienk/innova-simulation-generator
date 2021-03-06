from cls_databases import *
cols = ['Year','Make','Model','Engine','Market1','Market2']
ford = Manufacturer('ford')
print(ford.dtbs['ymme'].sheets['YMME'][cols])
print(ford.filter_market('VN').dtbs['ymme'].sheets['YMME'][cols].sample(50))




#class Manufacturer:
#    def __init__(self, mfr):
#        self.dtbs = {'a':'aaaa','b':'bbbbb'}
#
#    # filter market
#    def filter_market(self, market):
#        # iterate all dtbs
#        for dtb_key, dtb in self.dtbs.items():
#            temp = self.dtbs
#            temp[dtb_key] = 'cccccccccc'
#        return self
#
#ford = Manufacturer('ford')
#print(ford.dtbs)
#print(ford.filter_market('VN').dtbs)




