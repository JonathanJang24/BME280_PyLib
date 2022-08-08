import Adafruit_GPIO.I2C as i2c
from bitstring import BitArray
import subprocess

# BME280 Sensor Class
class BME():

    def __toBin(self, val):
        temp = list(bin(val).replace("0b",""))
        for i in range(len(temp),8):
                temp.insert(0,"0")
        return ''.join(temp)

    def __init__(self, address=0x76,busnum=1):
        
        self.address = address
        self.busnum = busnum
        self.tRaw = 0
        self.pRaw = 0
        self.hRaw = 0
        self.t_fine = 0

        # uses pure Python I2C interface
        dev = i2c.Device(address,busnum)

        # The compensation values are found per BME280 Data Sheet. For more information, visit the official page for documentation here:
        # https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/#documents
        # Compensation values are assigned within the constructor due to the necessity for communication with the sensor

        # config bits for BME280 chip
        dev.write8(0xf2,0x02)
        dev.write8(0xf4,0x43)
        dev.write8(0xf5,0x64)

        # Tempertaure Compensation Values
        self.dig_T1 = float(BitArray(bin=self.__toBin(dev.readU8(0x89))+self.__toBin(dev.readU8(0x88))).uint)
        self.dig_T2 = float(BitArray(bin=self.__toBin(dev.readU8(0x8B))+self.__toBin(dev.readU8(0x8A))).int)
        self.dig_T3 = float(BitArray(bin=self.__toBin(dev.readU8(0x8D))+self.__toBin(dev.readU8(0x8C))).int)

        # Pressure Compensation Values
        self.dig_P1 = float(BitArray(bin=self.__toBin(dev.readU8(0x8F))+self.__toBin(dev.readU8(0x8E))).uint)
        self.dig_P2 = float(BitArray(bin=self.__toBin(dev.readU8(0x91))+self.__toBin(dev.readU8(0x90))).int)
        self.dig_P3 = float(BitArray(bin=self.__toBin(dev.readU8(0x93))+self.__toBin(dev.readU8(0x92))).int)
        self.dig_P4 = float(BitArray(bin=self.__toBin(dev.readU8(0x95))+self.__toBin(dev.readU8(0x94))).int)
        self.dig_P5 = float(BitArray(bin=self.__toBin(dev.readU8(0x97))+self.__toBin(dev.readU8(0x96))).int)
        self.dig_P6 = float(BitArray(bin=self.__toBin(dev.readU8(0x99))+self.__toBin(dev.readU8(0x98))).int)
        self.dig_P7 = float(BitArray(bin=self.__toBin(dev.readU8(0x9B))+self.__toBin(dev.readU8(0x9A))).int)
        self.dig_P8 = float(BitArray(bin=self.__toBin(dev.readU8(0x9D))+self.__toBin(dev.readU8(0x9C))).int)
        self.dig_P9 = float(BitArray(bin=self.__toBin(dev.readU8(0x9F))+self.__toBin(dev.readU8(0x9E))).int)

        # Humidity Compensation Values
        self.dig_H1 = float(BitArray(bin=self.__toBin(dev.readU8(0xA1))).uint)
        self.dig_H2 = float(BitArray(bin=(self.__toBin(dev.readU8(0xE2))+self.__toBin(dev.readU8(0xE1)))).int)
        self.dig_H3 = float(BitArray(bin=self.__toBin(dev.readU8(0xE3))).uint)

        # conversion for shorts not using full 8 bits
        dig_E5_temp = self.__toBin(dev.readU8(0xE5))
        e5_1 = dig_E5_temp[:len(dig_E5_temp)//2]
        e5_2 = dig_E5_temp[len(dig_E5_temp)//2:]

        self.dig_H4 = float(BitArray(bin=self.__toBin(dev.readU8(0xE4))+e5_1).int)
        self.dig_H5 = float(BitArray(bin=self.__toBin(dev.readU8(0xE6))+e5_2).int)
        self.dig_H6 = float(BitArray(bin=self.__toBin(dev.readU8(0xE7))).int)

    def __process(self, data):
        data = str(data)
        temp = data.split(",")[7]
        temp = temp.split(":")[1]
        temp = temp.split()
        return ([int(x,16) for x in temp[0:8]])
    
    def __readValues(self):
        temp = subprocess.run(["i2cdump","-y","-r","0xF7-0xFE",str(self.busnum),str(self.address)],capture_output=True)
        data = self.__process(temp)
        press_msb = data[0]
        press_lsb = data[1]
        press_xlsb = data[2]
        pRaw = (press_msb << 12)|(press_lsb << 4)|(press_xlsb >> 4)
        self.pRaw = pRaw

        temp_msb = data[3]
        temp_lsb = data[4]
        temp_xlsb = data[5]
        tRaw = (temp_msb << 12)|(temp_lsb << 4)|(temp_xlsb >> 4)
        self.tRaw = tRaw

        hum_msb = data[6]
        hum_lsb = data[7]
        hRaw = (hum_msb << 8)|hum_lsb
        self.hRaw = hRaw

    def __t_fine_update(self):
        adc_T = float(self.tRaw)
        var1 = ((adc_T/16384.0) - (self.dig_T1/1024.0)) * self.dig_T2
        var2 = (((adc_T/131072.0) - (self.dig_T1/8192.0)) * ((adc_T/131072.0) - (self.dig_T1/8192.0))) * self.dig_T3
        self.t_fine = (var1+var2)

    def getTemp(self):
        self.__readValues()
        adc_T = float(self.tRaw)
        var1 = ((adc_T/16384.0) - (self.dig_T1/1024.0)) * self.dig_T2
        var2 = (((adc_T/131072.0) - (self.dig_T1/8192.0)) * ((adc_T/131072.0) - (self.dig_T1/8192.0))) * self.dig_T3
        T = (var1+var2)/5120.0
        return T

    def getHum(self):
        self.__t_fine_update()
        self.__readValues()
        adc_H = float(self.hRaw)
        var_H = self.t_fine-76800.0
        var_H = (adc_H - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * var_H)) * (self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * var_H * (1.0 + self.dig_H3 / 67108864.0 * var_H)))
        var_H = var_H * (1.0 - self.dig_H1 * var_H / 524288.0)
        if(var_H > 100.0):
            var_H = 100.0
        elif(var_H < 0.0):
            var_H = 0.0
        return var_H

    def getPress(self):
        self.__t_fine_update()
        self.__readValues()
        adc_P = float(self.pRaw)
        var1 = (self.t_fine/2.0) - 64000.0
        var2 = var1*var1 * (self.dig_P6) / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = (var2/4.0)+(self.dig_P4 * 65536.0)
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0+var1/32768.0)*self.dig_P1
        if(var1==0.0):
            return 0
        p = 1048576.0 - adc_P
        p = (p-(var2/4096.0)) * 6250.0 / var1
        var1 = self.dig_P9 * p * p / 2147483648.0
        var2 = p * self.dig_P8 / 32768.0
        p = p + (var1+var2 + self.dig_P7) / 16.0
        return p/1000
