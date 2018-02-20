import python_i2c
import time

print('python_i2c testing program\n')

print('testing open...')
i2c = python_i2c.i2c_open()
print('i2c handle = ' + str(i2c))



#print("testing read i2c")
#result = python_i2c.i2c_read(i2c, 0x2b, 32)

#for i in range(0, 32):
#	print(int(result[i]))

# create the UPDATE_SINGLE commnad, for led #0
# set the led to red
one_red = bytearray.fromhex(u'02 02 01 10 10 10 03 08 08 00')
python_i2c.i2c_send(i2c, 0x1a, one_red)

time.sleep(0.033) # 30 frames per second

#two_orange = bytearray.fromhex(u'20 01 00 10 00')
#python_i2c.i2c_send(i2c, 0x1a, two_orange)


print('closing i2c handle')
python_i2c.i2c_close(i2c)