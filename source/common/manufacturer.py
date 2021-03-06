import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy



import cls_databases
import pandas as pd
from path_management import *



class VehicleManufacturer:
    def __init__(self, make):
        self.ymme = cls_databases.Ymme(ymme_path[make])
        self.battery_procedure = cls_databases.BatteryProcedure(battery_reset_path[make])
        self.vin = cls_databases.VinDecode(vin_path[make])



ford = VehicleManufacturer('ford')























#while 1:
#    # print 10 random samples
#    print('\n***** 10 random YMME *****')
#    print(us_ymme_df.sample(5)[['Year', 'Make', 'Model', 'Engine']].to_string())
#
#    # loop for typing control string
#    while 1:
#        print('\nType: \n    "redo" to retest \n    "pass" to exit')
#        print('Your control: ', end='')
#        control_string = input()
#
#        if control_string == 'pass' or control_string == 'redo': 
#            break
#
#    if control_string == 'pass':
#        break
#    elif control_string == 'redo':
#        continue
        
    



