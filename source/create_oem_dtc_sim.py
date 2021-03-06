try:
    from common.simulation import *


    ymme_dict = {'name':'  aaa', 'year':2018, 'make':'Ford', 'model':'Explorer', 'engine':'V6, 3.5L'}

    fordsim = FordSimulation(ymme_dict)
    fordsim.create_sim_file()


except Exception as e:
    print(e)


input()