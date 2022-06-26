import Adafruit_GPIO.I2C as i2c
from bitstring import BitArray


# function to turn hexadecimal values into 8 bit binary values (regardless of leading zeroes)
# needed due to the primitive nature of the sensor which can only store bytes, thus needing to concate binary strings to form 
# short data types for compensation [see H2, H4, H5]
def toBin(val):
        temp = list(bin(val).replace("0b",""))
        for i in range(len(temp),8):
                temp.insert(0,"0")
        return ''.join(temp)


# BME280 Sensor Class
class BME(object):

    dig_T1, dig_T2, dig_T3, dig_P1, dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9, dig_H1, dig_H2, dig_H3, dig_H4, dig_H5, dig_H6 = 0

    def __init__(self,busnum,address):

        global dig_T1, dig_T2, dig_T3, dig_P1, dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9, dig_H1, dig_H2, dig_H3, dig_H4, dig_H5, dig_H6

        # uses pure Python I2C interface
        dev = i2c.device(address, busnum)


        # The compensation values are found per BME280 Data Sheet. For more information, visit the official page for documentation here:
        # https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/#documents
        # Compensation values are assigned within the constructor due to the necessity for communication with the sensor

        # Tempertaure Compensation Values
        dig_T1 = float(BitArray(bin=toBin(dev.readU8(0x89))+toBin(dev.readU8(0x88))).uint)
        dig_T2 = float(BitArray(bin=toBin(dev.readU8(0x8B))+toBin(dev.readU8(0x8A))).int)
        dig_T3 = float(BitArray(bin=toBin(dev.readU8(0x8D))+toBin(dev.readU8(0x8C))).int)

        # Pressure Compensation Values
        dig_P1 = float(BitArray(bin=toBin(dev.readU8(0x8F))+toBin(dev.readU8(0x8E))).uint)
        dig_P2 = float(BitArray(bin=toBin(dev.readU8(0x91))+toBin(dev.readU8(0x90))).int)
        dig_P3 = float(BitArray(bin=toBin(dev.readU8(0x93))+toBin(dev.readU8(0x92))).int)
        dig_P4 = float(BitArray(bin=toBin(dev.readU8(0x95))+toBin(dev.readU8(0x94))).int)
        dig_P5 = float(BitArray(bin=toBin(dev.readU8(0x97))+toBin(dev.readU8(0x96))).int)
        dig_P6 = float(BitArray(bin=toBin(dev.readU8(0x99))+toBin(dev.readU8(0x98))).int)
        dig_P7 = float(BitArray(bin=toBin(dev.readU8(0x9B))+toBin(dev.readU8(0x9A))).int)
        dig_P8 = float(BitArray(bin=toBin(dev.readU8(0x9D))+toBin(dev.readU8(0x9C))).int)
        dig_P9 = float(BitArray(bin=toBin(dev.readU8(0x9F))+toBin(dev.readU8(0x9E))).int)

        # Humidity Compensation Values
        dig_H1 = float(BitArray(bin=toBin(dev.readU8(0xA1))).uint)
        dig_H2 = float(BitArray(bin=(toBin(dev.readU8(0xE2))+toBin(dev.readU8(0xE1)))).int)
        dig_H3 = float(BitArray(bin=toBin(dev.readU8(0xE3))).uint)

        dig_E5_temp = toBin(dev.readU8(0xE5))
        e5_1 = dig_E5_temp[:len(dig_E5_temp)//2]
        e5_2 = dig_E5_temp[len(dig_E5_temp)//2:]

        dig_H4 = float(BitArray(bin=toBin(dev.readU8(0xE4))+e5_1).int)
        dig_H5 = float(BitArray(bin=toBin(dev.readU8(0xE6))+e5_2).int)
        dig_H6 = float(BitArray(bin=toBin(dev.readU8(0xE7))).int)


    def getRawTemp():
        pass

    def getRawHum():
        pass

    def getRawPress():
        pass

    def getRawAlt():
        pass

    def getCompTemp():
        pass

    def getCompHum():
        pass

    def getCompPress():
        pass
    
    def getCompAlt():
        pass