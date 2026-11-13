
from DataFormatter import *
import threading
from threading import Thread, Condition, Timer, Lock, Semaphore, Event
from Defines import *
import usb.core
import usb.util
import time
import ctypes
import types
import logging
import numpy as np
import pickle as pk
import serial
import ctypes
import re
import serial.tools.list_ports

class Request:
    def __init__(self, analyzer, header, buffer, callback, timeout = 1):
        self.analyzer = analyzer
        self.header = header
        self.buffer = buffer
        self.content = bytearray(header) + buffer
        self.callback = callback
        self.transmitted = False
        self.data = None

        # assign timout callback
        self.t = Timer(timeout, self.received)

    def received(self):
        self.t.cancel()
        logging.info(self.data)
        if self.callback is types.FunctionType:
            self.callback()
        else:
            self.analyzer.blockCallback()
            pass
        self.analyzer.popRequest(self)
    def transmit(self):
        self.transmitted = True
        self.t.start()


class Analyzer:
    def __init__(self, VCOM):
        self.requestId = 0
        self.requests = []
        self.requestsLock = Lock()
        self.writeSem = Semaphore(0)
        self.blockEvent = Event()
        self.readBuffer = []
        self.readEvent = None
        self.readEventCount = 0
        self.readEventLock = Lock()
        self.ser = serial.Serial(VCOM, baudrate=0)
        self.createThreads()
    
    def setReadEvent(self, count):
        self.readBuffer = []
        e = Event()
        self.readEvent = e
        self.readEventCount = count
        

    def resetReadEvent(self):
        with self.readEventLock:
            self.readEvent.clear()
            self.readEvent = None
            self.readEventCount = 0

    def waitReadEvent(self, timeout:"in ms"):
        flag = self.readEvent.wait(timeout / 1000)
        self.resetReadEvent()
        
        return flag

    def addRequest(self, request):
        with self.requestsLock:
            self.requests.append(request)

        logging.info(request.header.requestInformation.id)
        # trigger write thread, increase semaphore
        self.writeSem.release()

    def popRequest(self, request):
        with self.requestsLock:
            try:
                self.requests.remove(request)
            except:
                pass
    
    def dataDecode(data,bytesNum):
        packRange = (len(data)-8)/bytesNum
        dataRepacked = [[]]
        if packRange-round(packRange) != 0:
            print("error bytesNum wrong1",)
        else:
            packRange = int(packRange)
            data = data[8:]
            for i in range(len(data)):
                if len(dataRepacked[-1])==bytesNum:
                    dataRepacked.append([])
                dataRepacked[-1].append(data[i])
            # print(data)
            # for i in range(len(data)):
            #     if 10>i%20>4:
            #         if len(dataRepacked[-1]) ==17:
            #             dataRepacked.append([])
            #         dataRepacked[-1].append(data[i])
            return dataRepacked

    def resolvepackages(self,packages):
        results = []
        for package in packages:
            # print(package)
            totalLngth = len(package)

            if totalLngth < 4:
                raise BufferError("Can't resolve too short data")

            header = USBDataHeader.from_buffer_copy(package)

            index = ctypes.sizeof(USBDataHeader)
            count = 0
            while index < totalLngth:
                trigger = TriggerInfo.from_buffer_copy(package, index)
                # print(trigger, trigger.length + ctypes.sizeof(TriggerInfo), index)

                index += ctypes.sizeof(TriggerInfo)
                if trigger.length == 0:
                    triggerData = None
                else:
                    triggerData = package[index: index + trigger.length]
                index += trigger.length

                count += 1
                results.append([trigger, triggerData])

            assert header.requestInformation.packageNum == count
        return results
    
    def readThread(self):
        lastindex = 0
        angle = 0
        lastangle = 0
        iflag = 0
        starttime = time.time()
        while True:
            # print(self.readEventCount,'read event count')
            try:
                data = self.ser.read(ctypes.sizeof(USBDataHeader))
            except:
                continue
            # packRange = (len(data)-8)/11
            # dataRepacked = []
            length = len(data)
            if length < ctypes.sizeof(USBDataHeader):
                continue
            
            # print(type(data), data.itemsize, data.buffer_info())
            header = USBDataHeader.from_buffer_copy(data)
            data += self.ser.read(header.bufferBytesLength)
            # print(threading.current_thread().name)
            if header.control == ControlData:
                # print(self.readEventCount)
                # a = list(data[12:])
                # lastangle = angle
                # angle = int((a[4]*65536)+(a[3]*256)+a[2])*360/(1<<17)
                # print(int((a[4]*65536)+(a[3]*256)+a[2])*360/(1<<17))
                # print(a)
                # print(angle)
                # if(220>angle>140):
                    # print(angle)
                    # exit()
                # if (abs(lastangle - angle)>90):
                    # print("there")
                    # time.sleep(2)
                # print(int((a[4]*65536)+(a[5]*256)+a[6])*360/(1<<24))
                # print(list(data)[12:])
                # print(list(data)[8:])
                # print(list(data))
                # print(list(data)[12]*256+list(data)[13])
                triggerData = self.resolvepackages([data])
                # self.readBuffer.append(triggerData[i])
                for i in range(len(triggerData)):
                    if(triggerData[i][0].length != 0):
                #         if(list(triggerData[i][1])[0]+list(triggerData[i][1])[1]*256 > 360):
                #             # while True:
                #             #     print('error sequence')
                #             raise 'errorsequence'
                        self.readBuffer.append(list(triggerData[i][1]))
                        # print(list(triggerData[i][1]),time.time()-starttime)
                # print(triggerData[0][0].length)
                # for i in range(len(triggerData)):
                    # if triggerData[i][0].index - lastindex > 1:
                        # print('error index',triggerData[i][0].index,lastindex)
                    # lastindex = triggerData[i][0].index
                #     lastangle = angle
                #     angle = (triggerData[i][1][0]*256+triggerData[i][1][1])*360/(1<<16)
                #     # angle = (triggerData[i][1][0]*65536+triggerData[i][1][1]*256+triggerData[i][1][2])*360/(1<<17)
                #     if (180>abs(lastangle - angle)>2):
                #         if lastangle != 0:
                #             print('error angle',triggerData[i],triggerData[i-1])
                #             print(lastangle,angle)
                #             exit()
                # print(angle)
                # self.readBuffer.append(data)
                # print(len(data))
                # print('read',header.requestInformation.packageNum,self.readEventCount)
                # print(self.readEventCount)
                # if self.readEventCount != 0:
                #     exit()
                
                # iflag +=1
                # if iflag >=4:
                if self.readEvent is not None:
                    self.readEvent.set()
                with self.readEventLock:
                    if self.readEvent is not None and self.readEventCount != 0:
                        self.readEventCount -= header.requestInformation.packageNum
                        # print(data, header.requestInformation.packageNum)
                        if self.readEventCount == 0:
                            self.readEvent.set()
                # print('rawdata',data)
                # print('decodedData',Analyzer.dataDecode(data,8))

            elif header.control == ControlSet or header.control == ControlGet:
                # print(self.readEventCount,123)
                self.requestsLock.acquire()
                for req in self.requests:
                    # trigger request callback
                    # print("received", length, len(self.requests), req.header.requestInformation.id, header.requestInformation.id)
                    if req.header.requestInformation.id == header.requestInformation.id:
                        logging.info(length)
                        self.requestsLock.release()
                        req.data = data[ctypes.sizeof(USBDataHeader):]
                        req.received()
                        break
                # print('requestReturn',data)

                if self.requestsLock.locked():
                    self.requestsLock.release()
            else:
                print(self.readEventCount,234)
                print("error data")
                raise BufferError("Control not right")

    def writeThread(self):
        while True:
            # print(threading.current_thread().name)
            # decrease semaphore
            self.writeSem.acquire()
            for request in self.requests:
                if request.transmitted == False:
                    try:
                        self.ser.write(request.content)
                    except:
                        print("USB error to write")
                    request.transmit()

    # def decodeThread(self):
