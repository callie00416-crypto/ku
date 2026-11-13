# from threading import Thread, Condition, Timer, Lock, Semaphore, Event

# from Defines import *
# import time
# import ctypes
# import types
# import logging
# import CRC
# from Analyzer import Analyzer
# import numpy as np


from DataFormatter import *
from threading import Thread, Condition, Timer, Lock, Semaphore, Event
from Defines import *
import time
import ctypes
import types
import logging
import CRC
from Analyzer import Analyzer
import numpy as np
import pickle

class Encoder:
    def __init__(self, analyzer) -> None:
        self.analyzer = analyzer
        self.readoutConfigs = []
        self.readouts = []
        self.status = []
        self.command = EncoderCommander(self)

    def createThreads(self):
        pass

    def powerOn(self):
        return self.analyzer.sendCommand(DeviceAnalyzer, ControlSet, AnalyzerCommandEncoderPower, b'\x01')
    
    def powerOff(self):
        return self.analyzer.sendCommand(DeviceAnalyzer, ControlSet, AnalyzerCommandEncoderPower, b'\x00')

    def startPolling(self):
        self.start()
    def setTriggerSource(self,triggerSource):
        self.status = triggerSource
        self.setTriggerSource()

    def setReadoutConfig(self,readoutConfig):
        self.setReadoutConfigs([readoutConfig])

    def setReadoutConfigs(self, readoutConfigs):
        self.readoutConfigs = readoutConfigs

        readoutConfigsBytes = b''
        for readoutConfig in readoutConfigs:
            if EncoderInterfaceRecail <= readoutConfig.interface <= EncoderInterfaceBus:
                extraBytes = b''
                if hasattr(readoutConfig, 'commands'):
                    extraBytes += bytes(readoutConfig.commands)
                else:
                    extraBytes += readoutConfig.request.uart.command.to_bytes(1, byteorder="little")

                if hasattr(readoutConfig, 'data'):
                    extraBytes += bytes(readoutConfig.data)

                if hasattr(readoutConfig, 'crc') and readoutConfig.crc == True:
                    extraBytes += CRC.calcCRC8(extraBytes, 0, len(extraBytes)).to_bytes(1, byteorder="little")

                readoutConfig.request.uart.command = extraBytes[0]
                readoutConfig.followedData.length = len(extraBytes) - 1
                readoutConfigsBytes += bytes(readoutConfig) + extraBytes[1:]
            else:
                readoutConfigsBytes += bytes(readoutConfig)
        return self.analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandReadoutConfig, readoutConfigsBytes)
    def setReadout(self, readout):
        self.setReadouts([readout])

    def setReadouts(self, readouts):
        self.readouts = readouts

        readoutsBytes = b''
        for readout in readouts:
            readoutsBytes += bytes(readout)
        
        return self.analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandReadout, readoutsBytes)

    def FrameIDADD(frameidGot,n):
        AnalyzerCommandFrameID = frameidGot[1]|frameidGot[2]<< 8
        if AnalyzerCommandFrameID+n > 2**14:
            FrameIdTrigger = AnalyzerCommandFrameID+n-2**14
        else:
            FrameIdTrigger = AnalyzerCommandFrameID+n
        # if AnalyzerCommandId>255:
        return FrameIdTrigger
    def startAndReceive(self,count,readingFrequency,timeout:'ms'=0, startTriggerWithoutDelay = 0):
        encoderStatus = EncoderStatus()
        FrameidGot = self.analyzer.sendCommand(DeviceAnalyzer,ControlGet,AnalyzerCommandFrameID)
        if FrameidGot == None:
            print('error  did not got Frameid')
            exit()
        encoderStatus.startTriggerFrame = Encoder.FrameIDADD(FrameidGot,5000)
        if readingFrequency > 0:
            encoderStatus.USBTriggerInterval = int(12e6/readingFrequency)
        else:
            print('error:the readingFrequency should be bigger than 0hz' )
            #TODO: the readingFrequency must be less than 184hz
        encoderStatus.encoderStatus = EncoderStatusRunWithUSBTrigger
        encoderStatus.startTriggerWithoutDelay = startTriggerWithoutDelay

        self.analyzer.setReadEvent(count)
        # print('firstset',self.analyzer.readEventCount)
        self.analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandStatus,bytes(encoderStatus))
        if timeout != 0:
            flag = self.analyzer.waitReadEvent(timeout)
        elif timeout == -1:
            return self.analyzer.readBuffer
        else:
            stopFlag = input()
            print(stopFlag)
        return self.analyzer.readBuffer

        if flag:
            return self.analyzer.readBuffer
        else:
            None
            
    def stop(self):
        self.analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandStatus, b'\x00')
        time.sleep(1)
    def setZero(self):
        '''readout configs'''
        readoutConfig0 = EncoderReadoutConfig()
        readoutConfig0.interface = EncoderInterfaceRS485
        readoutConfig0.returnType = EncoderReturnDirect
        readoutConfig0.baudRate = 2500000
        readoutConfig0.followedData.length = 0
        readoutConfig0.request.uart.command = Encoder485422CommandZero
        readoutConfig0.request.uart.timeoutByteNum = 5

        readoutConfig1 = EncoderReadoutConfig.from_buffer_copy(readoutConfig0)
        readoutConfig1.request.uart.command = Encoder485422CommandPosition

        readoutConfigs = [readoutConfig0, readoutConfig1]

        '''readouts'''
        readout0 = EncoderReadout()
        readout0.configIndex = 1
        readout0.times = 1
        readout0.delayTime = 100
        readout1 = EncoderReadout.from_buffer_copy(readout0)
        readout1.configIndex = 0

        readouts = [readout0, readout1] * 10
        Encoder.markLastReadoutAsEnd(readouts)

        '''transmit'''
        self.setReadoutConfigs(readoutConfigs)
        self.setReadouts(readouts)

        return self.startAndReceive(len(readouts),8000)

    def enterEncoderRecalibration(self):
        readoutend = SetEncoderReadout(0,5,0)
        configLowlevelTime = EncoderReadoutConfig()
        configLowlevelTime.interface = EncoderInterfaceRS485LowLevelPulse
        configLowlevelTime.returntype = 1
        configLowlevelTime.baudRate = 2500000
        configLowlevelTime.request.lowLevelTime = 310
        readout1 =SetEncoderReadout(0,1,10) 
        readout2 =SetEncoderReadout(0,1,50) 


        self.setReadoutConfigs([configLowlevelTime])
        self.setReadouts(([readout1]*11)+[readoutend])
        # input()
        data = self.startAndReceive(1,1000,1500)
        input()
        """test Recalibration"""
        configRecaliCommandGlobal = EncoderReadoutConfig()
        configRecaliCommandGlobal.interface = EncoderInterfaceRS485
        configRecaliCommandGlobal.returnType = EncoderReturnDirect
        configRecaliCommandGlobal.baudRate = 2500000
        # configRecaliCommandGlobal.data = b'h'
        configRecaliCommandGlobal.request.uart.command = EncoderRecalibrationCommandGlobal
        configRecaliCommandGlobal.crc = True
        self.setReadoutConfigs([configRecaliCommandGlobal])
        self.setReadouts([readout2]*10+[readoutend])

        data = self.startAndReceive(1,1000,2000)
        self.stop()
        print(data)
        print(self.resolvepackages(data))
        # exit()
        # input()
        return
    def exitEncoderRecalibration(self):
        configbuffer1 = EncoderReadoutConfig()
        configbuffer1.interface = EncoderInterfaceRS485
        configbuffer1.returnType = EncoderReturnDirect
        configbuffer1.baudRate = 2500000
        configbuffer1.data = b'E'
        configbuffer1.request.uart.command = ord('E')
        configbuffer1.crc = True
        
        readoutend = SetEncoderReadout(0,5,0)
        readout1 =SetEncoderReadout(0,1,10) 
        self.setReadoutConfigs([configbuffer1])
        self.setReadouts([readout1,readoutend])
        self.startAndReceive(1,1000,1000)
        self.stop()

    def resolvePackages(packages, crc=False):
        results = []
        for package in packages:
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

                if crc and CRC.calcCRC8(triggerData, 0, trigger.length) != 0:
                    continue

                count += 1
                results.append((trigger, triggerData))

            assert header.requestInformation.packageNum == count

        return results
    def markLastReadoutAsEnd(readouts):
        if readouts[-1].times == 1:
            # Set last readout dealyTime to zero(this readout still will be triggered once)
            readouts[-1] = EncoderReadout.from_buffer_copy(readouts[-1])
            readouts[-1].delayTime = 0
        else:
            # Minus 1 from readouts' last element, and append a copy to list with delayTime = 0 and times = 1
            readouts[-1] = EncoderReadout.from_buffer_copy(readouts[-1])
            readouts[-1].times -= 1

            readouts.append(EncoderReadout.from_buffer_copy(readouts[-1]))
            readouts[-1].times = 1
            readouts[-1].delayTime = 0
    def stop(self):
        self.analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandStatus, b'\x00')

    def setZero(self):
        '''readout configs'''
        readoutConfig0 = EncoderReadoutConfig()
        readoutConfig0.interface = EncoderInterfaceRS485
        readoutConfig0.returnType = EncoderReturnDirect
        readoutConfig0.baudRate = 2500000
        readoutConfig0.followedData.length = 0
        readoutConfig0.request.uart.command = Encoder485422CommandZero
        readoutConfig0.request.uart.timeoutByteNum = 5

        readoutConfig1 = EncoderReadoutConfig.from_buffer_copy(readoutConfig0)
        readoutConfig1.request.uart.command = Encoder485422CommandPosition

        readoutConfigs = [readoutConfig0, readoutConfig1]

        '''readouts'''
        readout0 = EncoderReadout()
        readout0.configIndex = 1
        readout0.times = 1
        readout0.delayTime = 100
        readout1 = EncoderReadout.from_buffer_copy(readout0)
        readout1.configIndex = 0

        readouts = [readout0, readout1] * 10
        Encoder.markLastReadoutAsEnd(readouts)

        '''transmit'''
        self.setReadoutConfigs(readoutConfigs)
        self.setReadouts(readouts)

        return self.startAndReceive(len(readouts),8000)
