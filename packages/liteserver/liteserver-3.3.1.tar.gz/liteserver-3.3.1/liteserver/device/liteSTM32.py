"""LiteServer for for STM32 boards"""
#__version__ = '0.0.1 2022-05-03'#
__version__ = '0.0.2 2022-06-23'#
 
import sys, time, threading
from timeit import default_timer as timer
import numpy as np

try:
    from liteserv import liteserver
except:
    from liteserver import liteserver
LDO = liteserver.LDO
Device = liteserver.Device

#````````````````````````````Helper functions`````````````````````````````````
def printTime(): return time.strftime("%m%d:%H%M%S")
def croppedText(txt, limit=200):
    if len(txt) > limit:
        txt = txt[:limit]+'...'
    return txt

def printi(msg): print(f'INFO@{printTime()}: {msg}')

def printw(msg):
    msg = croppedText(msg)
    print(f'WARNING@{printTime()}: {msg}')

def printe(msg):
    msg = croppedText(msg)
    print(f'ERROR@{printTime()}: {msg}')

def _printv(msg, level=0):
    if pargs.verbose is None:
        return
    if len(pargs.verbose) >= level:
        print(msg)
def printv(msg):   _printv(msg, 0)
def printvv(msg):  _printv(msg, 1)
#```````````````````serbin stuff
import serial
def b2i(buf):
    return int.from_bytes(buf, 'little')

curves = []
lasttime = time.time()

lastheader = None
legalID = ['A']
def load(io):
    global lastheader
    header = io.read(4)
    if len(header) != 4:
        printw(f'No data: {header}')
        #serdev.flush()
        return
    if header ==  b'\x04\x00\x00E': #EndOfData, l=4, id='E'
        printv(f'EndOfData message')
        return
    if lastheader is not None and header != lastheader:
        printw(f'data shape changed: {header}')
        lastheader = header
    l = b2i(header[:2])
    if header[3] == 0:
        printe(f'Header wrong: {header}')
        #serdev.flush()
        return
    hdrNB = (header[2]&0x3) + 1
    hdrNCh = ((header[2]>>2)&0xf) + 1
    printvv(f'l:{l}, NB:{hdrNB}, NChannels: {hdrNCh}')
    samplesPerChannel = l//hdrNB//hdrNCh
    errmsg = None
    try:
        hdrID = header[3:].decode()
    except:
        printe(f'Number of bits is wrong: {header}')
        return
    if hdrID not in legalID:
        printe(f'ID {header[3]} not supported')
        return
    #printv(f'h: {header}')
    payload = serdev.read(l-4)
    #printvv(croppedText(f'payload: {payload}'))
    dtype = {1:np.uint8, 2:np.uint16, 4:np.uint32}.get(hdrNB)
    if dtype is None:
        printe(f'3-byte word is not supported: {header}')
        #serdev.flush()
        return
    #print(f'dt: {dtype}')
    try:
        r = np.frombuffer(payload,dtype\
          = dtype).reshape(samplesPerChannel,hdrNCh).T
    except:
        printe(f'data[{len(payload)}] shape is wrong, channels: {hdrNCh}, width: {samplesPerChannel}')
        #serdev.flush()
        return
    #print(f'r: {r.shape}')
    return hdrID,r
 
