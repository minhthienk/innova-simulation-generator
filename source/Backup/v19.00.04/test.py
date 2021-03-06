def put_bytebit(data, bytepos, bitpos, mode):
    bytepos = int(bytepos)
    bitpos = int(bitpos)
    if bytepos > len(data) - 1: # if bytepos > the max pos
        data.extend(['00' for x in range(0, bytepos-len(data) + 1)])

    if mode=='set':
        data[bytepos] = format(int(data[bytepos], 16)|(1<<bitpos), '02x')

    return data

a = put_bytebit(['41','01'], 3, 5, mode='noset')

print(a)