class EncoderCommander:
    def __init__(self, encoder) -> None:
        self.encoder = encoder

    def setZero(self):
        '''readout configs'''
        readoutConfig0 = EncoderReadoutConfig()
        readoutConfig0.interface = EncoderInterfaceRS485
        readoutConfig0.returnType = EncoderReturnDirect
        readoutConfig0.baudRate = 2500000
        readoutConfig0.request.uart.command = Encoder485422CommandZero
        readoutConfig0.request.uart.timeoutByteNum = 5

        readoutConfig1 = EncoderReadoutConfig.from_buffer_copy(readoutConfig0)
        readoutConfig1.request.uart.command = Encoder485422CommandPosition

        readoutConfigs = [readoutConfig0, readoutConfig1]

        '''readouts'''
        readout0 = EncoderReadout()
        readout0.configIndex = 1
        readout0.times = 1
        readout0.delayTime = 100

        readout1 = EncoderReadout.from_buffer_copy(readout0)
        readout1.configIndex = 0

        readouts = [readout0, readout1] * 10

        '''transmit'''
        self.encoder.setReadoutConfigs(readoutConfigs)
        self.encoder.setReadouts(readouts, end=True)

        return self.encoder.startAndReceive(len(readouts))
    def enterRecalibration(self):
        # readoutend = SetEncoderReadout(0,5,0)
        readoutend = EncoderReadout()
        readoutend.configIndex = 1
        readoutend.times = 1
        readoutend.delayTime = 0
        configLowlevelTime = EncoderReadoutConfig()
        configLowlevelTime.interface = EncoderInterfaceRS485LowLevelPulse
        configLowlevelTime.returnType = 2
        configLowlevelTime.baudRate = 2500000
        configLowlevelTime.request.lowLevelTime = 310
        configbuffer1 = EncoderReadoutConfig()
        configbuffer1.interface = EncoderInterfaceRS485
        configbuffer1.returnType = EncoderReturnDirect
        configbuffer1.baudRate = 2500000
        configbuffer1.request.uart.command = ord('v')
        configbuffer1.crc = True
        configbuffer1.request.uart.timeoutByteNum = 5
        readout1 = EncoderReadout()
        readout1.configIndex = 0 
        readout1.times = 12
        readout1.delayTime =10
        readout2 = EncoderReadout()
        readout2.configIndex = 1
        readout2.times = 19
        readout2.delayTime =10


        self.encoder.setReadoutConfigs([configLowlevelTime,configbuffer1])
        self.encoder.setReadouts(([readout1])+[readout2]+[readoutend])
        # input()
        data = self.encoder.startAndReceive(1,2000,1000)
        time.sleep(0.2)
        self.encoder.stop()
        return data
    # def allEnterRecalibration(self):
    #     configLowlevelTime = EncoderReadoutConfig()
    #     configLowlevelTime.interface = EncoderInterfaceRS485LowLevelPulse
    #     configLowlevelTime.returnType = 2
    #     configLowlevelTime.baudRate = 2500000
    #     configLowlevelTime.request.lowLevelTime = 310

    #     ConfigSPI = EncoderReadoutConfig()
    #     ConfigSPI.interface = EncoderInterfaceBISSC
    #     ConfigSPI.returnType = EncoderReturnDirect
    #     ConfigSPI.baudRate = 1000000
    #     ConfigSPI.request.byteLength = 40
    #     ConfigSPI.request.uart.timeoutByteNum = 10

    #     ConfigSPI1 = EncoderReadoutConfig()
    #     ConfigSPI1.interface = EncoderInterfaceBISSC
    #     ConfigSPI1.returnType = EncoderReturnDirect
    #     ConfigSPI1.baudRate = 1000000
    #     ConfigSPI1.request.byteLength = 80
    #     ConfigSPI1.request.uart.timeoutByteNum = 10

    #     configbuffer1 = EncoderReadoutConfig()
    #     configbuffer1.interface = EncoderInterfaceRS485
    #     configbuffer1.returnType = EncoderReturnDirect
    #     configbuffer1.baudRate = 4000000
    #     configbuffer1.request.uart.command = ord('v')
    #     configbuffer1.crc = True
    #     configbuffer1.request.uart.timeoutByteNum = 5

    #     readoutend = EncoderReadout()
    #     readoutend.configIndex = 0
    #     readoutend.times = 1
    #     readoutend.delayTime = 0

    #     readoutSPI = EncoderReadout()
    #     readoutSPI.configIndex = 0
    #     readoutSPI.times = 1
    #     readoutSPI.delayTime = 5

    #     readoutSPI1 = EncoderReadout()
    #     readoutSPI1.configIndex = 1
    #     readoutSPI1.times = 1
    #     readoutSPI1.delayTime = 5

    #     readoutLowLevelTime = EncoderReadout()
    #     readoutLowLevelTime.configIndex = 0 
    #     readoutLowLevelTime.times = 12
    #     readoutLowLevelTime.delayTime =10

    #     readoutRecaliRead = EncoderReadout()
    #     readoutRecaliRead.configIndex = 2
    #     readoutRecaliRead.times = 19
    #     readoutRecaliRead.delayTime =10
    #     # self.encoder.setReadoutConfigs([ConfigSPI1])
    #     self.encoder.setReadoutConfigs([ConfigSPI1,ConfigSPI,configbuffer1])
    #     # exit()
    #     self.encoder.setReadouts([readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
    #             readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
    #             readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,readoutend])
    #     # printStruct([readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
    #     #         readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
    #     #         readoutSPI1,readoutSPI,readoutRecaliRead,readoutend])
    #     data = self.encoder.startAndReceive(1,2000,1000)
    #     self.encoder.stop()
    #     self.encoder.setReadoutConfigs([configLowlevelTime,configbuffer1])
    #     # self.encoder.setReadouts([readoutLowLevelTime]+[readoutRecaliRead]+[readoutend])
    #     self.encoder.setReadouts([readoutLowLevelTime]+[readoutRecaliRead]+[readoutend])
    #     data = self.encoder.startAndReceive(1,2000,1000)
    #     # time.sleep(0.5)
    #     self.encoder.stop()
    #     # readouts = [readoutSPI,readoutSPI1]*6+[readoutSPI,readoutRecaliRead,readoutend]
    #     # printStruct(readouts)
    #     # exit()
    #     return data
    def allEnterRecalibration(self):
        configLowlevelTime = EncoderReadoutConfig()
        configLowlevelTime.interface = EncoderInterfaceRS485LowLevelPulse
        configLowlevelTime.returnType = 2
        configLowlevelTime.baudRate = 2500000
        configLowlevelTime.request.lowLevelTime = 310

        ConfigSPI = EncoderReadoutConfig()
        ConfigSPI.interface = EncoderInterfaceBISSC
        ConfigSPI.returnType = EncoderReturnDirect
        ConfigSPI.baudRate = 2500000
        ConfigSPI.request.byteLength = 80
        ConfigSPI.request.uart.timeoutByteNum = 20

        ConfigSPI1 = EncoderReadoutConfig()
        ConfigSPI1.interface = EncoderInterfaceBISSC
        ConfigSPI1.returnType = EncoderReturnDirect
        ConfigSPI1.baudRate = 2500000
        ConfigSPI1.request.byteLength = 40
        ConfigSPI1.request.uart.timeoutByteNum = 20

        configbuffer1 = EncoderReadoutConfig()
        configbuffer1.interface = EncoderInterfaceRS485
        configbuffer1.returnType = EncoderReturnDirect
        configbuffer1.baudRate = 4000000
        configbuffer1.request.uart.command = ord('v')
        configbuffer1.crc = True
        configbuffer1.request.uart.timeoutByteNum = 10

        readoutend = EncoderReadout()
        readoutend.configIndex = 1
        readoutend.times = 1
        readoutend.delayTime = 0

        readoutSPI = EncoderReadout()
        readoutSPI.configIndex = 0
        readoutSPI.times = 1
        readoutSPI.delayTime = 5

        readoutSPI1 = EncoderReadout()
        readoutSPI1.configIndex = 1
        readoutSPI1.times = 1
        readoutSPI1.delayTime = 5

        readoutLowLevelTime = EncoderReadout()
        readoutLowLevelTime.configIndex = 0 
        readoutLowLevelTime.times = 12
        readoutLowLevelTime.delayTime =10

        readoutRecaliRead = EncoderReadout()
        readoutRecaliRead.configIndex = 0
        readoutRecaliRead.times = 19
        readoutRecaliRead.delayTime =10
        self.encoder.setReadoutConfigs([ConfigSPI1,ConfigSPI])
        # exit()
        self.encoder.setReadouts([readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
                readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,
                readoutSPI1,readoutSPI,readoutSPI1,readoutSPI,readoutend])
        data = self.encoder.startAndReceive(1,2000,1000,EncoderStatusRunWithTimerTrigger)
        # self.encoder.stop()
        data = self.encoder.command.singleRead(EncoderInterfaceRecail, 4000000, 0x01, timeoutBytesNum=5, crc=True)
        time.sleep(0.5)
        self.encoder.setReadoutConfigs([configLowlevelTime,configbuffer1])
        self.encoder.setReadouts([readoutLowLevelTime]+[readoutend])
        # self.encoder.setReadouts([readoutLowLevelTime]+[readoutRecaliRead]+[readoutend])
        data = self.encoder.startAndReceive(1,2000,1000,EncoderStatusRunWithTimerTrigger)
        # time.sleep(0.5)
        self.encoder.stop()
        return data
    def exitEncoderRecalibration(self):
        configbuffer1 = EncoderReadoutConfig()
        configbuffer1.interface = EncoderInterfaceRS485
        configbuffer1.returnType = EncoderReturnDirect
        configbuffer1.baudRate = 00000
        configbuffer1.data = b'E'
        configbuffer1.request.uart.command = ord('E')
        configbuffer1.crc = True
        readoutConfig = EncoderReadoutConfig()
        readoutConfig.interface = EncoderInterfaceRS485
        readoutConfig.returnType = EncoderReturnDirect
        readoutConfig.baudRate = 4000000
        readoutConfig.crc = True
        readoutConfig.request.uart.command = ord('h')
        readoutConfig.request.uart.timeoutByteNum = 5
        # encoder.setReadoutConfig(readoutConfig)
        readoutend = EncoderReadout()
        readoutend.configIndex = 0
        readoutend.times = 1
        readoutend.delayTime = 0
        readout1 = EncoderReadout()
        readout1.configIndex = 0
        readout1.times = 1
        readout1.delayTime = 10
        self.encoder.setReadoutConfigs([configbuffer1])
        self.encoder.setReadouts([readout1,readoutend])
        self.encoder.startAndReceive(1,1000,1000)
        self.encoder.stop()

    def singleRead(self, interface, baudrate, commandOrByteLength, isFirstByteLongWait=False, timeoutBytesNum = 10, payload=None, crc=False):
        # Set readout config
        # print('get3')
        readoutConfig = EncoderReadoutConfig()
        readoutConfig.interface = interface
        readoutConfig.returnType = EncoderReturnDirect
        readoutConfig.baudRate = baudrate
        # if EncoderInterfaceRecail <= interface <= EncoderInterfaceBus:
        if interface <= EncoderInterfaceBISSC:
            readoutConfig.reeuqst.byteLength = commandOrByteLength
        else:
            # print(commandOrByteLength, type(commandOrByteLength), commandOrByteLength is int)
            if isinstance(commandOrByteLength, int):
                # Single command
                readoutConfig.commands = [commandOrByteLength]
            else:
                # Multiple commands
                readoutConfig.commands = commandOrByteLength
            if payload is not None:
                readoutConfig.data = payload
            if crc:
                readoutConfig.crc = True
            readoutConfig.request.uart.isFirstByteLongWait = 1 if isFirstByteLongWait else 0
            readoutConfig.request.uart.timeoutByteNum = timeoutBytesNum
        self.encoder.setReadoutConfig(readoutConfig)
        # Set readout
        readout = EncoderReadout()
        readout.configIndex = 0
        readout.times = 1
        readout.delayTime = 10
        readoutend = EncoderReadout()
        readoutend.configIndex = 0
        readoutend.times = 0
        readoutend.delayTime = 0
        self.encoder.setReadouts([readoutend])
        data = self.encoder.startAndReceive(1,8000,100,startTriggerWithoutDelay = 1)
        # self.encoder.stop()
        return data
