import time
import Adafruit_GPIO.I2C as i2c
import subprocess
from bitstring import BitArray

dev = i2c.Device(0x76,1)

t_fine = 0

def process(data):

        data = str(data)

        temp = data.split(",")[7]

        temp = temp.split(":")[1]

        temp = temp.split()

        return ([int(x,16) for x in temp[0:8]])

def toBin(val):

        temp = list(bin(val).replace("0b",""))

        for i in range(len(temp),8):

                temp.insert(0,"0")

        return ''.join(temp)

def compensateT(adc_T):

        global t_fine

        adc_T = float(adc_T)

        var1 = ((adc_T/16384.0) - (dig_T1/1024.0)) * dig_T2

        var2 = (((adc_T/131072.0) - (dig_T1/8192.0)) * ((adc_T/131072.0) - (dig_T1/8192.0))) * dig_T3

        t_fine = (var1+var2)

        T = (var1+var2)/5120.0

        return T

def compensateP(adc_P):

    adc_P = float(adc_P)

    var1 = (t_fine/2.0) - 64000.0

    var2 = var1*var1 * (dig_P6) / 32768.0

    var2 = var2 + var1 * dig_P5 * 2.0

    var2 = (var2/4.0)+(dig_P4 * 65536.0)

    var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0

    var1 = (1.0+var1/32768.0)*dig_P1

    if(var1==0.0):

        return 0

    p = 1048576.0 - adc_P

    p = (p-(var2/4096.0)) * 6250.0 / var1

    var1 = dig_P9 * p * p / 2147483648.0

    var2 = p * dig_P8 / 32768.0

    p = p + (var1+var2 + dig_P7) / 16.0

    return p

def compensateH(adc_H):

    var_H = t_fine-76800.0

    var_H = (adc_H - (dig_H4 * 64.0 + dig_H5 / 16384.0 * var_H)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * var_H * (1.0 + dig_H3 / 67108864.0 * var_H)))

    var_H = var_H * (1.0 - dig_H1 * var_H / 524288.0)

    if(var_H > 100.0):

        var_H = 100.0

    elif(var_H < 0.0):

        var_H = 0.0

    return var_H

# assign trimming parameters values

dig_T1 = toBin(dev.readU8(0x89))+toBin(dev.readU8(0x88))

dig_T2 = toBin(dev.readU8(0x8B))+toBin(dev.readU8(0x8A))

dig_T3 = toBin(dev.readU8(0x8D))+toBin(dev.readU8(0x8C))

dig_T1 = float(BitArray(bin=dig_T1).uint)

dig_T2 = float(BitArray(bin=dig_T2).int)

dig_T3 = float(BitArray(bin=dig_T3).int)


dig_P1 = toBin(dev.readU8(0x8F))+toBin(dev.readU8(0x8E))

dig_P2 = toBin(dev.readU8(0x91))+toBin(dev.readU8(0x90))

dig_P3 = toBin(dev.readU8(0x93))+toBin(dev.readU8(0x92))

dig_P4 = toBin(dev.readU8(0x95))+toBin(dev.readU8(0x94))

dig_P5 = toBin(dev.readU8(0x97))+toBin(dev.readU8(0x96))

dig_P6 = toBin(dev.readU8(0x99))+toBin(dev.readU8(0x98))

dig_P7 = toBin(dev.readU8(0x9B))+toBin(dev.readU8(0x9A))

dig_P8 = toBin(dev.readU8(0x9D))+toBin(dev.readU8(0x9C))

dig_P9 = toBin(dev.readU8(0x9F))+toBin(dev.readU8(0x9E))

dig_P1 = float(BitArray(bin=dig_P1).uint)

dig_P2 = float(BitArray(bin=dig_P2).int)

dig_P3 = float(BitArray(bin=dig_P3).int)

dig_P4 = float(BitArray(bin=dig_P4).int)

dig_P5 = float(BitArray(bin=dig_P5).int)

dig_P6 = float(BitArray(bin=dig_P6).int)

dig_P7 = float(BitArray(bin=dig_P7).int)

dig_P8 = float(BitArray(bin=dig_P8).int)

dig_P9 = float(BitArray(bin=dig_P9).int)


# Humidity values

dig_H1 = toBin(dev.readU8(0xA1))

dig_H2 = toBin(dev.readU8(0xE2))+toBin(dev.readU8(0xE1))

dig_H3 = toBin(dev.readU8(0xE3))

dig_E5_temp = toBin(dev.readU8(0xE5))

e5_1 = dig_E5_temp[:len(dig_E5_temp)//2]

e5_2 = dig_E5_temp[len(dig_E5_temp)//2:]

dig_H4 = toBin(dev.readU8(0xE4))+e5_1

dig_H5 = toBin(dev.readU8(0xE6))+e5_2

dig_H6 = toBin(dev.readU8(0xE7))

dig_H1 = float(BitArray(bin=dig_H1).uint)

dig_H2 = float(BitArray(bin=dig_H2).int)

dig_H3 = float(BitArray(bin=dig_H3).uint)

dig_H4 = float(BitArray(bin=dig_H4).int)

dig_H5 = float(BitArray(bin=dig_H5).int)

dig_H6 = float(BitArray(bin=dig_H6).int)

while(True):

        temp = subprocess.run(["i2cdump","-y","-r","0xF7-0xFE","1","0x76"],capture_output=True)

        data = process(temp)

        press_msb = data[0]

        press_lsb = data[1]

        press_xlsb = data[2]

        pRaw = (press_msb << 12)|(press_lsb << 4)|(press_xlsb >> 4)

  
        temp_msb = data[3]

        temp_lsb = data[4]

        temp_xlsb = data[5]

        tRaw = (temp_msb << 12)|(temp_lsb << 4)|(temp_xlsb >> 4)

  
        hum_msb = data[6]

        hum_lsb = data[7]

        hRaw = (hum_msb << 8)|hum_lsb

  
        time.sleep(.5)

        print("Temperature: "+str(compensateT(tRaw))+" C")

        print("Pressure: "+str(compensateP(pRaw)/1000)+" hPa")

        print("Humidity: "+str(compensateH(hRaw))+" %")

        print()