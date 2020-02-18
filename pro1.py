#!/usr/bin/env python
import sys
import httplib
import signal
import socket
import time
import paho.mqtt.client as mqtt
from twisted.internet import task
from twisted.internet import reactor

from pymodbus.constants import Endian
from pymodbus.constants import Defaults
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

#————————- basic settings —————————–
DEBUG = 1

# settings for USB-RS485 adapter
SERIAL = '/dev/ttyAMA0'
BAUD = 9600

# settings for SDM630 Modbus
MB_ID = 1
READ_INTERVAL = 0
WRITE_INTERVAL = 2

 

#———————————————————————-
# set Modbus defaults
Defaults.UnitId = MB_ID
Defaults.Retries = 5

 

p1_sum = p2_sum = p3_sum = 0
v1_sum = v2_sum = v3_sum = 0
pl1 = pl2 = pl3 = p14 = 0
vl1 = vl2 = vl3 = 10
il1 = il2 = il3 = 0
msg_count = 0
count = 0
failed = 0




def doWork():
  print("###################################")
  global failed, v1_sum, v2_sum, v3_sum, p1_sum, p2_sum, p3_sum, count, msg_count, export, imp

  result = client.read_input_registers(0x3913, 18,1)
  result2 = client.read_input_registers(0x048, 4,1)
  if result2:
  if count >= WRITE_INTERVAL:
  decoder2 = BinaryPayloadDecoder.fromRegisters(result2.registers, endian=Endian.Big)
  imp = decoder2.decode_32bit_float()
  export = decoder2.decode_32bit_float()
  print “Export: %.2f import: %.2f” % (export, imp)
  if result:
  failed = 0
  decoder = BinaryPayloadDecoder.fromRegisters(result.registers, endian=Endian.Big)
  v1_sum = v1_sum + decoder.decode_32bit_float()
  v2_sum = v2_sum + decoder.decode_32bit_float()
  v3_sum = v3_sum + decoder.decode_32bit_float()
  i1 = decoder.decode_32bit_float()
  i12 = decoder.decode_32bit_float()
  i13 = decoder.decode_32bit_float()
  p1_sum = p1_sum + decoder.decode_32bit_float()
  p2_sum = p2_sum + decoder.decode_32bit_float()
  p3_sum = p3_sum + decoder.decode_32bit_float()
  count = count + 1
  print “Count: “, (“%.2f” % count)
 if count >= WRITE_INTERVAL:
 vl1 = v1_sum / count
 vl2 = v2_sum / count
 vl3 = v3_sum / count
 pl1 = p1_sum / count
 pl2 = p2_sum / count
 pl3 = p3_sum / count
 ts = (p1_sum + p2_sum + p3_sum) / count
 v1_sum = v2_sum = v3_sum = 0
 p1_sum = p2_sum = p3_sum = 0
 count = 0
msg_count = msg_count + 1
data1 = [pl1, pl2, pl3, vl1, vl2, vl3, msg_count, 0, ts]
if DEBUG:
print “V1: %.2f V2: %.2f V3: %.2f” % (vl1, vl2, vl3)
print “P1: %.2f P2: %.2f P3: %.2f” % (pl1, pl2, pl3)
print “Total: “,(“%.2f” % ts)


else:
if DEBUG:
print “Sent!”
else:
failed = failed + 1
print “no result: “, (“%.2f” % failed)
pass

client = ModbusClient(method=’rtu’, port=SERIAL, stopbits=1, bytesize=8, timeout=0.25, baudrate=BAUD, parity=’N’)
connection = client.connect()
if DEBUG:
print “Readout started”

signal.signal(signal.SIGINT, sig_handler)

l = task.LoopingCall(doWork)
l.start(READ_INTERVAL)

reactor.run()