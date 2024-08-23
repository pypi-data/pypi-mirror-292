#!/usr/bin/env python3
"""Minimal manager"""
__version__ = '0.0.1 2024-05-23'#

import sys, time, threading
timer = time.perf_counter
import numpy as np

from .. import liteserver
LDO = liteserver.LDO
Device = liteserver.Device

#````````````````````````````Helper functions`````````````````````````````````
def printi(msg): print('inf_LT: '+msg)
def printw(msg): print('WAR_LT: '+msg)
def printe(msg): print('ERR_LT: '+msg)
def printd(msg): 
    if pargs.dbg:
        print('dbg_LT: '+str(msg))
#````````````````````````````Lite Data Objects````````````````````````````````
class Dev(Device):
    """ Derived from liteserver.Device.
    Note???: All class members, which are not process variables should 
    be prefixed with _"""
    
    ArrSize = 4
    ArrMax = 16
    
    def __init__(self):
        self.dummy = 0
        pars = {
          'frequency':  LDO('RWE','Update frequency of all counters',1.3,
                            units='Hz', opLimits=(0.001,1001.)),
          'cycle':      LDO('R','Cycle number',0),
          'array':      LDO('R','Array',[0]),
          'number':     LDO('RWE','Test number',0., opLimits=(-1000000,1000000),
                            setter=self.set_number),
        }
        '''
          'discrete_text': LDO('RWE','Discrete text values', 'One',
                            legalValues=['One', 'Two', 'Three']),
          'text':       LDO('RWE','Test text', ['Test'], setter=self.set_text),
          'reset':      LDO('WE','Reset array',[None],
                            setter=self.reset),
          'time':       LDO('R','Current time',0., getter=self.get_time),
        '''
        super().__init__('dev1', pars)
        if pargs.stop:
            self.PV['run'].value[0] = 'Stopped'
            self.start()
    #``````````````Overridables```````````````````````````````````````````````        
    def start(self):
        printi('>liteTiny.start()')
        self.reset()
        thread = threading.Thread(target=self._state_machine)
        thread.daemon = False
        thread.start()
    #,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

    def reset(self):
        printi(f'resetting array[{Dev.ArrSize}]')
        array = self.PV['array']
        array.value = [0]*Dev.ArrSize
        t = time.time()
        array.timestamp = t
        #self.PV['reset'].timestamp = t

    def set_number(self):
        print('Setting number to '+str(self.PV['number'].value))

    def set_text(self):
        msg = 'Setting text to '+str(self.PV['text'].value)
        printi(msg)
        #raise ValueError(msg)

    def get_time(self):
        self.PV['time'].value = time.time()

    def _state_machine(self):
        #time.sleep(.2)# give time for server to startup
        printi(f'>>>>>liteTiny._state_machine {self.name}')
        pv_status = self.PV['status']
        pv_cycle = self.PV['cycle']
        pv_array = self.PV['array']
        periodic_update = time.time()
        timestamp = time.time()
        while not Device.EventExit.is_set():
            if self.PV['run'].value[0][:4] == 'Stop':
                break
            waitTime = 1./self.PV['frequency'].value[0] - (time.time() - timestamp)
            Device.EventExit.wait(waitTime)
            timestamp = time.time()

            dt = timestamp - periodic_update
            if dt > 10.:
                periodic_update = timestamp
                if server.Dbg > 0:
                    printi(f'cycle of {self.name}:{pv_cycle.value}, wt:{round(waitTime,4)}')
                print(f'periodic update: {dt}')
                msg = f'periodic update {self.name} @{round(timestamp,3)}'
                pv_status.set_valueAndTimestamp(msg, timestamp)

            # increment counters individually
            for i in range(Dev.ArrSize):
                pv_array.value[i] += (pv_cycle.value%Dev.ArrMax) + i
     
            pv_cycle.value += 1
            # invalidate timestamps for changing variables, otherwise the
            # publish() will ignore them
            for i in [pv_array, pv_cycle, self.PV['time']]:
                i.timestamp = timestamp
        printi(f'<<<<liteTiny._state_machine')
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(description=__doc__
        ,formatter_class=argparse.ArgumentDefaultsHelpFormatter
        ,epilog=f'liteTiny version {__version__}, liteserver {liteserver.__version__}')
    defaultIP = liteserver.ip_address('')
    parser.add_argument('-i','--interface', default = defaultIP, help=\
    'Network interface. Default is the interface, which connected to internet.')
    n = 1100# to fit liteTiny volume into one chunk
    parser.add_argument('-p','--port', type=int, default=9700, help=\
    'Serving port.') 
    parser.add_argument('-S','--stop',  action='store_true', help=\
    'Do not start')
    parser.add_argument('-v', '--verbose', action='count', default=0, help=\
      'Show more log messages (-vv: show even more).')
    pargs = parser.parse_args()

    liteserver.Server.Dbg = pargs.verbose
    devices = [Dev()]

    server = liteserver.Server(devices, interface=pargs.interface,
        port=pargs.port)

    print('`'*79)
    print((f"To monitor, use: python3 -m pvplot -a'L:{server.host};{pargs.port}:dev1:' 'publishingSpeed udpSpeed'"))
    print(','*79)

    server.loop()
