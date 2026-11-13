ControlGet = 0
ControlSet = 1
ControlData = 2

DeviceAnalyzer = 0
DeviceEncoder = 1
DeviceDriver = 2

USBSetGetSuccess = 0
USBSetGetErrorParams = 1
USBSetGetErrorUnsettable = 2
USBSetGetErrorUngettable = 3

'''------------------Analyzer Start------------------'''
AnalyzerCommandId = 0
AnalyzerCommandInfo = 1
AnalyzerCommandLEDMode = 2
AnalyzerCommandFirmwareMode = 3
AnalyzerCommandFirmwareData = 4
AnalyzerCommandEncoderPower = 5

AnalyzerCommandId = 0
AnalyzerCommandInfo = 1
AnalyzerCommandLEDMode = 2
AnalyzerCommandFirmwareMode = 3
AnalyzerCommandFirmwareData = 4
AnalyzerCommandEncoderPower = 5
AnalyzerCommandVotageVcc = 6
AnalyzerCommandListener = 7
AnalyzerCommandFrameID = 8
AnalyzerCommandLEDSwitch = 9
'''------------------Analyzer End------------------'''


'''------------------Encoder Start------------------'''
EncoderStatusStop = 0
EncoderStatusRunWithTimerTrigger = 1
EncoderStatusRunWithUSBTrigger = 2

EncoderCommandStatus = 0
EncoderCommandReadoutConfig = 1
EncoderCommandReadout = 2

EncoderReturnNo = 0
EncoderReturnParsed = 1
EncoderReturnDirect = 2

EncoderErrorNo = 0
EncoderErrorTimeout = 1
EncoderErrorCRC = 2
EncoderErrorBusy = 3

EncoderInterfaceSSI = 0
EncoderInterfaceBISSC = 1
EncoderInterfaceRecail = 2
EncoderInterfaceRS485 = 3
EncoderInterfaceRS422 = 4
EncoderInterfaceT485 = 5
EncoderInterfaceBus = 6
EncoderInterfaceAutoSend = 7
EncoderInterfaceSSIListener = 0x7F
EncoderInterfaceBISSCListener = 0x80
EncoderInterfaceRS485Listener = 0x81
EncoderInterfaceRS422Listener = 0x82
EncoderInterfaceBusListener = 0x83
EncoderInterfaceRS485LowLevelPulse = 0xF0

Encoder485422CommandZero = ord('0')
Encoder485422CommandPosition = ord('1')
Encoder485422CommandPositionWithStatus = ord('d')
Encoder485422CommandPositionWithSpeed = ord('s')
Encoder485422CommandPositionWithTemperature = ord('t')
Encoder485422CommandRecalibration = ord('c')
Encoder485422CommandESDDetectionNormal = 0x55
Encoder485422CommandESDDetectionError = 0x35
Encoder485422CommandHalldData = 0x95

"""recalibrate command"""
EncoderRecalibrationCommandBaudrate = ord('f')
EncoderRecalibrationCommandGlobal = ord('g')
EncoderRecalibrationCommandHall = ord('h')


EncoderT485CommandAngle = 0x02
EncoderT485CommandMulti = 0x8A
EncoderT485CommandAll = 0x1A
EncoderT485CommandResetAngle = 0xC2
EncoderT485CommandResetMulti = 0x62




RECALIBRATION_MEMORY_ACTION_READ = 0x44
RECALIBRATION_MEMORY_ACTION_ERASE = 0x55
RECALIBRATION_MEMORY_ACTION_WRITE = 0x66
RECALIBRATION_MEMORY_ACTION_END = 0x77
'''------------------Encoder End------------------'''