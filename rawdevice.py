import time

opOUTPUT_STEP_SPEED = 174

DIRECT_COMMAND_NO_REPLY	      = 0x80

PRIMPAR_SHORT                 = 0x00
PRIMPAR_LONG                  = 0x80

PRIMPAR_CONST                 = 0x00
PRIMPAR_VARIABEL              = 0x40
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

def LC0(v):                     return [((v & PRIMPAR_VALUE) | PRIMPAR_SHORT | PRIMPAR_CONST)]
def LC1(v):                     return [(PRIMPAR_LONG  | PRIMPAR_CONST | PRIMPAR_1_BYTE),(v & 0xFF)]
def LC2(v):                     return [(PRIMPAR_LONG  | PRIMPAR_CONST | PRIMPAR_2_BYTES),(v & 0xFF),((v >> 8) & 0xFF)]
def LC4(v):                     return [(PRIMPAR_LONG  | PRIMPAR_CONST | PRIMPAR_4_BYTES),(v & 0xFF),((v >> 8) & 0xFF),((v >> 16) & 0xFF),((v >> 24) & 0xFF)]
def LCA(h):                     return [(PRIMPAR_LONG  | PRIMPAR_CONST | PRIMPAR_1_BYTE | PRIMPAR_ARRAY),(i & 0xFF)]

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


def output_step_speed(layer, motors, speed, step1, step2, step3, brake):
	return [opOUTPUT_STEP_SPEED] + LC0(layer) + LC0(motors) + LC1(speed) + LC0(step1) + LC2(step2) + LC2(step3) + LC0(brake)

class RawDevice:
	comm = None
	def __init__(self, s):
		self.comm = open(s, 'w', 0)
	def __del___(self):
		self.comm.close()
	def send_command_noreply(self, batch):
		batch = [0, 0, DIRECT_COMMAND_NO_REPLY, 0, 0] + batch		
		batch = [len(batch) & 0xFF, (len(batch) >> 8) & 0xFF] + batch
		self.comm.write(bytearray(batch))	

raw = RawDevice('/dev/rfcomm1')
raw.send_command_noreply(output_step_speed(0, 1, 50, 0, 900, 180, 1) + output_step_speed(0, 6, 50, 0, 900, 180, 1))



