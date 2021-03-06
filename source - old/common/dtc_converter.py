def check_dtc_format(dtc):
    count = 0
    dtc = str(dtc)
    for c in dtc:
        count += 1
        if count==1:
            if c not in ['P','B','C','U','p','b','c','u']:
                return False
        elif count==6:
            return False
        else:
            try:
                int(c, 16)
            except Exception as e:
                return False
    return True



def check_hex_format(hexnum):
    count = 0
    hexnum = str(hexnum).replace(' ', '')

    if len(hexnum) > 4:
        return False

    try:
        int(hexnum, 16)
    except Exception as e:
        return False

    return True


class IncorrectHexNumberFormat(Exception):
    """docstring for IncorrectHexNumberFormat"""
    def __init__(self):
        super().__init__()
        
class IncorrectDtcFormat(Exception):
    """docstring for IncorrectHexNumberFormat"""
    def __init__(self):
        super().__init__()

def hex2dtc(hexnum):

    hexnum = str(hexnum).replace(' ', '')

    if check_hex_format(hexnum) == False:
        raise IncorrectHexNumberFormat
    
    part1 = hexnum[0:1]
    part2 = hexnum[1:4]

    part1_bin = bin(int(part1, 16))[2:]
    part1_bin = '0'*(4-len(part1_bin)) + str(part1_bin)


    firt_code_bin = str(part1_bin[0:2])

    if firt_code_bin == "00":
        firt_code_hex = "P"
    elif firt_code_bin == "01":
        firt_code_hex = "C"
    elif firt_code_bin == "10":
        firt_code_hex = "B"
    elif firt_code_bin == "11":
        firt_code_hex = "U"

    second_code_bin = str(part1_bin[2:4])

    second_code_hex = hex(int(second_code_bin, 2))[2:5]

    return firt_code_hex + second_code_hex + part2



def dtc2hex(dtc):
    if check_dtc_format(dtc) == False:
        raise IncorrectDtcFormat

    part1 = dtc[0:1]
    part2 = dtc[1:2]
    part3 = dtc[2:3] + " " + dtc[3:5]

    data1 = ""
    if part1 == "P" or part1 == "p":
        data1 = "00"
    elif part1 == "C" or part1 == "c":
        data1 = "01"
    elif part1 == "B" or part1 == "b":
        data1 = "10"
    elif part1 == "U" or part1 == "u":
        data1 = "11"

    data2 = ""
    if part2 == "0":
        data2 = "00"
    elif part2 == "1":
        data2 = "01"
    elif part2 == "2":
        data2 = "10"
    elif part2 == "3":
        data2 = "11"
    else:
        return "Error: DTC format. Please check!"

    dtc_byte = hex(int(data1 + data2, 2))[2:5] + part3
    return dtc_byte

