import ctypes
import pprint

class BaseUnion(ctypes.Union):
    def toDict(self):
        obj = {}

        for key, cls in self._fields_:
            value = getattr(self, key)

            if issubclass(cls, ctypes.Array):
                value = list(value)

            obj[key] = value

        # move anonymous key to parent level
        if hasattr(self, "_anonymous_"):
            for key in self._anonymous_:

                child = obj[key].toDict()
                for k in child:
                    obj[k] = child[k]


                del obj[key]

        return obj

    def __repr__(self):
        return str(self.toDict())

class BaseStruct(ctypes.LittleEndianStructure):
    def toDict(self):
        obj = {}

        for v in self._fields_:
            key = v[0]
            cls = v[1]

            if len(v) == 3:
                bitFieldNumber = v[2]

            value = getattr(self, key)

            if issubclass(cls, ctypes.Array):
                value = list(value)

            obj[key] = value

        # move anonymous key to parent level
        if hasattr(self, "_anonymous_"):
            for key in self._anonymous_:
                child = obj[key].toDict()

                for k in child:
                    obj[k] = child[k]

                del obj[key]

        return obj

    def __repr__(self):
        return str(self.toDict())

class TriggerInfo(BaseStruct):
    # _pack_ = 1
    _fields_ = [
        ("index", ctypes.c_uint16, 13),
        ("error", ctypes.c_uint16, 3),
        ("readoutConfigIndex", ctypes.c_uint16, 5),
        ("length", ctypes.c_uint16, 11)
    ]

class EncoderRequestInformation(BaseStruct):
    class _U(BaseUnion):
        class _Seperated(BaseStruct):
            _fields_ = [
                ("isSeperated", ctypes.c_uint16, 1),
                ("packageNum", ctypes.c_uint16, 15)
            ]

        class _NoSeperated(BaseStruct):
            _fields_ = [
                ("_", ctypes.c_uint16, 1),
                ("seperatedId", ctypes.c_uint16, 7),
                ("seperatedNum", ctypes.c_uint16, 8)
            ]

        _anonymous_ = ("S", "NS")
        _fields_ = [
            ("S", _Seperated),
            ("NS", _NoSeperated),
        ]

    _anonymous_ = ("U")
    _fields_ = [
        ("packageId", ctypes.c_uint8),
        ("id", ctypes.c_uint8),
        ("U", _U)
    ]

class USBDataHeader(BaseStruct):
    _fields_ = [
        ("device", ctypes.c_uint8, 4),
        ("control", ctypes.c_uint8, 4),
        ("command", ctypes.c_uint8),
        ("bufferBytesLength", ctypes.c_uint16),
        ("requestInformation", EncoderRequestInformation)
    ]

class EncoderStatus(BaseStruct):
    _fields_ = [
        ('encoderStatus',ctypes.c_uint8),
        ('startTriggerWithoutDelay',ctypes.c_uint8),
        ('startTriggerFrame',ctypes.c_uint32),
        ('USBTriggerInterval',ctypes.c_uint32)
    ]

class EncoderReadout(BaseStruct):
    _fields_ = [
        ('configIndex',ctypes.c_uint8),
        ('times',ctypes.c_uint8),
        ('delayTime',ctypes.c_uint32)
    ]

