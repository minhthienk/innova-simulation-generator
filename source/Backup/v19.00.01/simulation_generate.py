from simulation_source import *
from path_management import *



# write data to a file, overwrite mode
def write_data(path, data):
    with open(path, "w") as file_object:
        file_object.write(data)


# read data from a file
def read_data(path):
    with open(path, "r") as file_object:
        return file_object.read()
    return 


def vin2hex(vin_ascii):
    vin_hex = []
    for c in vin_ascii:
        vin_hex.append(hex(ord(c))[2:])
    return vin_hex


def create_obd2(vehicle_name, vin='F'*17):
    vin = str(vin).replace(' ', '')
    if len(vin) != 17:
        print('Simulation created failed')
        return False

    simdata = (
        can614500_config +
        obd2_mode1 +
        obd2_mode37A +
        obd2_mode2 +
        obd2_mode9.format(*vin2hex(vin)))

    path = str(simulation_dir_path) + '\\' + vehicle_name
    write_data(path, simdata)
    print('Simulation created successfully')
    return True