def startAndReceiveAll(encoders,count,readingFrequency, startTriggerWithoutDelay = 0):##multi analyzer synchronous start send and receive data
    encoderStatus = EncoderStatus()
    FrameidGot = encoders[0].analyzer.sendCommand(DeviceAnalyzer,ControlGet,AnalyzerCommandFrameID)
    if FrameidGot == None:
        print('error  did not got Frameid')
        exit()
    encoderStatus.startTriggerFrame = Encoder.FrameIDADD(FrameidGot,5000) 
    if readingFrequency>0:
        encoderStatus.USBTriggerInterval = int(12e6/readingFrequency)
    else:
        print('error:the readingFrequency should be bigger than 0hz' )
        #TODO: the readingFrequency is less than 184hz
    encoderStatus.encoderStatus = EncoderStatusRunWithUSBTrigger
    encoderStatus.startTriggerWithoutDelay = startTriggerWithoutDelay

    data = []
    for i in range(len(encoders)):
        encoders[i].analyzer.setReadEvent(count)
        encoders[i].analyzer.sendCommand(DeviceEncoder, ControlSet, EncoderCommandStatus,bytes(encoderStatus))
        # if timeout != 0:
        #     flag = encoders[i].analyzer.waitReadEvent(timeout)
        # else:
    stopFlag = input()
    print(stopFlag)
    for i in range(len(encoders)):
        data.append(encoders[i].analyzer.readBuffer)
    return data

    if flag:
        return self.analyzer.readBuffer
    else:
        None







