try:
    from common.simulation import *


    ymme_dict = {'name':'  aaa', 'year':2010, 'make':'Ford', 'model':'Fusion', 'engine':'L4, 2.5L'}

    fordsim = FordSimulation(ymme_dict)
    fordsim.create_sim_file()


except Exception as e:
    print(e)


input()