class EncoderReadoutConfig(BaseStruct):
    class _U(BaseUnion):
        class _S(BaseStruct):
            _fields_ =[
                ('interface',ctypes.c_uint8),
                ('returnType',ctypes.c_uint8)
            ]
        _anonymous_ = ('S')
        _fields_ = [
            ('S', _S),
            ('id',ctypes.c_uint16)
        ]

    class request(BaseUnion):
        class uart(BaseStruct):
            _fields_ = [
                ('command',ctypes.c_uint8),
                ('timeoutByteNum',ctypes.c_uint8)
            ]
        _fields_ = [
            ('uart',uart),
            ('byteLength',ctypes.c_uint8),
            ('lowLevelTime',ctypes.c_uint16),
            ('value',ctypes.c_uint16)
        ]

    class followedData(BaseUnion):
        class index(BaseStruct):
            _fields_ = [
                ('start',ctypes.c_uint16),
                ('length',ctypes.c_uint16)
            ]
        _fields_ = [
            ('length',ctypes.c_uint32),
            ('index',index)
        ]


    class parseFormat(BaseUnion):
        class bytes(BaseStruct):
            _fields_ = [
                ('multi',ctypes.c_uint8),
                ('single',ctypes.c_uint8),
                ('extra',ctypes.c_uint8),
                ('total',ctypes.c_uint8)
            ]

        class bits(BaseStruct):
            _fields_ = [
                ('multi',ctypes.c_uint8),
                ('single',ctypes.c_uint8),
                ('extra',ctypes.c_uint8),
                ('total',ctypes.c_uint8)
            ]
        _fields_ = [
            ('bytes',bytes),
            ('bits',bits)
        ]

    _anonymous_ = ('U')
    _fields_ = [
        ('U',_U),
        ('request',request),
        ('baudRate',ctypes.c_uint32),
        ('followedData',followedData),
        ('parseFormat',parseFormat)
    ]

class AnalyzerLEDMode(BaseStruct):
    _fields_ = [
        ('step', ctypes.c_uint32),
        ('color', ctypes.c_uint8 * 100),
        ('length', ctypes.c_uint8)
    ]
class AnalyzerLEDSwitch(BaseStruct):
    _fields_ = [
        ('turnOn', ctypes.c_uint32)
    ]
"""Recalibrations start"""
class RecalibrationArgumets(BaseStruct):
    class Version(BaseStruct):
        _fields_ = [
            ('software',ctypes.c_uint16),
            ('hardware',ctypes.c_uint16)
        ]
    class Product(BaseStruct):
        class _S(BaseUnion):
            class _T(BaseStruct):
                _fields_ = [
                    ('innerHallNumber',ctypes.c_uint8),
                    ('outterHallNumber',ctypes.c_uint8)
                ]
            _anonymous_ = ('T')
            _fields_ = [
                ('T',_T),
                ('hallNumber',ctypes.c_uint16)
            ]
        class _Q(BaseUnion):
            class _Y(BaseStruct):
                _fields_ = [
                    ('innerSectionNumber',ctypes.c_uint8),
                    ('outterSectionNumber',ctypes.c_uint8)
                ]
            _anonymous_ = ('Y')
            _fields_ = [
                ('Y',_Y),
                ('hallNumber',ctypes.c_uint16)
            ]
        class _NS(BaseUnion):
            class _U(BaseStruct):
                _fields_ = [
                    ('rotorInnerSize',ctypes.c_uint8),
                    ('rotorOutterSize',ctypes.c_uint8)
                ]
            _anonymous_ = ('U')
            _fields_ = [
                ('U',_U),
                ('rotorSize',ctypes.c_uint16)
            ]
        _anonymous_ = ('S','NS','Q')
        _fields_ = [
            ('series',ctypes.c_uint16),
            ('S',_S),
            ('Q',_Q),
            ('statorInnerSize',ctypes.c_uint8),
            ('statorOuterSize',ctypes.c_uint8),
            ('NS',_NS)
        ]
    class Resolution (BaseStruct):
        _fields_ = [
            ('multi',ctypes.c_uint8),
            ('single',ctypes.c_uint8)
        ]
    class _P(BaseStruct):
        _fields_ = [
            ('zeroPositonInner',ctypes.c_uint32),
            ('zeroPositonOutter',ctypes.c_uint32)
        ]
    _anonymous_ = ("P",)
    _fields_ = [
        ("argumentsVersion", ctypes.c_uint32),
        ("version", Version),
        ("P", _P),
        ("product",Product),
        ("baudrate",ctypes.c_uint32),
        ("updatefrequency",ctypes.c_uint32),
        ("autoSendPerioddPer100us",ctypes.c_uint16),
        ("batteryRPM",ctypes.c_uint16),
        ("date",ctypes.c_uint16),
        ("time",ctypes.c_uint16),
        ("OD",ctypes.c_uint16),
        ("ID",ctypes.c_uint16),
        ("model",ctypes.c_uint8),
        ("interface",ctypes.c_uint8),
        ("busID",ctypes.c_uint8),
        ("systemClock",ctypes.c_uint8),
        ("internalResolution", Resolution),
        ("outputResolution", Resolution),
        ("FlashStatus",ctypes.c_uint32)
    ]
