# Low-level communication - from functions to bytecodes

# Not really needed
import time
from struct import pack

# These constants and functions are used for parameter encoding process as described in Communication Developer Kit
PRIMPAR_SHORT                 = 0x00
PRIMPAR_LONG                  = 0x80

PRIMPAR_CONST                 = 0x00
PRIMPAR_VARIABEL              = 0x40 # sic! Danes are so Danish
PRIMPAR_LOCAL                 = 0x00
PRIMPAR_GLOBAL                = 0x20
PRIMPAR_HANDLE                = 0x10
PRIMPAR_ADDR                  = 0x08

PRIMPAR_INDEX                 = 0x1F
PRIMPAR_CONST_SIGN            = 0x20
PRIMPAR_VALUE                 = 0x3F

PRIMPAR_BYTES                 = 0x07

PRIMPAR_STRING_OLD            = 0
PRIMPAR_1_BYTE                = 1
PRIMPAR_2_BYTES               = 2
PRIMPAR_4_BYTES               = 3
PRIMPAR_STRING                = 4

PRIMPAR_LABEL                 = 0x20

LCS                           = [PRIMPAR_LONG | PRIMPAR_STRING]

def HND(x):                     return [PRIMPAR_HANDLE | x]
def ADR(x):                     return [PRIMPAR_ADDR | x]
def LAB1(v):                    return [(PRIMPAR_LONG | PRIMPAR_LABEL),(v & 0xFF)]

# such ugliness to save function call overhead
def LCA(h):                     return bytes([(PRIMPAR_LONG  | PRIMPAR_CONST | PRIMPAR_1_BYTE | PRIMPAR_ARRAY),(i & 0xFF)])

def lc(v):
	if v.bit_length() <= 5: return [v & 0x3F] 						# 00______
	elif v.bit_length() <= 7: return [0x81, v & 0xFF] 						# 01000001 ________
	elif v.bit_length() <= 15: return [0x82, v & 0xFF, v >> 8] 				# 01000010 ________ ________
	else: return [0x83, v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF] 	# 01000011 ________ ________ ________

def LV0(i):                     return [((i & PRIMPAR_INDEX) | PRIMPAR_SHORT | PRIMPAR_VARIABEL | PRIMPAR_LOCAL)]
def LV1(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_LOCAL | PRIMPAR_1_BYTE),(i & 0xFF)]
def LV2(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_LOCAL | PRIMPAR_2_BYTES),(i & 0xFF),((i >> 8) & 0xFF)]
def LV4(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_LOCAL | PRIMPAR_4_BYTES),(i & 0xFF),((i >> 8) & 0xFF),((i >> 16) & 0xFF),((i >> 24) & 0xFF)]
def LVA(h):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_LOCAL | PRIMPAR_1_BYTE | PRIMPAR_ARRAY),(i & 0xFF)]

def GV0(i):                     return [((i & PRIMPAR_INDEX) | PRIMPAR_SHORT | PRIMPAR_VARIABEL | PRIMPAR_GLOBAL)]
def GV1(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_GLOBAL | PRIMPAR_1_BYTE),(i & 0xFF)]
def GV2(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_GLOBAL | PRIMPAR_2_BYTES),(i & 0xFF),((i >> 8) & 0xFF)]
def GV4(i):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_GLOBAL | PRIMPAR_4_BYTES),(i & 0xFF),((i >> 8) & 0xFF),((i >> 16) & 0xFF),((i >> 24) & 0xFF)]
def GVA(h):                     return [(PRIMPAR_LONG  | PRIMPAR_VARIABEL | PRIMPAR_GLOBAL | PRIMPAR_1_BYTE | PRIMPAR_ARRAY),(i & 0xFF)]


# For each operation we need to create special function
# Incorporating opcodes as magic, as they are used only once and we do no want to produce redundant entities
# Small params (apriori positive and less than six bits) are not sent to encoding to avoid overhead
def output_step_speed(layer, motors, speed, step1, step2, step3, brake):
	return [174, layer, motors] + lc(speed) + lc(step1) + lc(step2) + lc(step3) + [brake]

def input_read(layer, port, devtype, mode):
	return [0x9A, layer, port] +lc(devtype) + lc(mode)

class RawDevice:
	device = None
	def __init__(self, s):
		self.device = open(s, 'w+b', 0)
	def __del___(self):
		self.device.close()
	
	# Sends batch of commands to the robot without reply request 
	# bytes 1-2 are the batch length
	# bytes 3-4 are message counter, but nobody seems to give a fuck about them, so we set them to zero for now
	# byte 5 is a magic code meaning DIRECT_COMMAND_NO_REPLY 
	# bytes 6-7 are variable reservation, I don't understand how it works
	def send_command_no_reply(self, batch):
		batch = [0, 0, 0x80, 0, 0] + batch		
		batch = [len(batch) & 0xFF, len(batch) >> 8] + batch
		self.device.write(bytes(batch))
	
	# Sends batch of commands to the robot with reply request
	# bytes 1-2 are the batch length
	# bytes 3-4 are message counter, but nobody seems to give a fuck about them, so we set them to zero for now
	# byte 5 is a magic code meaning DIRECT_COMMAND_REPLY 
	# bytes 6-7 are variable reservation, I don't understand how it works
	def send_command_reply(self, batch):
		batch = [0, 0, 0x00, 0x01, 0x00] + batch + GV0(0)	
		batch = [len(batch) & 0xFF, len(batch) >> 8] + batch 
		print(batch)		
		self.device.write(bytes(batch))	
	


# Just a usecase
raw = RawDevice('/dev/rfcomm1')

raw.send_command_no_reply(output_step_speed(0, 1, 25, 0, 1620, 180, 1))
raw.send_command_no_reply(output_step_speed(0, 2, -50, 0, 1620, 180, 1))
raw.send_command_no_reply(output_step_speed(0, 4, +50, 0, 1620, 180, 1))
while True:
	raw.send_command_reply(input_read(0, 3, 33, 0))
	time.sleep(0.001)	
	print(raw.device.read(6))
	
print(raw.device.flush())



