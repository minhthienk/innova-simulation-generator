
from common.simulation import *

ymme_dict = {'name':'2008 Ford Edge', 'year':2008, 'make':'Ford', 'model':'Edge', 'engine':'V6, 3.5L'}

fordsim = FordSimulation(ymme_dict)
fordsim.create_sim_file()