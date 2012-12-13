import ConfigParser
import serialinterface
import sys
import time
from Crypto.Cipher import AES
from struct import pack, unpack


config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

serialdevice = config.get('MasterController', 'serialdevice')
baudrate = config.get('MasterController', 'baudrate')
masterkey = config.get('MasterController', 'key')
masterkey =''.join([chr(int(x)) for x in masterkey.split()])

ser = serialinterface.SerialInterface(serialdevice, baudrate, timeout=.1)
cipher = AES.new(masterkey, AES.MODE_ECB)

msgformat = ">IB5s2sI"
cmd = pack(msgformat, 0, 0, '', '',0)

while True:
    msg = cipher.encrypt(cmd)
    ser.writeMessage('0', msg)
    for i in range(5):
        print ser.readMessage()
    print time.time()