#````````````````````````````Lite Data Objects````````````````````````````````
NCh = 8
NSamples = 16
class MCU(Device):
    """ Derived from liteserver.Device.
    Note: All class members, which are not process variables should 
    be prefixed with _"""
    def __init__(self, name):
        pars = {
          'ADC':        LDO('R', 'ADC channels',
            np.arange(NCh*NSamples).reshape(NCh,NSamples)),
          'cycle':      LDO('R','Cycle number',0),
          'rps':        LDO('R','Cycles per second',0.,units='Hz'),
          'time':       LDO('R','Current time',0., getter=self.get_time),
          'publishingSpeed': LDO('R', 'Instanteneous publishing speed of published data', 0., units='MB/s'),
          'dataSize':   LDO('R', 'Size of published data', 0., units='KB'),
          'chunks':     LDO('R', 'Number of chunks in UDP transfer, for lowest latency it should be 1', 0.),
          'udpSpeed':   LDO('R', 'Instanteneous socket.send spped', 0., units='MB/s'),
        }
        super().__init__(name,pars)
        self.start()
    #``````````````Overridables```````````````````````````````````````````````        
    def start(self):
        printi('liteSTM32 started')
        thread = threading.Thread(target=self._state_machine)
        thread.daemon = False
        thread.start()
    #,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

    def set_text(self):
        msg = 'Setting text to '+str(self.text.value)
        print(msg)
        raise ValueError(msg)

    def get_time(self):
        self.time.value = time.time()

    def _state_machine(self):
        time.sleep(.2)# give time for server to startup

        self.cycle.value = 0
        prevCycle = 0
        timestamp = time.time()
        periodic_update = time.time()
        maxChunks = 0
        while not Device.EventExit.is_set():
            #TODO: with liteserver-v76 we have to use value[0]
            if self.run.value[0][:4] == 'Stop':
                break

            # get data from serial
            #print(f'cycle: { self.cycle.value}')
            r = load(serdev)
            if r is None:
                print('no data')
                continue
            hdrID,npdata = r
            printv(f'HdrId:{hdrID}[{len(npdata)}], data:\n{npdata}')
            #npdata = np.array(serdata).reshape(NSamples,NCh).T
            #print(f'data: {npdata}')
            self.ADC.value = npdata

            timestamp = time.time()
            dt = timestamp - periodic_update
            if dt > 10.:
                periodic_update = timestamp
                if server.Dbg > 0:
                    printi(f'cycle of {self.name}:{self.cycle.value}')
                #print(f'periodic update: {dt}')
                if maxChunks > 1:
                    msg = 'WARNING: published data are chopped, latency will increase'
                    maxChunks = 0
                else:
                    msg = f'periodic update {self.name} @{round(timestamp,3)}'
                self.status.value = msg
                self.status.timestamp = timestamp
                #print(self.status.value[0])
                #Device.setServerStatusText('Cycle %i on '%self.cycle.value[0]+self.name)
                self.rps.value = (self.cycle.value - prevCycle)/dt
                self.rps.timestamp = timestamp
                prevCycle = self.cycle.value
     
            self.cycle.value += 1

            #print('publish all modified parameters of '+self.name)
            try:
                dt = server.Perf['Seconds'] - self._prevs[1]
                mbps = round((server.Perf['MBytes'] - self._prevs[0])/dt, 3)
            except:
                mbps = 0.
            self._prevs = server.Perf['MBytes'],server.Perf['Seconds']
            self.udpSpeed.value = mbps

            # invalidate timestamps for changing variables, otherwise the
            # publish() will ignore them
            for i in [self.cycle, self.udpSpeed,
                self.publishingSpeed, self.dataSize, self.chunks, self.time]:
                i.timestamp = timestamp

            ts = timer()
            shippedBytes = self.publish()

            if shippedBytes:
                ss = round(shippedBytes / (timer() - ts) / 1.e6, 3)
                #print(f'sb: {shippedBytes}')            
                self.publishingSpeed.value = ss
                #printd(f'publishing speed of {self.name}: {ss}')
                self.dataSize.value = round(shippedBytes/1000.,1)
                self.chunks.value = (shippedBytes-1)//liteserver.ChunkSize + 1
                maxChunks = max(maxChunks, self.chunks.value)
        print('Scaler '+self.name+' exit')
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,S,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# parse arguments
import argparse
parser = argparse.ArgumentParser(description=__doc__
    ,formatter_class=argparse.ArgumentDefaultsHelpFormatter
    ,epilog=f'{sys.argv[0].split("/")[-1]} version {__version__}, liteserver {liteserver.__version__}')
parser.add_argument('-b', '--baudrate', type=int, default=10000000)
defaultIP = liteserver.ip_address('')
parser.add_argument('-i','--interface', default = defaultIP, help=\
'Network IP interface. Default is the interface, which connected to internet.')
parser.add_argument('-p','--port', type=int, default=9700, help=\
'Serving IP port.')
parser.add_argument('-s','--serial', default='/dev/ttyACM0', help=\
'Serial port')
parser.add_argument('-v','--verbose', nargs='*', help='Show more log messages.')
pargs = parser.parse_args()

serdev = serial.Serial(pargs.serial, pargs.baudrate,
      timeout=1) #parity=serial.PARITY_EVEN, rtscts=1)

liteserver.Server.Dbg = 0 if pargs.verbose is None else len(pargs.verbose)+1
devices = [MCU('dev1')]

print('Serving:'+str([dev.name for dev in devices]))

server = liteserver.Server(devices, interface=pargs.interface,
    port=pargs.port)

server.loop()
