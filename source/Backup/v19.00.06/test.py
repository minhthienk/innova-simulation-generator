
from sys import exit
from unit_converter.converter import convert, converts


a = convert('2.78 daN*mm^2', 'mN*µm^2')

print(float(a))
exit()





output_raw = 50.5
a = round(output_raw,0)

print(a)
exit()

from common.mypaths import *

from fractions import Fraction

from common.simulation import *

from common.databases import *


#ford_ld = LiveDataOBD2(obd2_ld_fp)



#temp = ford_ld.check_missing_formulas()

#temp1 = ford_ld.ld_calculate('OBD2_0271', ld_input_hex='2fff')
#print(temp1)
#
#temp2 = ford_ld.ld_calculate('OBD2_0271', ld_output_raw_dec=temp1[0])
#print(temp2)
#
#temp3 = ford_ld.request_command('OBD2_0271')
#print(temp3)
#
#temp5 = ford_ld.auto_select_item_value('OBD2_0429')
#print(temp5)
#
#temp4 = ford_ld.response_command('OBD2_0429', temp5)
#print(temp4)
#
#temp6 = ford_ld.get_all()
#print(temp6)
#
#temp = ford_ld.get_support_cmds('OBD2_0001')
#print(temp)
#
#exit()

obd2 = Obd2Simulation()

#temp = obd2.create_obd2_mode09()
#print(temp)
#
#temp = obd2.create_obd2_dtcs(mode='0A')
#print(temp)
#
#temp = obd2.create_obd2_monitors()
#print(temp)






ld_inputs={'itemid_auto_setting':'03-06'}

temp = obd2.create_obd2_ld_support(ld_inputs)
print(temp)

temp = obd2.create_obd2_ld(ld_inputs)
print(temp)



