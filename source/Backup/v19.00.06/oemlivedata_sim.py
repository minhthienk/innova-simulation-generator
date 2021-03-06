import sys


from common.databases import FordLiveData, Database
from common.mypaths import *

#fordld = FordLiveData(ford_telematics_fp)
#
#
#year = 2007
#make = 'Ford'
#model = 'Focus'
#
#sys.exit()


# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)


'''
CODE NOTES:
	- nhóm items lại
	- bỏ vô simulate
'''


from common.simulation import *

ymme_dict = {'name':'Demo name', 'year':2017, 'make':'Ford', 'model':'Focus', 'engine':'L4, 2.0L'}

fordsim = FordSimulation(ymme_dict)

simdata = fordsim.create_livedata(ford_tpms_ld_fp)

path = str(simulation_dir_path) + '\\' + ymme_dict['name'] + '.sim'
write_data(path, simdata)

print(simdata)

input()


#ford_chassis_ld_fp
#ford_body_ld_fp
#ford_telematics_fp
#ford_abs_ld_fp
#ford_srs_ld_fp
#ford_ecm_ld_fp
#ford_tcm_ld_fp
#ford_becm_ld_fp
#ford_dcdc_ld_fp
#ford_tpms_ld_fp





#ymme_dict = {'name': '-----------------', 'year': 2012,
#             'make': 'Mazda', 'model': 'CX-7', 'engine': 'L4, 2.3L'}
#
#mazdasim = MazdaSimulation(ymme_dict)
#a = mazdasim.create_livedata(mazda_chassis_ld_fp)