# [33, 2, 16, 0, 0, 2, 8, 0,

    def createThreads(self):
        w = Thread(target=self.readThread, daemon=True)
        r = Thread(target=self.writeThread, daemon=True)

        w.start()
        r.start()

    def blockCallback(self):
        # print("release", self.requestsLock.locked())
        self.blockEvent.set()
    
    def sendCommand(self, device, control, command, buffer=b'', timeout:"in ms"=10, callback:"no callback will be block"=None):
        if not (callback is None or callback is types.FunctionType):
            raise TypeError("callback must be function")

        # print("sending", self.requestsLock.locked())

        header = USBDataHeader()

        header.device = device
        header.control = control
        header.command = command
        header.bufferBytesLength = len(buffer)
        
        #self increment and no overflow with uint8_t
        self.requestId += 1
        # print('RequestID:',self.requestId)
        if self.requestId >= 1 << 8:
            self.requestId = 0
        header.requestInformation.id = self.requestId
        r = Request(self, header, buffer, callback, timeout=timeout/1000)
        self.addRequest(r)

        if callback is None:
            self.blockEvent.wait()
            self.blockEvent.clear()
            logging.info("pass")
            # input()

            return r.data
    def list(self):
        VCOM = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_str = str(port)
            print(port_str)
            match = re.search(r'KingKong Analyzer \((.*?)\)', port_str)
            if match:
                VCOM.append(match.group(1))
        print(VCOM)
        return VCOM




if __name__ == '__main__':
    # logging.basicConfig(format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s", level=logging.INFO)
    # devices = Analyzer.list(0x6b6b, 0x0001)
    devices = Analyzer.list()
    # exit()
    print(devices,1)
    analyzer = Analyzer(devices[0])
    
    # analyzer1 = Analyzer(0x6b6b, 0x0001, devices[0])
    # analyzer2 = Analyzer(0x6b6b, 0x0001, devices[1])
    ledMode = AnalyzerLEDMode()
    ledMode.step = 100000
    ledMode.color[0] = 1
    # ledMode.color[1] = 2
    # ledMode.color[2] = 3
    # ledMode.color[3] = 4
    ledMode.length = 4

    # test set success
    data = analyzer.sendCommand(DeviceAnalyzer, ControlSet, AnalyzerCommandLEDMode, bytes(ledMode))
    assert data[0] == 0
    print(data)
    exit()

    # test set error
    ledMode.color[0] = 10
    data = analyzer.sendCommand(DeviceAnalyzer, ControlSet, AnalyzerCommandLEDMode, bytes(ledMode))
    assert data[0] == 1
    print(data)

    # test set success
    ledMode.color[0] = 0
    data = analyzer.sendCommand(DeviceAnalyzer, ControlSet, AnalyzerCommandLEDMode, bytearray(ledMode))
    assert data[0] == 0
    print(data)
    # test get
    data = analyzer.sendCommand(DeviceAnalyzer, ControlGet, AnalyzerCommandLEDMode)
    assert data[0] == 0 and len(data) == ctypes.sizeof(AnalyzerLEDMode) + 1
    ledMode = AnalyzerLEDMode.from_buffer(data, 1)
    printStruct(ledMode)