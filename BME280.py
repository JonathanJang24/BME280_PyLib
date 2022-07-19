import Adafruit_GPIO.I2C as i2c
from bitstring import BitArray
import subprocess

# function to turn hexadecimal values into 8 bit binary values (regardless of leading zeroes)
# needed due to the primitive nature of the sensor which can only store bytes, thus needing to concate binary strings to form 
# short data types for compensation [see H2, H4, H5]


# BME280 Sensor Class
class BME():

    dig_T1, dig_T2, dig_T3, dig_P1, dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9, dig_H1, dig_H2, dig_H3, dig_H4, dig_H5, dig_H6 = 0

    t_fine = None

    def __init__(self,busnum,address):

        global dig_T1, dig_T2, dig_T3, dig_P1, dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9, dig_H1, dig_H2, dig_H3, dig_H4, dig_H5, dig_H6

        # uses pure Python I2C interface
        dev = i2c.device(address, busnum)

        # The compensation values are found per BME280 Data Sheet. For more information, visit the official page for documentation here:
        # https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/#documents
        # Compensation values are assigned within the constructor due to the necessity for communication with the sensor

        # Tempertaure Compensation Values
        dig_T1 = float(BitArray(bin=self.__toBin(dev.readU8(0x89))+self.__toBin(dev.readU8(0x88))).uint)
        dig_T2 = float(BitArray(bin=self.__toBin(dev.readU8(0x8B))+self.__toBin(dev.readU8(0x8A))).int)
        dig_T3 = float(BitArray(bin=self.__toBin(dev.readU8(0x8D))+self.__toBin(dev.readU8(0x8C))).int)

        # Pressure Compensation Values
        dig_P1 = float(BitArray(bin=self.__toBin(dev.readU8(0x8F))+self.__toBin(dev.readU8(0x8E))).uint)
        dig_P2 = float(BitArray(bin=self.__toBin(dev.readU8(0x91))+self.__toBin(dev.readU8(0x90))).int)
        dig_P3 = float(BitArray(bin=self.__toBin(dev.readU8(0x93))+self.__toBin(dev.readU8(0x92))).int)
        dig_P4 = float(BitArray(bin=self.__toBin(dev.readU8(0x95))+self.__toBin(dev.readU8(0x94))).int)
        dig_P5 = float(BitArray(bin=self.__toBin(dev.readU8(0x97))+self.__toBin(dev.readU8(0x96))).int)
        dig_P6 = float(BitArray(bin=self.__toBin(dev.readU8(0x99))+self.__toBin(dev.readU8(0x98))).int)
        dig_P7 = float(BitArray(bin=self.__toBin(dev.readU8(0x9B))+self.__toBin(dev.readU8(0x9A))).int)
        dig_P8 = float(BitArray(bin=self.__toBin(dev.readU8(0x9D))+self.__toBin(dev.readU8(0x9C))).int)
        dig_P9 = float(BitArray(bin=self.__toBin(dev.readU8(0x9F))+self.__toBin(dev.readU8(0x9E))).int)

        # Humidity Compensation Values
        dig_H1 = float(BitArray(bin=self.__toBin(dev.readU8(0xA1))).uint)
        dig_H2 = float(BitArray(bin=(self.__toBin(dev.readU8(0xE2))+self.__toBin(dev.readU8(0xE1)))).int)
        dig_H3 = float(BitArray(bin=self.__toBin(dev.readU8(0xE3))).uint)

        dig_E5_temp = self.__toBin(dev.readU8(0xE5))
        e5_1 = dig_E5_temp[:len(dig_E5_temp)//2]
        e5_2 = dig_E5_temp[len(dig_E5_temp)//2:]

        dig_H4 = float(BitArray(bin=self.__toBin(dev.readU8(0xE4))+e5_1).int)
        dig_H5 = float(BitArray(bin=self.__toBin(dev.readU8(0xE6))+e5_2).int)
        dig_H6 = float(BitArray(bin=self.__toBin(dev.readU8(0xE7))).int)

        self.__t_fine_update()


    def __toBin(self, val):
        temp = list(bin(val).replace("0b",""))
        for i in range(len(temp),8):
                temp.insert(0,"0")
        return ''.join(temp)

    def __process(self, data):
        data = str(data)
        temp = data.split(",")[7]
        temp = temp.split(":")[1]
        temp = temp.split()
        return ([int(x,16) for x in temp[0:8]])


    def __readValues(self, val:int):
        temp = subprocess.run(["i2cdump","-y","-r","0xF7-0xFE","1","0x76"],capture_output=True)
        data = self.__process(temp)
        if(val==0):
            press_msb = data[0]
            press_lsb = data[1]
            press_xlsb = data[2]
            pRaw = (press_msb << 12)|(press_lsb << 4)|(press_xlsb >> 4)
            return pRaw
        elif(val==1):
            temp_msb = data[3]
            temp_lsb = data[4]
            temp_xlsb = data[5]
            tRaw = (temp_msb << 12)|(temp_lsb << 4)|(temp_xlsb >> 4)
            return tRaw
        elif(val==2):
            hum_msb = data[6]
            hum_lsb = data[7]
            hRaw = (hum_msb << 8)|hum_lsb
            return hRaw


    def getRawTemp(self):
        return self.__readValues(1)

    def getRawHum(self):
        return self.__readValues(2)

    def getRawPress(self):
        return self.__readValues(0)

    def getRawAlt():
        pass

    def __t_fine_update(self):
        global t_fine
        adc_T = float(self.__readValues(1))
        var1 = ((adc_T/16384.0) - (dig_T1/1024.0)) * dig_T2
        var2 = (((adc_T/131072.0) - (dig_T1/8192.0)) * ((adc_T/131072.0) - (dig_T1/8192.0))) * dig_T3
        t_fine = (var1+var2)

    def getCompTemp(self):
        global t_fine
        adc_T = float(self.__readValues(1))
        var1 = ((adc_T/16384.0) - (dig_T1/1024.0)) * dig_T2
        var2 = (((adc_T/131072.0) - (dig_T1/8192.0)) * ((adc_T/131072.0) - (dig_T1/8192.0))) * dig_T3
        T = (var1+var2)/5120.0
        return T

    def getCompHum(self):
        self.__t_fine_update()
        adc_H = float(self.__readValues(2))
        var_H = t_fine-76800.0
        var_H = (adc_H - (dig_H4 * 64.0 + dig_H5 / 16384.0 * var_H)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * var_H * (1.0 + dig_H3 / 67108864.0 * var_H)))
        var_H = var_H * (1.0 - dig_H1 * var_H / 524288.0)
        if(var_H > 100.0):
            var_H = 100.0
        elif(var_H < 0.0):
            var_H = 0.0
        return var_H

    def getCompPress(self):
        self.__t_fine_update()
        adc_P = float(self.__readValues(0))
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
    
    def getCompAlt():
        pass