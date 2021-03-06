from common.path_management import *
from common.databases import Obd2_Monitors, LiveDataJ1979, FordNWS, FordDTC
from fractions import Fraction
from sys import exit

from pandas import DataFrame

import random


sign = 'signed'
byte_size = 1
x = -128
if sign == 'signed': x = x if x >= 0 else x + (int('FF'*byte_size,16)+1)
print(x)
exit()




j1979_ld_db = LiveDataJ1979(j1979_ld_path)
item_df = j1979_ld_db.sheets['Item ID']

item_df = item_df[item_df['GetValueCmd']=='01 0F']
print(item_df)
exit()


print(j1979_ld_db.response_command('OBD2_0001','OL'))#


class ClassName(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(ClassName, self).__init__()
		self.arg = arg
		