class DPTParamFit(BaseStruct):
    _fields_ = [
        ('InnerParamFit1', ctypes.c_float*36*4),
        ('InnerParamFit2', ctypes.c_float*36*4),
        ('InnerParamFit3', ctypes.c_float*36*4),
        ('OutterParamFit1', ctypes.c_float*36*4),
        ('OutterParamFit2', ctypes.c_float*36*4),
        ('OutterParamFit3', ctypes.c_float*36*4),
    ]
class MPTParamFit(BaseStruct):
    _fields_ = [
        ('ParamFit1', ctypes.c_float*36*4),
        ('ParamFit2', ctypes.c_float*36*4),
        ('ParamFit3', ctypes.c_float*36*4),
    ]
def HallParamFactory(hallNum, poleNum, DegSize=15):
    class HallParam(BaseStruct):
        _fields_ = [
            ("partitionTrustZeroMoreExtend", ctypes.c_uint8),
            ("calibrationA2VDeg", ctypes.c_uint8),
            ("calibrationA2VDiv", ctypes.c_uint8),
            ("calibrationV2ADeg", ctypes.c_uint8),
            ("calibrationV2ADiv", ctypes.c_uint8),
            ('pattern', ctypes.c_uint8*poleNum),
            ("partitionZeroThreshold", ctypes.c_float),
            ("calibrationExtendAngle", ctypes.c_float),
            ('base',ctypes.c_float*(DegSize+1)*poleNum*hallNum),
            ('hallZeroPosition', ctypes.c_float*poleNum*hallNum),
            ('hallAmplitude', ctypes.c_int16*poleNum*hallNum)
        ]
    return HallParam
def ParamFitFactory(poleNum, DegSize=3):
    class ParamFit(BaseStruct):
        _fields_ = [
            ('paramFit1', ctypes.c_float*(DegSize+1)*poleNum),
            ('paramFit2', ctypes.c_float*(DegSize+1)*poleNum),
            ('paramFit3', ctypes.c_float*(DegSize+1)*poleNum)
        ]
    return ParamFit
class HallIndex(BaseStruct):
    _fields_ = [
        ('index', ctypes.c_uint32, 4),
        ('bits', ctypes.c_uint32, 12),
        ('bitsCount', ctypes.c_uint32, 4)
    ]
class CodeInfo(BaseStruct):
    _fields_ = [
        ('v0IndexIdeal', ctypes.c_uint8),
        ('v1IndexIdeal', ctypes.c_uint8),
        ('v0IndexReal', HallIndex),
        ('v1IndexReal', HallIndex),
        ('lastV0IndexReal', HallIndex),
        ('nextV1IndexReal', HallIndex),
        ('groupGuidersLength', ctypes.c_uint8),
        ('lastCodeIdeal', ctypes.c_uint16),
        ('nextCodeIdeal', ctypes.c_uint16),
        ('crossFromCode0', ctypes.c_uint16),
        ('crossFromCode1', ctypes.c_uint16),
        ('v0Index_polyftIndex', ctypes.c_uint16),
        ('groupMSKGID', ctypes.c_uint32),
        ('groupGuiders', ctypes.c_uint32 * 5)
    ]
def AngleDataFactory(hallNum):
    class AngleData(BaseStruct):
        _fields_ = [
            ('extendAngle', ctypes.c_float),
            ('zeroThreshold', ctypes.c_float),
            ('trustZeroMoreExtend', ctypes.c_uint8),
            ('v2ARangeSize', ctypes.c_uint8),
            ('v2AParamsSize', ctypes.c_uint8),
            ('v2AParamsDegSize', ctypes.c_uint8),
            ('a2VRangeSize', ctypes.c_uint8),
            ('a2VParamsSize', ctypes.c_uint8),
            ('a2VParamsDegSize', ctypes.c_uint8),
            ('calcMaxPolyfitDiff',ctypes.c_uint8),
            ('groupsSize',ctypes.c_uint32),
            ('polyfitSize',ctypes.c_uint32),
            ('middles', ctypes.c_uint16 * hallNum),
            ('codes', CodeInfo * (1 << hallNum)),
            ('groups', ctypes.c_uint32)
        ]

    return AngleData