'''----------Test Fucntions End-----------'''
import win32api, win32process,win32con
current_process_haldle = win32api.GetCurrentProcess()
win32process.SetPriorityClass(current_process_haldle, win32process.REALTIME_PRIORITY_CLASS)

if __name__ == "__main__":
    # rawdata,rawdata1 = testUSART()
    # print(rawdata[0],rawdata1[0],'len')
    # rawdata = testUSART()
    # time.sleep(2)
    devices = Analyzer.list()
    # exit()
    print(devices,1)
    analyzer = Analyzer(devices[0])
    # exit()
    encoder = Encoder(analyzer)
    configT485All = EncoderReadoutConfig()
    configT485All.interface = EncoderInterfaceRS485
    configT485All.returnType = EncoderReturnDirect
    configT485All.baudRate = 2500000
    # configT485All.request.uart.command = 0x1A
    configT485All.request.uart.command = 0x31
    configT485All.request.uart.timeoutByteNum = 5
    readout = EncoderReadout()
    readout.configIndex = 0
    readout.times = 1
    readout.delayTime = 5

    ConfigSPI = EncoderReadoutConfig()
    ConfigSPI.interface = EncoderInterfaceSSI
    ConfigSPI.returnType = EncoderReturnDirect
    ConfigSPI.baudRate = 1000000
    ConfigSPI.request.byteLength = 10
    ConfigSPI.request.uart.timeoutByteNum = 10
    # for i in range(1000):
    #     encoder.powerOff()
    #     time.sleep(0.01)
    #     encoder.powerOn()
    #     time.sleep(0.03)
    #     print(i)
    # for i in range(200):
    #     encoder.powerOff()
    #     time.sleep(0.01)
    #     encoder.powerOn()
    #     time.sleep(0.5)
    #     print(i)
    # encoder.powerOn()
    # input()
    # while True:
    #     encoder.powerOff()
    #     input()
    #     encoder.powerOn()
    #     input()
    # exit()
    encoder.powerOn()
    encoder.setReadoutConfigs([configT485All])
    encoder.setReadouts([readout])

    rawdata = encoder.startAndReceive(1,500)
    encoder.stop()
    exit()
    dataResolved = Encoder.resolvePackages(rawdata)
    print(dataResolved)
    np.savetxt('./data.txt',np.array(list(dataResolved[1])))
    exit()
    # with open("./doubleAngle.pkl", "wb") as f:
    #     pickle.dump((20000, dataResolved), f)
    # exit()
    dataResolved = Encoder.resolvePackages(rawdata)
    # CRCdata = CRC.calcBISSCCRC(a,42)
    # print(CRCdata,dataResolved[0][1][5] & 0b00111111,dataResolved[0][1][6])
    # exit()
    # # print(len(dataResolved[0][1])*8)
    # a = bytes([0,0,26,26,26,53])
    # print(CRCdata,"crc")
    # exit()
    angle = []
    for i in range(len(dataResolved)):
        # print(dataResolved)
        if dataResolved[i][-1]!= None:
            angleData = list(dataResolved[i][-1][:])
            angle.append(((angleData[0]<<16)+(angleData[1]<<8)+angleData[2])/(1<<24)*360)
            # angle.append(((angleData[2]<<16)+(angleData[3]<<8)+(angleData[4]))/(1<<24)*360)
            # print(((angleData[0]<<16)+(angleData[0]<<8)+(angleData[4]))/(1<<24)*360)``
            # print(angleData)
    import matplotlib.pyplot as plt
    plt.plot(angle)
    plt.show()
    exit()
    halldata = []
    indexHall = []
    print(dataResolved[-10:])
    for i in range(len(dataResolved)):
        if dataResolved[i][-1]!= None:
            halldata.append(list(dataResolved[i][-1]))
            indexHall.append(dataResolved[i][0].index)
    np.savetxt('./dataEncoder1.txt',halldata)
    # np.savetxt('./indexHall.txt',indexHall)
    # exit()
    exit()
    halldataReal = []
    for i in range(len(halldata)):
        halldataReal.append([])
        for j in range(int(len(halldata[i])//2)):
            halldataReal[i].append(halldata[i][2*j]*256+halldata[i][2*j+1])
    print(len(halldataReal))
    print(halldataReal[-1])
    # print(halldataReal[1])

    plt.plot(halldataReal[i])
    # plt.show()
    np.savetxt('./dualEncoderRawdata.txt',hallidataReal)
    # print(len(dataResolved[0]))
    # exit()

    # print(rawdata[1],'first')
    # print(rawdata[0][8:])
    