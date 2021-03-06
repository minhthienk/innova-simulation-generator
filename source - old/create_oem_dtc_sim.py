



try:
    from common.simulation import *


    ymme_dict = {'name':'2018 Lincoln MKC L4, 2.0L', 'year':2018, 'make':'Lincoln', 'model':'MKC', 'engine':'L4, 2.0L'}

    fordsim = FordSimulation(ymme_dict)
    fordsim.create_sim_file()


except Exception as e:
    print(e)


