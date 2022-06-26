
# show all available buses
dmesg | grep i2c

# 1 being the bus number selected
i2cdetect -y -r 1

# Reads byte from register 0xFA on device 0x76
i2cget -y 1 0x76 0xFA

# used for burst reading, between a range of registers (0xF7-0xFE) from device 0x76 on bus 1
i2cdump -y -r 0xF7-0xFE 1 0x76

# writes value 0x12 to register 0xFA on device 0x76
i2cset -y 1 0x76 0xFA 0x12