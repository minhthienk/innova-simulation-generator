# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)



import sys
from common.databases import FordLiveData, Database
from common.mypaths import *
from common.simulation import *


ymme_dict = {'name':'2011 Ford Fiesta', 'year':2011, 'make':'Ford', 'model':'Fiesta', 'engine':'L4, 1.6L'}



#ymme_dict['name'] = 'NWS 2017 Ford Fusion'
#fordsim = FordSimulation(ymme_dict)
#fordsim.create_sim_file()

#1.  2012 Mazda CX-7 L4, 2.3L ====JM3ER4D3XC1108239
#2. JM3KFADL9H0137846_2017 Mazda CX-5 L4, 2.5L
#3.  2008 Mazda Tribute L4, 2.3L 4F2CZ92Z58KM16614


paths = {}
paths['ABS'] = ford_abs_ld_fp
paths['SRS'] = ford_srs_ld_fp
paths['TPMS'] = ford_tpms_ld_fp
#paths['Telematics'] = mazda_telematics_fp

for name, path in paths.items():
	ymme_dict['name'] = 'LD {} 2011 Ford Fiesta'.format(name)
	fordsim = FordSimulation(ymme_dict)
	simdata = fordsim.create_livedata(path)
	path = str(simulation_dir_path) + '\\' + ymme_dict['name'] + '.sim'
	write_data(path, simdata)
	print(simdata)







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