AngleData9 = AngleDataFactory(9)
AngleData8 = AngleDataFactory(8)

class GroupInfo(BaseStruct):
    _fields_ = [
            ('groupMSKGID', ctypes.c_uint32),
            ('leftCode', ctypes.c_uint16),
            ('rightCode', ctypes.c_uint16),
            ('targetHallNum', ctypes.c_uint8),
            ('targetHallIndex0', ctypes.c_uint8),
            ('targetHallIndex1', ctypes.c_uint8),
            ('targetHallLeftState', ctypes.c_uint8),
            ('targetHallIndex0_polyfitIndex', ctypes.c_uint16),
            ('targetHallIndex1_polyfitIndex',ctypes.c_uint16)
    ]
def PolyfitFactory(V2A_R_ARR_SIZE,V2A_P_ARR_SIZE,V2A_P_DEG_SIZE,A2V_R_ARR_SIZE,A2V_P_ARR_SIZE,A2V_P_DEG_SIZE):
    class Polyfit(BaseStruct):
        _fields_ = [
            ('hallIndex', ctypes.c_uint8),
            ('hallDir', ctypes.c_uint8),
            ('angleBase', ctypes.c_uint32),
            ('V2ARanges', ctypes.c_float*V2A_R_ARR_SIZE),
            ('V2AParams', ctypes.c_float *V2A_P_DEG_SIZE*V2A_P_ARR_SIZE),
            ('A2VRanges', ctypes.c_float *A2V_R_ARR_SIZE),
            ('A2VParams', ctypes.c_float*A2V_P_DEG_SIZE*A2V_P_ARR_SIZE)
        ]
    return Polyfit


"""Recalibrations end"""
def printStruct(s):
    d = eval(str(s))
    pprint.pprint(d, compact=True)

if __name__ == '__main__':
    '''TriggerInfo Test'''
    b = bytearray([150, 34, 0, 0])
    print(len(b))
    t = TriggerInfo.from_buffer(b)
    print(ctypes.sizeof(t))
    print(t.error, t.index, t.length)
    
    thead = USBDataHeader()
    # thead.controlAndDevice = 17
    # thead.command = 1
    # thead.bufferBytesLength = 1
    # thead.requestInformation = 0
    # b = bytearray(thead)
    # print(thead, (thead), thead.content)

    print(ctypes.sizeof(AnalyzerLEDMode))




    
    # print(b)
    # print("Size of TriggerInfo:", ctypes.sizeof(t))
    # # exit()
    # print(t.index, t.error, t.readoutConfigIndex, t.length)

    # #Update unoverflow test
    # t.length = (1 << 11) - 1
    # print(b)
    # print(t.index, t.error, t.readoutConfigIndex, t.length)
    # #Update overflow test
    # t.length = (1 << 11)
    # print(b)
    # print(t.index, t.error, t.readoutConfigIndex, t.length)

    # #convert struct to bytes
    # print(bytearray(t))



    # '''EncoderRequestInformation Test'''
    # b = bytearray([33, 2, 42, 0, 0, 0, 2, 0])
    # r = EncoderRequestInformation.from_buffer(b)

    # print("Size of EncoderRequestInformation:", ctypes.sizeof(t))
    # #test anonymous field
    # print(r.id16, r.isSeperated, r.packageNum, r.seperatedId, r.seperatedNum)



    # '''USBDataHeader Test'''
    # b = bytearray([1, 2, 00, 00, 0, 0, 2, 0])
    # h = USBDataHeader.from_buffer(b)
    # print(bytes(b))

    # print("Size of USBDataHeader:", ctypes.sizeof(h))
    # #test anonymous field
    # print(h.controlAndDevice, h.command, h.bufferBytesLength, h.requestInformation)
    # print(size(h))
    # print(ctypes.sizeof(USBDataReadoutConfig))