'''
Created on Oct 4, 2015

@author: lab
'''
import os
import ctypes
from collections import OrderedDict

class PI_Enum(object):
    
    def __init__(self, name, byname_dict):
        self.name = name
        self.byname = dict(byname_dict)
        self.bysname = dict() # ShortName
        self.bynum  = dict()
        self.bynums  = dict()
        for name, num in self.byname.items():
            self.bynum[num] = name
            sname = name.split('_')[1]
            self.bysname[sname] = num
            self.bynums[num] = sname



#typedef          int    piint;  /* integer native to platform                 */
piint = ctypes.c_int
#typedef          double piflt;  /* floating point native to platform          */
piflt = ctypes.c_double
#typedef          int    pibln;  /* boolean native to platform                 */
pibln = ctypes.c_int
#typedef          char   pichar; /* character native to platform               */
pichar = ctypes.c_char
pichar_p = ctypes.c_char_p
#typedef unsigned char   pibyte; /* byte native to platform                    */
pibyte = ctypes.c_ubyte
#if defined __cplusplus
#    typedef      bool   pibool; /* C++ boolean native to platform             */
#endif
pibool = ctypes.c_bool

#typedef signed   char      pi8s;  /* 8-bit signed integer                 */
pi8s = ctypes.c_int8    
#typedef unsigned char      pi8u;  /* 8-bit unsigned integer               */
pi8u = ctypes.c_uint8
#typedef          short     pi16s; /* 16-bit signed integer                */
pi16s = ctypes.c_int16
#typedef unsigned short     pi16u; /* 16-bit unsigned integer              */
pi32u = ctypes.c_uint32
#typedef          long      pi32s; /* 32-bit signed integer                */
pi32s = ctypes.c_int32
#typedef unsigned long      pi32u; /* 32-bit unsigned integer              */
pi32u = ctypes.c_uint32
#typedef          long long pi64s; /* 64-bit signed integer                */
pi64s = ctypes.c_int64
#typedef unsigned long long pi64u; /* 64-bit unsigned integer              */
pi64u = ctypes.c_uint64
#typedef          float     pi32f; /* 32-bit floating point                */
pi32f = ctypes.c_float
#typedef          double    pi64f; /* 64-bit floating point                */
pi64f = ctypes.c_double

PicamEnumeratedTypeEnum = PI_Enum(
    "PicamEnumeratedType", dict(
    #/*------------------------------------------------------------------------*/
    #/* Function Return Error Codes -------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_Error                      =  1,
    #/*------------------------------------------------------------------------*/
    #/* General String Handling -----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_EnumeratedType             = 29,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Identification ---------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_Model                      =  2,
    PicamEnumeratedType_ComputerInterface          =  3,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Plug 'n Play Discovery -------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_DiscoveryAction            = 26,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Access -----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_HandleType                 = 27,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameters -------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueType                  =  4,
    PicamEnumeratedType_ConstraintType             =  5,
    PicamEnumeratedType_Parameter                  =  6,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameter Values - Enumerated Types ------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ActiveShutter              = 53,
    PicamEnumeratedType_AdcAnalogGain              =  7,
    PicamEnumeratedType_AdcQuality                 =  8,
    PicamEnumeratedType_CcdCharacteristicsMask     =  9,
    PicamEnumeratedType_CenterWavelengthStatus     = 51,
    PicamEnumeratedType_CoolingFanStatus           = 56,
    PicamEnumeratedType_EMIccdGainControlMode      = 42,
    PicamEnumeratedType_GateTrackingMask           = 36,
    PicamEnumeratedType_GatingMode                 = 34,
    PicamEnumeratedType_GatingSpeed                = 38,
    PicamEnumeratedType_GratingCoating             = 48,
    PicamEnumeratedType_GratingType                = 49,
    PicamEnumeratedType_IntensifierOptionsMask     = 35,
    PicamEnumeratedType_IntensifierStatus          = 33,
    PicamEnumeratedType_LaserOutputMode            = 45,
    PicamEnumeratedType_LaserStatus                = 54,
    PicamEnumeratedType_LightSource                = 46,
    PicamEnumeratedType_LightSourceStatus          = 47,
    PicamEnumeratedType_ModulationTrackingMask     = 41,
    PicamEnumeratedType_OrientationMask            = 10,
    PicamEnumeratedType_OutputSignal               = 11,
    PicamEnumeratedType_PhosphorType               = 39,
    PicamEnumeratedType_PhotocathodeSensitivity    = 40,
    PicamEnumeratedType_PhotonDetectionMode        = 43,
    PicamEnumeratedType_PixelFormat                = 12,
    PicamEnumeratedType_ReadoutControlMode         = 13,
    PicamEnumeratedType_SensorTemperatureStatus    = 14,
    PicamEnumeratedType_SensorType                 = 15,
    PicamEnumeratedType_ShutterStatus              = 52,
    PicamEnumeratedType_ShutterTimingMode          = 16,
    PicamEnumeratedType_ShutterType                = 50,
    PicamEnumeratedType_TimeStampsMask             = 17,
    PicamEnumeratedType_TriggerCoupling            = 30,
    PicamEnumeratedType_TriggerDetermination       = 18,
    PicamEnumeratedType_TriggerResponse            = 19,
    PicamEnumeratedType_TriggerSource              = 31,
    PicamEnumeratedType_TriggerStatus              = 55,
    PicamEnumeratedType_TriggerTermination         = 32,
    PicamEnumeratedType_VacuumStatus               = 57,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameter Information - Value Access -----------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueAccess                = 20,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameter Information - Dynamics ---------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_DynamicsMask               = 28,
    #/*------------------------------------------------------------------------*/
    #/* Camera/Accessory Parameter Constraints - Enumerated Types -------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ConstraintScope            = 21,
    PicamEnumeratedType_ConstraintSeverity         = 22,
    PicamEnumeratedType_ConstraintCategory         = 23,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Constraints - Regions of Interest --------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_RoisConstraintRulesMask    = 24,
    #/*------------------------------------------------------------------------*/
    #/* Camera Acquisition Control --------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionErrorsMask      = 25,
    #/*------------------------------------------------------------------------*/
    #/* Camera Acquisition Notification ---------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionState           = 37,
    PicamEnumeratedType_AcquisitionStateErrorsMask = 44
    #/*------------------------------------------------------------------------*/
    ))

PicamModelEnum = PI_Enum(
    "PicamModelEnum", {**dict(
    #/*------------------------------------------------------------------------*/
    #/* PI-MTE Series (1419) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMteSeries               = 1400,
    #/* PI-MTE 1024 Series ----------------------------------------------------*/
    PicamModel_PIMte1024Series           = 1401,
    PicamModel_PIMte1024F                = 1402,
    PicamModel_PIMte1024B                = 1403,
    PicamModel_PIMte1024BR               = 1405,
    PicamModel_PIMte1024BUV              = 1404,
    #/* PI-MTE 1024FT Series --------------------------------------------------*/
    PicamModel_PIMte1024FTSeries         = 1406,
    PicamModel_PIMte1024FT               = 1407,
    PicamModel_PIMte1024BFT              = 1408,
    #/* PI-MTE 1300 Series ----------------------------------------------------*/
    PicamModel_PIMte1300Series           = 1412,
    PicamModel_PIMte1300B                = 1413,
    PicamModel_PIMte1300R                = 1414,
    PicamModel_PIMte1300BR               = 1415,
    #/* PI-MTE 2048 Series ----------------------------------------------------*/
    PicamModel_PIMte2048Series           = 1416,
    PicamModel_PIMte2048B                = 1417,
    PicamModel_PIMte2048BR               = 1418,
    #/* PI-MTE 2K Series ------------------------------------------------------*/
    PicamModel_PIMte2KSeries             = 1409,
    PicamModel_PIMte2KB                  = 1410,
    PicamModel_PIMte2KBUV                = 1411,
    #/*------------------------------------------------------------------------*/
    #/* PI-MTE3 Series (2006) -------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMte3Series              = 2000,
    #/* PI-MTE3 2048 Series ---------------------------------------------------*/
    PicamModel_PIMte32048Series          = 2001,
    PicamModel_PIMte32048B               = 2002,
    #/* PI-MTE3 4096 Series ---------------------------------------------------*/
    PicamModel_PIMte34096Series          = 2003,
    PicamModel_PIMte34096B               = 2004,
    PicamModel_PIMte34096B_2             = 2005,
    #/*------------------------------------------------------------------------*/
    #/* PIXIS Series (76) -----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PixisSeries               =    0,
    #/* PIXIS 100 Series ------------------------------------------------------*/
    PicamModel_Pixis100Series            =    1,
    PicamModel_Pixis100F                 =    2,
    PicamModel_Pixis100B                 =    6,
    PicamModel_Pixis100R                 =    3,
    PicamModel_Pixis100C                 =    4,
    PicamModel_Pixis100BR                =    5,
    PicamModel_Pixis100BExcelon          =   54,
    PicamModel_Pixis100BRExcelon         =   55,
    PicamModel_PixisXO100B               =    7,
    PicamModel_PixisXO100BR              =    8,
    PicamModel_PixisXB100B               =   68,
    PicamModel_PixisXB100BR              =   69,
    #/* PIXIS 256 Series ------------------------------------------------------*/
    PicamModel_Pixis256Series            =   26,
    PicamModel_Pixis256F                 =   27,
    PicamModel_Pixis256B                 =   29,
    PicamModel_Pixis256E                 =   28,
    PicamModel_Pixis256BR                =   30,
    PicamModel_PixisXB256BR              =   31,
    #/* PIXIS 400 Series ------------------------------------------------------*/
    PicamModel_Pixis400Series            =   37,
    PicamModel_Pixis400F                 =   38,
    PicamModel_Pixis400B                 =   40,
    PicamModel_Pixis400R                 =   39,
    PicamModel_Pixis400BR                =   41,
    PicamModel_Pixis400BExcelon          =   56,
    PicamModel_Pixis400BRExcelon         =   57,
    PicamModel_PixisXO400B               =   42,
    PicamModel_PixisXB400BR              =   70,
    #/* PIXIS 512 Series ------------------------------------------------------*/
    PicamModel_Pixis512Series            =   43,
    PicamModel_Pixis512F                 =   44,
    PicamModel_Pixis512B                 =   45,
    PicamModel_Pixis512BUV               =   46,
    PicamModel_Pixis512BExcelon          =   58,
    PicamModel_PixisXO512F               =   49,
    PicamModel_PixisXO512B               =   50,
    PicamModel_PixisXF512F               =   48,
    PicamModel_PixisXF512B               =   47,
    #/* PIXIS 1024 Series -----------------------------------------------------*/
    PicamModel_Pixis1024Series           =    9,
    PicamModel_Pixis1024F                =   10,
    PicamModel_Pixis1024B                =   11,
    PicamModel_Pixis1024BR               =   13,
    PicamModel_Pixis1024BUV              =   12,
    PicamModel_Pixis1024BExcelon         =   59,
    PicamModel_Pixis1024BRExcelon        =   60,
    PicamModel_PixisXO1024F              =   16,
    PicamModel_PixisXO1024B              =   14,
    PicamModel_PixisXO1024BR             =   15,
    PicamModel_PixisXF1024F              =   17,
    PicamModel_PixisXF1024B              =   18,
    PicamModel_PixisXB1024BR             =   71,
    #/* PIXIS 1300 Series -----------------------------------------------------*/
    PicamModel_Pixis1300Series           =   51,
    PicamModel_Pixis1300F                =   52,
    PicamModel_Pixis1300F_2              =   75,
    PicamModel_Pixis1300B                =   53,
    PicamModel_Pixis1300BR               =   73,
    PicamModel_Pixis1300BExcelon         =   61,
    PicamModel_Pixis1300BRExcelon        =   62,
    PicamModel_PixisXO1300B              =   65,
    PicamModel_PixisXF1300B              =   66,
    PicamModel_PixisXB1300R              =   72,
    #/* PIXIS 2048 Series -----------------------------------------------------*/
    PicamModel_Pixis2048Series           =   20,
    PicamModel_Pixis2048F                =   21,
    PicamModel_Pixis2048B                =   22,
    PicamModel_Pixis2048BR               =   67,
    PicamModel_Pixis2048BExcelon         =   63,
    PicamModel_Pixis2048BRExcelon        =   74,
    PicamModel_PixisXO2048B              =   23,
    PicamModel_PixisXF2048F              =   25,
    PicamModel_PixisXF2048B              =   24,
    #/* PIXIS 2K Series -------------------------------------------------------*/
    PicamModel_Pixis2KSeries             =   32,
    PicamModel_Pixis2KF                  =   33,
    PicamModel_Pixis2KB                  =   34,
    PicamModel_Pixis2KBUV                =   36,
    PicamModel_Pixis2KBExcelon           =   64,
    PicamModel_PixisXO2KB                =   35,
    ), **dict(
    #/*------------------------------------------------------------------------*/
    #/* Quad-RO Series (104) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_QuadroSeries              =  100,
    PicamModel_Quadro4096                =  101,
    PicamModel_Quadro4096_2              =  103,
    PicamModel_Quadro4320                =  102,
    #/*------------------------------------------------------------------------*/
    #/* ProEM Series (214) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMSeries               =  200,
    #/* ProEM 512 Series ------------------------------------------------------*/
    PicamModel_ProEM512Series            =  203,
    PicamModel_ProEM512B                 =  201,
    PicamModel_ProEM512BK                =  205,
    PicamModel_ProEM512BExcelon          =  204,
    PicamModel_ProEM512BKExcelon         =  206,
    #/* ProEM 1024 Series -----------------------------------------------------*/
    PicamModel_ProEM1024Series           =  207,
    PicamModel_ProEM1024B                =  202,
    PicamModel_ProEM1024BExcelon         =  208,
    #/* ProEM 1600 Series -----------------------------------------------------*/
    PicamModel_ProEM1600Series           =  209,
    PicamModel_ProEM1600xx2B             =  212,
    PicamModel_ProEM1600xx2BExcelon      =  210,
    PicamModel_ProEM1600xx4B             =  213,
    PicamModel_ProEM1600xx4BExcelon      =  211,
    #/*------------------------------------------------------------------------*/
    #/* ProEM+ Series (614) ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMPlusSeries           =  600,
    #/* ProEM+ 512 Series -----------------------------------------------------*/
    PicamModel_ProEMPlus512Series        =  603,
    PicamModel_ProEMPlus512B             =  601,
    PicamModel_ProEMPlus512BK            =  605,
    PicamModel_ProEMPlus512BExcelon      =  604,
    PicamModel_ProEMPlus512BKExcelon     =  606,
    #/* ProEM+ 1024 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1024Series       =  607,
    PicamModel_ProEMPlus1024B            =  602,
    PicamModel_ProEMPlus1024BExcelon     =  608,
    #/* ProEM+ 1600 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1600Series       =  609,
    PicamModel_ProEMPlus1600xx2B         =  612,
    PicamModel_ProEMPlus1600xx2BExcelon  =  610,
    PicamModel_ProEMPlus1600xx4B         =  613,
    PicamModel_ProEMPlus1600xx4BExcelon  =  611,
    #/*------------------------------------------------------------------------*/
    #/* ProEM-HS Series (1218) ------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMHSSeries             = 1200,
    #/* ProEM-HS 512 Series ---------------------------------------------------*/
    PicamModel_ProEMHS512Series          = 1201,
    PicamModel_ProEMHS512B               = 1202,
    PicamModel_ProEMHS512BK              = 1207,
    PicamModel_ProEMHS512BExcelon        = 1203,
    PicamModel_ProEMHS512BKExcelon       = 1208,
    PicamModel_ProEMHS512B_2             = 1216,
    PicamModel_ProEMHS512BExcelon_2      = 1217,
    #/* ProEM-HS 1024 Series --------------------------------------------------*/
    PicamModel_ProEMHS1024Series         = 1204,
    PicamModel_ProEMHS1024B              = 1205,
    PicamModel_ProEMHS1024BExcelon       = 1206,
    PicamModel_ProEMHS1024B_2            = 1212,
    PicamModel_ProEMHS1024BExcelon_2     = 1213,
    PicamModel_ProEMHS1024B_3            = 1214,
    PicamModel_ProEMHS1024BExcelon_3     = 1215,
    #/* ProEM-HS 1K-10 Series -------------------------------------------------*/
    PicamModel_ProEMHS1K10Series         = 1209,
    PicamModel_ProEMHS1KB10              = 1210,
    PicamModel_ProEMHS1KB10Excelon       = 1211,
    #/*------------------------------------------------------------------------*/
    #/* PI-MAX3 Series (303) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMax3Series              =  300,
    PicamModel_PIMax31024I               =  301,
    PicamModel_PIMax31024x256            =  302,
    #/*------------------------------------------------------------------------*/
    #/* PI-MAX4 Series (721) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMax4Series              =  700,
    #/* PI-MAX4 1024i Series --------------------------------------------------*/
    PicamModel_PIMax41024ISeries         =  703,
    PicamModel_PIMax41024I               =  701,
    PicamModel_PIMax41024IRF             =  704,
    #/* PI-MAX4 1024f Series --------------------------------------------------*/
    PicamModel_PIMax41024FSeries         =  710,
    PicamModel_PIMax41024F               =  711,
    PicamModel_PIMax41024FRF             =  712,
    #/* PI-MAX4 1024x256 Series -----------------------------------------------*/
    PicamModel_PIMax41024x256Series      =  705,
    PicamModel_PIMax41024x256            =  702,
    PicamModel_PIMax41024x256RF          =  706,
    #/* PI-MAX4 2048 Series ---------------------------------------------------*/
    PicamModel_PIMax42048Series          =  716,
    PicamModel_PIMax42048F               =  717,
    PicamModel_PIMax42048B               =  718,
    PicamModel_PIMax42048FRF             =  719,
    PicamModel_PIMax42048BRF             =  720,
    #/* PI-MAX4 512EM Series --------------------------------------------------*/
    PicamModel_PIMax4512EMSeries         =  708,
    PicamModel_PIMax4512EM               =  707,
    PicamModel_PIMax4512BEM              =  709,
    #/* PI-MAX4 1024EM Series -------------------------------------------------*/
    PicamModel_PIMax41024EMSeries        =  713,
    PicamModel_PIMax41024EM              =  715,
    PicamModel_PIMax41024BEM             =  714,
    ), **dict(
    #/*------------------------------------------------------------------------*/
    #/* PyLoN Series (439) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PylonSeries               =  400,
    #/* PyLoN 100 Series ------------------------------------------------------*/
    PicamModel_Pylon100Series            =  418,
    PicamModel_Pylon100F                 =  404,
    PicamModel_Pylon100B                 =  401,
    PicamModel_Pylon100BR                =  407,
    PicamModel_Pylon100BExcelon          =  425,
    PicamModel_Pylon100BRExcelon         =  426,
    #/* PyLoN 256 Series ------------------------------------------------------*/
    PicamModel_Pylon256Series            =  419,
    PicamModel_Pylon256F                 =  409,
    PicamModel_Pylon256B                 =  410,
    PicamModel_Pylon256E                 =  411,
    PicamModel_Pylon256BR                =  412,
    #/* PyLoN 400 Series ------------------------------------------------------*/
    PicamModel_Pylon400Series            =  420,
    PicamModel_Pylon400F                 =  405,
    PicamModel_Pylon400B                 =  402,
    PicamModel_Pylon400BR                =  408,
    PicamModel_Pylon400BExcelon          =  427,
    PicamModel_Pylon400BRExcelon         =  428,
    #/* PyLoN 1024 Series -----------------------------------------------------*/
    PicamModel_Pylon1024Series           =  421,
    PicamModel_Pylon1024B                =  417,
    PicamModel_Pylon1024BExcelon         =  429,
    #/* PyLoN 1300 Series -----------------------------------------------------*/
    PicamModel_Pylon1300Series           =  422,
    PicamModel_Pylon1300F                =  406,
    PicamModel_Pylon1300B                =  403,
    PicamModel_Pylon1300R                =  438,
    PicamModel_Pylon1300BR               =  432,
    PicamModel_Pylon1300BExcelon         =  430,
    PicamModel_Pylon1300BRExcelon        =  433,
    #/* PyLoN 2048 Series -----------------------------------------------------*/
    PicamModel_Pylon2048Series           =  423,
    PicamModel_Pylon2048F                =  415,
    PicamModel_Pylon2048B                =  434,
    PicamModel_Pylon2048BR               =  416,
    PicamModel_Pylon2048BExcelon         =  435,
    PicamModel_Pylon2048BRExcelon        =  436,
    #/* PyLoN 2K Series -------------------------------------------------------*/
    PicamModel_Pylon2KSeries             =  424,
    PicamModel_Pylon2KF                  =  413,
    PicamModel_Pylon2KB                  =  414,
    PicamModel_Pylon2KBUV                =  437,
    PicamModel_Pylon2KBExcelon           =  431,
    #/*------------------------------------------------------------------------*/
    #/* PyLoN-IR Series (904) -------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PylonirSeries             =  900,
    #/* PyLoN-IR 1024 Series --------------------------------------------------*/
    PicamModel_Pylonir1024Series         =  901,
    PicamModel_Pylonir102422             =  902,
    PicamModel_Pylonir102417             =  903,
    #/*------------------------------------------------------------------------*/
    #/* PIoNIR Series (502) ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PionirSeries              =  500,
    PicamModel_Pionir640                 =  501,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana Series (802) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaSeries             =  800,
    PicamModel_Nirvana640                =  801,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana ST Series (1302) ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaSTSeries           = 1300,
    PicamModel_NirvanaST640              = 1301,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana-LN Series (1102) ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaLNSeries           = 1100,
    PicamModel_NirvanaLN640              = 1101,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana HS Series (2202) ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaHSSeries           = 2200,
    PicamModel_NirvanaHS                 = 2201,
    #/*------------------------------------------------------------------------*/
    #/* SOPHIA Series (1845) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_SophiaSeries              = 1800,
    #/* SOPHIA 2048 Series ----------------------------------------------------*/
    PicamModel_Sophia2048Series          = 1801,
    PicamModel_Sophia2048B               = 1802,
    PicamModel_Sophia2048BExcelon        = 1803,
    PicamModel_SophiaXO2048B             = 1804,
    PicamModel_SophiaXF2048B             = 1805,
    PicamModel_SophiaXB2048B             = 1806,
    #/* SOPHIA 2048-13.5 Series -----------------------------------------------*/
    PicamModel_Sophia2048135Series       = 1807,
    PicamModel_Sophia2048135             = 1808,
    PicamModel_Sophia2048B135            = 1809,
    PicamModel_Sophia2048BR135           = 1810,
    PicamModel_Sophia2048BUV135          = 1844,
    PicamModel_Sophia2048B135Excelon     = 1811,
    PicamModel_Sophia2048BR135Excelon    = 1812,
    PicamModel_SophiaXO2048B135          = 1813,
    PicamModel_SophiaXO2048BR135         = 1814,
    PicamModel_Sophia2048B135Excelon_2   = 1840,
    #/* SOPHIA 4096 Series ----------------------------------------------------*/
    PicamModel_Sophia4096Series          = 1826,
    PicamModel_Sophia4096B               = 1827,
    PicamModel_SophiaXO4096B             = 1829,
    PicamModel_SophiaXF4096B             = 1830,
    PicamModel_SophiaXB4096B             = 1831,
    PicamModel_Sophia4096B_2             = 1841,
    #/* SOPHIA 4096-HDR Series ------------------------------------------------*/
    PicamModel_Sophia4096HdrSeries       = 1832,
    PicamModel_Sophia4096BHdr            = 1833,
    PicamModel_Sophia4096BRHdr           = 1834,
    PicamModel_SophiaXO4096BHdr          = 1837,
    PicamModel_SophiaXO4096BRHdr         = 1838,
    PicamModel_SophiaXF4096BHdr          = 1839,
    PicamModel_SophiaXF4096BRHdr         = 1828,
    PicamModel_SophiaXB4096BHdr          = 1835,
    PicamModel_SophiaXB4096BRHdr         = 1836,
    PicamModel_Sophia4096BHdr_2          = 1842,
    PicamModel_Sophia4096BRHdr_2         = 1843,
    ), **dict(
    #/*------------------------------------------------------------------------*/
    #/* BLAZE Series (1519) ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_BlazeSeries               = 1500,
    #/* BLAZE 100 Series ------------------------------------------------------*/
    PicamModel_Blaze100Series            = 1507,
    PicamModel_Blaze100B                 = 1501,
    PicamModel_Blaze100BR                = 1505,
    PicamModel_Blaze100HR                = 1503,
    PicamModel_Blaze100BRLD              = 1509,
    PicamModel_Blaze100BExcelon          = 1511,
    PicamModel_Blaze100BRExcelon         = 1513,
    PicamModel_Blaze100HRExcelon         = 1515,
    PicamModel_Blaze100BRLDExcelon       = 1517,
    #/* BLAZE 400 Series ------------------------------------------------------*/
    PicamModel_Blaze400Series            = 1508,
    PicamModel_Blaze400B                 = 1502,
    PicamModel_Blaze400BR                = 1506,
    PicamModel_Blaze400HR                = 1504,
    PicamModel_Blaze400BRLD              = 1510,
    PicamModel_Blaze400BExcelon          = 1512,
    PicamModel_Blaze400BRExcelon         = 1514,
    PicamModel_Blaze400HRExcelon         = 1516,
    PicamModel_Blaze400BRLDExcelon       = 1518,
    #/*------------------------------------------------------------------------*/
    #/* FERGIE Series (1612) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_FergieSeries              = 1600,
    #/* FERGIE 256 Series -----------------------------------------------------*/
    PicamModel_Fergie256Series           = 1601,
    PicamModel_Fergie256B                = 1602,
    PicamModel_Fergie256BR               = 1607,
    PicamModel_Fergie256BExcelon         = 1603,
    PicamModel_Fergie256BRExcelon        = 1608,
    #/* FERGIE 256FT Series ---------------------------------------------------*/
    PicamModel_Fergie256FTSeries         = 1604,
    PicamModel_Fergie256FFT              = 1609,
    PicamModel_Fergie256BFT              = 1605,
    PicamModel_Fergie256BRFT             = 1610,
    PicamModel_Fergie256BFTExcelon       = 1606,
    PicamModel_Fergie256BRFTExcelon      = 1611,
    #/*------------------------------------------------------------------------*/
    #/* FERGIE-ISO-81 Series (2104) -------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_FergieIso81Series         = 2100,
    #/* FERGIE-ISO-81 256FT Series --------------------------------------------*/
    PicamModel_FergieIso81256FTSeries    = 2101,
    PicamModel_FergieIso81256BFTExcelon  = 2102,
    PicamModel_FergieIso81256BRFTExcelon = 2103,
    #/*------------------------------------------------------------------------*/
    #/* FERGIE Accessory Series (1707) ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_FergieAccessorySeries     = 1700,
    #/* FERGIE Lamp Series ----------------------------------------------------*/
    PicamModel_FergieLampSeries          = 1701,
    PicamModel_FergieAEL                 = 1702,
    PicamModel_FergieQTH                 = 1703,
    #/* FERGIE Laser Series ---------------------------------------------------*/
    PicamModel_FergieLaserSeries         = 1704,
    PicamModel_FergieLaser785            = 1705,
    PicamModel_FergieLaser532            = 1706,
    #/*------------------------------------------------------------------------*/
    #/* KURO Series (1904) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_KuroSeries                = 1900,
    PicamModel_Kuro1200B                 = 1901,
    PicamModel_Kuro1608B                 = 1902,
    PicamModel_Kuro2048B                 = 1903,
    #/*------------------------------------------------------------------------*/
    #/* IntelliCal Accessory Series (2603) ------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_IntellicalAccessorySeries = 2600,
    #/* IntelliCal Lamp Series ------------------------------------------------*/
    PicamModel_IntellicalLampSeries      = 2601,
    PicamModel_IntellicalSwirQTH         = 2602,
    #/*------------------------------------------------------------------------*/
    #/* TPIR Series (2304) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_TpirSeries                = 2300,
    #/* TPIR-785 Series -------------------------------------------------------*/
    PicamModel_Tpir785Series             = 2301,
    PicamModel_Tpir785100                = 2302,
    PicamModel_Tpir785400                = 2303,
    #/*------------------------------------------------------------------------*/
    #/* TPIR HR Series (2404) -------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_TpirHRSeries              = 2400,
    #/* TPIR-785 HR Series ----------------------------------------------------*/
    PicamModel_Tpir785HRSeries           = 2401,
    PicamModel_Tpir785HR100              = 2402,
    PicamModel_Tpir785HR400              = 2403
    #/*------------------------------------------------------------------------*/
    )})

PicamComputerInterfaceEnum = PI_Enum(
    "PicamComputerInterface", dict(
    PicamComputerInterface_Usb2            = 1,
    PicamComputerInterface_1394A           = 2,
    PicamComputerInterface_GigabitEthernet = 3,
    PicamComputerInterface_Usb3            = 4                                
    ))

PicamStringSizeEnum = PI_Enum(
    "PicamStringSize", dict(
    PicamStringSize_SensorName     =  64,
    PicamStringSize_SerialNumber   =  64,
    PicamStringSize_FirmwareName   =  64,
    PicamStringSize_FirmwareDetail = 256                       
    ))

class PicamFirmwareDetail(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char * PicamStringSizeEnum.bysname['FirmwareName']),
                ("detail", ctypes.c_char * PicamStringSizeEnum.bysname['FirmwareDetail'])]

class PicamCameraID(ctypes.Structure):
    _fields_ = [("model", ctypes.c_int),
                ("PicamComputerInterface", ctypes.c_int),
                ("sensor_name", pichar * PicamStringSizeEnum.bysname['SensorName']),
                ("serial_number", pichar * PicamStringSizeEnum.bysname['SerialNumber'])
                ]

PicamHandle = ctypes.c_void_p

PicamValueTypeEnum  = PI_Enum(
    "PicamValueType",  dict(
    #/*------------------------------------------------------------------------*/
    #/* Integral Types --------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Integer       = 1,
    PicamValueType_Boolean       = 3,
    PicamValueType_Enumeration   = 4,
    #/*------------------------------------------------------------------------*/
    #/* Large Integral Type ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_LargeInteger  = 6,
    #/*------------------------------------------------------------------------*/
    #/* Floating Point Type ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_FloatingPoint = 2,
    #/*------------------------------------------------------------------------*/
    #/* Regions of Interest Type ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Rois          = 5,
    #/*------------------------------------------------------------------------*/
    #/* Pulse Type ------------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Pulse         = 7,
    #/*------------------------------------------------------------------------*/
    #/* Custom Intensifier Modulation Sequence Type ---------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Modulations   = 8
    #/*------------------------------------------------------------------------*/
    ))

PicamConstraintTypeEnum = PI_Enum(
    "PicamConstraintType", dict(
    PicamConstraintType_None        = 1,
    PicamConstraintType_Range       = 2,
    PicamConstraintType_Collection  = 3,
    PicamConstraintType_Rois        = 4,
    PicamConstraintType_Pulse       = 5,
    PicamConstraintType_Modulations = 6
    ))

class PI_Param(object):

    def __init__(self, param_type,constraint_type, offset_n):
        
        self.name = None
        self.param_type = param_type
        self.constraint_type = constraint_type
        n = self.offset_n = offset_n
        c = PicamConstraintTypeEnum.bysname[self.constraint_type]
        v = PicamValueTypeEnum.bysname[self.param_type]
        self.enum = (c<<24)+(v<<16)+(n)

PicamParameter = OrderedDict([
#define PI_V(v,c,n) (((PicamConstraintType_##c)<<24)+((PicamValueType_##v)<<16)+(n))
    #/***************************************************************************************/
    #/* Camera Parameters *******************************************************************/
    #/***************************************************************************************/
    #/*-------------------------------------------------------------------------------------*/
    #/* Shutter Timing ---------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ExposureTime"                      , PI_Param("FloatingPoint", "Range",        23) ),
    ("PicamParameter_ShutterTimingMode"                 , PI_Param("Enumeration",   "Collection",   24) ),
    ("PicamParameter_ShutterOpeningDelay"               , PI_Param("FloatingPoint", "Range",        46) ),
    ("PicamParameter_ShutterClosingDelay"               , PI_Param("FloatingPoint", "Range",        25) ),
    ("PicamParameter_ShutterDelayResolution"            , PI_Param("FloatingPoint", "Collection",   47) ),
    ("PicamParameter_InternalShutterType"               , PI_Param("Enumeration",   "None",        139) ),
    ("PicamParameter_InternalShutterStatus"             , PI_Param("Enumeration",   "None",        153) ),
    ("PicamParameter_ExternalShutterType"               , PI_Param("Enumeration",   "None",        152) ),
    ("PicamParameter_ExternalShutterStatus"             , PI_Param("Enumeration",   "None",        154) ),
    ("PicamParameter_ActiveShutter"                     , PI_Param("Enumeration",   "Collection",  155) ),
    ("PicamParameter_InactiveShutterTimingModeResult"   , PI_Param("Enumeration",   "None",        156) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Gating -----------------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_GatingMode"                        , PI_Param("Enumeration",   "Collection",   93) ),
    ("PicamParameter_RepetitiveGate"                    , PI_Param("Pulse",         "Pulse",        94) ),
    ("PicamParameter_SequentialStartingGate"            , PI_Param("Pulse",         "Pulse",        95) ),
    ("PicamParameter_SequentialEndingGate"              , PI_Param("Pulse",         "Pulse",        96) ),
    ("PicamParameter_SequentialGateStepCount"           , PI_Param("LargeInteger",  "Range",        97) ),
    ("PicamParameter_SequentialGateStepIterations"      , PI_Param("LargeInteger",  "Range",        98) ),
    ("PicamParameter_DifStartingGate"                   , PI_Param("Pulse",         "Pulse",       102) ),
    ("PicamParameter_DifEndingGate"                     , PI_Param("Pulse",         "Pulse",       103) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Intensifier ------------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_EnableIntensifier"                 , PI_Param("Boolean",       "Collection",   86) ),
    ("PicamParameter_IntensifierStatus"                 , PI_Param("Enumeration",   "None",         87) ),
    ("PicamParameter_IntensifierGain"                   , PI_Param("Integer",       "Range",        88) ),
    ("PicamParameter_EMIccdGainControlMode"             , PI_Param("Enumeration",   "Collection",  123) ),
    ("PicamParameter_EMIccdGain"                        , PI_Param("Integer",       "Range",       124) ),
    ("PicamParameter_PhosphorDecayDelay"                , PI_Param("FloatingPoint", "Range",        89) ),
    ("PicamParameter_PhosphorDecayDelayResolution"      , PI_Param("FloatingPoint", "Collection",   90) ),
    ("PicamParameter_BracketGating"                     , PI_Param("Boolean",       "Collection",  100) ),
    ("PicamParameter_IntensifierOptions"                , PI_Param("Enumeration",   "None",        101) ),
    ("PicamParameter_EnableModulation"                  , PI_Param("Boolean",       "Collection",  111) ),
    ("PicamParameter_ModulationDuration"                , PI_Param("FloatingPoint", "Range",       118) ),
    ("PicamParameter_ModulationFrequency"               , PI_Param("FloatingPoint", "Range",       112) ),
    ("PicamParameter_RepetitiveModulationPhase"         , PI_Param("FloatingPoint", "Range",       113) ),
    ("PicamParameter_SequentialStartingModulationPhase" , PI_Param("FloatingPoint", "Range",       114) ),
    ("PicamParameter_SequentialEndingModulationPhase"   , PI_Param("FloatingPoint", "Range",       115) ),
    ("PicamParameter_CustomModulationSequence"          , PI_Param("Modulations",   "Modulations", 119) ),
    ("PicamParameter_PhotocathodeSensitivity"           , PI_Param("Enumeration",   "None",        107) ),
    ("PicamParameter_GatingSpeed"                       , PI_Param("Enumeration",   "None",        108) ),
    ("PicamParameter_PhosphorType"                      , PI_Param("Enumeration",   "None",        109) ),
    ("PicamParameter_IntensifierDiameter"               , PI_Param("FloatingPoint", "None",        110) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Analog to Digital Conversion -------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_AdcSpeed"                          , PI_Param("FloatingPoint", "Collection",   33) ),
    ("PicamParameter_AdcBitDepth"                       , PI_Param("Integer",       "Collection",   34) ),
    ("PicamParameter_AdcAnalogGain"                     , PI_Param("Enumeration",   "Collection",   35) ),
    ("PicamParameter_AdcQuality"                        , PI_Param("Enumeration",   "Collection",   36) ),
    ("PicamParameter_AdcEMGain"                         , PI_Param("Integer",       "Range",        53) ),
    ("PicamParameter_CorrectPixelBias"                  , PI_Param("Boolean",       "Collection",  106) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Hardware I/O -----------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_TriggerSource"                     , PI_Param("Enumeration",   "Collection",   79) ),
    ("PicamParameter_TriggerResponse"                   , PI_Param("Enumeration",   "Collection",   30) ),
    ("PicamParameter_TriggerDetermination"              , PI_Param("Enumeration",   "Collection",   31) ),
    ("PicamParameter_TriggerFrequency"                  , PI_Param("FloatingPoint", "Range",        80) ),
    ("PicamParameter_TriggerTermination"                , PI_Param("Enumeration",   "Collection",   81) ),
    ("PicamParameter_TriggerCoupling"                   , PI_Param("Enumeration",   "Collection",   82) ),
    ("PicamParameter_TriggerThreshold"                  , PI_Param("FloatingPoint", "Range",        83) ),
    ("PicamParameter_TriggerDelay"                      , PI_Param("FloatingPoint", "Range",       164) ),    
    ("PicamParameter_OutputSignal"                      , PI_Param("Enumeration",   "Collection",   32) ),
    ("PicamParameter_InvertOutputSignal"                , PI_Param("Boolean",       "Collection",   52) ),
    ("PicamParameter_OutputSignal2"                     , PI_Param("Enumeration",   "Collection",  150) ),
    ("PicamParameter_InvertOutputSignal2"               , PI_Param("Boolean",       "Collection",  151) ),
    ("PicamParameter_EnableAuxOutput"                   , PI_Param("Boolean",       "Collection",  161) ),    
    ("PicamParameter_AuxOutput"                         , PI_Param("Pulse",         "Pulse",        91) ),
    ("PicamParameter_EnableSyncMaster"                  , PI_Param("Boolean",       "Collection",   84) ),
    ("PicamParameter_SyncMaster2Delay"                  , PI_Param("FloatingPoint", "Range",        85) ),
    ("PicamParameter_EnableModulationOutputSignal"      , PI_Param("Boolean",       "Collection",  116) ),
    ("PicamParameter_ModulationOutputSignalFrequency"   , PI_Param("FloatingPoint", "Range",       117) ),
    ("PicamParameter_ModulationOutputSignalAmplitude"   , PI_Param("FloatingPoint", "Range",       120) ),
    ("PicamParameter_AnticipateTrigger"                 , PI_Param("Boolean",       "Collection",  131) ),
    ("PicamParameter_DelayFromPreTrigger"               , PI_Param("FloatingPoint", "Range",       132) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Readout Control --------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ReadoutControlMode"                , PI_Param("Enumeration",   "Collection",   26) ),
    ("PicamParameter_ReadoutTimeCalculation"            , PI_Param("FloatingPoint", "None",         27) ),
    ("PicamParameter_ReadoutPortCount"                  , PI_Param("Integer",       "Collection",   28) ),
    ("PicamParameter_ReadoutOrientation"                , PI_Param("Enumeration",   "None",         54) ),
    ("PicamParameter_KineticsWindowHeight"              , PI_Param("Integer",       "Range",        56) ),
    ("PicamParameter_SeNsRWindowHeight"                 , PI_Param("Integer",       "Range",       163) ),
    ("PicamParameter_VerticalShiftRate"                 , PI_Param("FloatingPoint", "Collection",   13) ),
    ("PicamParameter_Accumulations"                     , PI_Param("LargeInteger",  "Range",        92) ),
    ("PicamParameter_EnableNondestructiveReadout"       , PI_Param("Boolean",       "Collection",  128) ),
    ("PicamParameter_NondestructiveReadoutPeriod"       , PI_Param("FloatingPoint", "Range",       129) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Data Acquisition -------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_Rois"                              , PI_Param("Rois",          "Rois",         37) ),
    ("PicamParameter_NormalizeOrientation"              , PI_Param("Boolean",       "Collection",   39) ),
    ("PicamParameter_DisableDataFormatting"             , PI_Param("Boolean",       "Collection",   55) ),
    ("PicamParameter_ReadoutCount"                      , PI_Param("LargeInteger",  "Range",        40) ),
    ("PicamParameter_ExactReadoutCountMaximum"          , PI_Param("LargeInteger",  "None",         77) ),
    ("PicamParameter_PhotonDetectionMode"               , PI_Param("Enumeration",   "Collection",  125) ),
    ("PicamParameter_PhotonDetectionThreshold"          , PI_Param("FloatingPoint", "Range",       126) ),
    ("PicamParameter_PixelFormat"                       , PI_Param("Enumeration",   "Collection",   41) ),
    ("PicamParameter_FrameSize"                         , PI_Param("Integer",       "None",         42) ),
    ("PicamParameter_FrameStride"                       , PI_Param("Integer",       "None",         43) ),
    ("PicamParameter_FramesPerReadout"                  , PI_Param("Integer",       "None",         44) ),
    ("PicamParameter_ReadoutStride"                     , PI_Param("Integer",       "None",         45) ),
    ("PicamParameter_PixelBitDepth"                     , PI_Param("Integer",       "None",         48) ),
    ("PicamParameter_ReadoutRateCalculation"            , PI_Param("FloatingPoint", "None",         50) ),
    ("PicamParameter_OnlineReadoutRateCalculation"      , PI_Param("FloatingPoint", "None",         99) ),
    ("PicamParameter_FrameRateCalculation"              , PI_Param("FloatingPoint", "None",         51) ),
    ("PicamParameter_Orientation"                       , PI_Param("Enumeration",   "None",         38) ),
    ("PicamParameter_TimeStamps"                        , PI_Param("Enumeration",   "Collection",   68) ),
    ("PicamParameter_TimeStampResolution"               , PI_Param("LargeInteger",  "Collection",   69) ),
    ("PicamParameter_TimeStampBitDepth"                 , PI_Param("Integer",       "Collection",   70) ),
    ("PicamParameter_TrackFrames"                       , PI_Param("Boolean",       "Collection",   71) ),
    ("PicamParameter_FrameTrackingBitDepth"             , PI_Param("Integer",       "Collection",   72) ),
    ("PicamParameter_GateTracking"                      , PI_Param("Enumeration",   "Collection",  104) ),
    ("PicamParameter_GateTrackingBitDepth"              , PI_Param("Integer",       "Collection",  105) ),
    ("PicamParameter_ModulationTracking"                , PI_Param("Enumeration",   "Collection",  121) ),
    ("PicamParameter_ModulationTrackingBitDepth"        , PI_Param("Integer",       "Collection",  122) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Information -----------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_SensorType"                        , PI_Param("Enumeration",   "None",         57) ),
    ("PicamParameter_CcdCharacteristics"                , PI_Param("Enumeration",   "None",         58) ),
    ("PicamParameter_SensorActiveWidth"                 , PI_Param("Integer",       "None",         59) ),
    ("PicamParameter_SensorActiveHeight"                , PI_Param("Integer",       "None",         60) ),
    ("PicamParameter_SensorActiveExtendedHeight"        , PI_Param("Integer",       "None",        159) ),
    ("PicamParameter_SensorActiveLeftMargin"            , PI_Param("Integer",       "None",         61) ),
    ("PicamParameter_SensorActiveTopMargin"             , PI_Param("Integer",       "None",         62) ),
    ("PicamParameter_SensorActiveRightMargin"           , PI_Param("Integer",       "None",         63) ),
    ("PicamParameter_SensorActiveBottomMargin"          , PI_Param("Integer",       "None",         64) ),
    ("PicamParameter_SensorMaskedHeight"                , PI_Param("Integer",       "None",         65) ),
    ("PicamParameter_SensorMaskedTopMargin"             , PI_Param("Integer",       "None",         66) ),
    ("PicamParameter_SensorMaskedBottomMargin"          , PI_Param("Integer",       "None",         67) ),
    ("PicamParameter_SensorSecondaryMaskedHeight"       , PI_Param("Integer",       "None",         49) ),
    ("PicamParameter_SensorSecondaryActiveHeight"       , PI_Param("Integer",       "None",         74) ),
    ("PicamParameter_PixelWidth"                        , PI_Param("FloatingPoint", "None",          9) ),
    ("PicamParameter_PixelHeight"                       , PI_Param("FloatingPoint", "None",         10) ),
    ("PicamParameter_PixelGapWidth"                     , PI_Param("FloatingPoint", "None",         11) ),
    ("PicamParameter_PixelGapHeight"                    , PI_Param("FloatingPoint", "None",         12) ),
    ("PicamParameter_ApplicableStarDefectMapID"         , PI_Param("Integer",       "None",        166) ),
    
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Layout ----------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ActiveWidth"                       , PI_Param("Integer",       "Range",         1) ),
    ("PicamParameter_ActiveHeight"                      , PI_Param("Integer",       "Range",         2) ),
    ("PicamParameter_ActiveExtendedHeight"              , PI_Param("Integer",       "Range",       160) ),
    ("PicamParameter_ActiveLeftMargin"                  , PI_Param("Integer",       "Range",         3) ),
    ("PicamParameter_ActiveTopMargin"                   , PI_Param("Integer",       "Range",         4) ),
    ("PicamParameter_ActiveRightMargin"                 , PI_Param("Integer",       "Range",         5) ),
    ("PicamParameter_ActiveBottomMargin"                , PI_Param("Integer",       "Range",         6) ),
    ("PicamParameter_MaskedHeight"                      , PI_Param("Integer",       "Range",         7) ),
    ("PicamParameter_MaskedTopMargin"                   , PI_Param("Integer",       "Range",         8) ),
    ("PicamParameter_MaskedBottomMargin"                , PI_Param("Integer",       "Range",        73) ),
    ("PicamParameter_SecondaryMaskedHeight"             , PI_Param("Integer",       "Range",        75) ),
    ("PicamParameter_SecondaryActiveHeight"             , PI_Param("Integer",       "Range",        76) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Cleaning --------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_CleanSectionFinalHeight"           , PI_Param("Integer",       "Range",        17) ),
    ("PicamParameter_CleanSectionFinalHeightCount"      , PI_Param("Integer",       "Range",        18) ),
    ("PicamParameter_CleanSerialRegister"               , PI_Param("Boolean",       "Collection",   19) ),
    ("PicamParameter_CleanCycleCount"                   , PI_Param("Integer",       "Range",        20) ),
    ("PicamParameter_CleanCycleHeight"                  , PI_Param("Integer",       "Range",        21) ),
    ("PicamParameter_CleanBeforeExposure"               , PI_Param("Boolean",       "Collection",   78) ),
    ("PicamParameter_CleanUntilTrigger"                 , PI_Param("Boolean",       "Collection",   22) ),
    ("PicamParameter_StopCleaningOnPreTrigger"          , PI_Param("Boolean",       "Collection",  130) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Temperature -----------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_SensorTemperatureSetPoint"         , PI_Param("FloatingPoint", "Range",        14) ),
    ("PicamParameter_SensorTemperatureReading"          , PI_Param("FloatingPoint", "None",         15) ),
    ("PicamParameter_SensorTemperatureStatus"           , PI_Param("Enumeration",   "None",         16) ),
    ("PicamParameter_DisableCoolingFan"                 , PI_Param("Boolean",       "Collection",   29) ),
    ("PicamParameter_CoolingFanStatus"                  , PI_Param("Enumeration",   "None",        162) ),
    ("PicamParameter_EnableSensorWindowHeater"          , PI_Param("Boolean",       "Collection",  127) ),
    ("PicamParameter_VacuumStatus"                      , PI_Param("Enumeration",   "None",        165) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Spectrograph -----------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_CenterWavelengthSetPoint"          , PI_Param("FloatingPoint", "Range",       140) ),
    ("PicamParameter_CenterWavelengthReading"           , PI_Param("FloatingPoint", "None",        141) ),
    ("PicamParameter_CenterWavelengthStatus"            , PI_Param("Enumeration",   "None",        149) ),
    ("PicamParameter_GratingType"                       , PI_Param("Enumeration",   "None",        142) ),
    ("PicamParameter_GratingCoating"                    , PI_Param("Enumeration",   "None",        143) ),
    ("PicamParameter_GratingGrooveDensity"              , PI_Param("FloatingPoint", "None",        144) ),
    ("PicamParameter_GratingBlazingWavelength"          , PI_Param("FloatingPoint", "None",        145) ),
    ("PicamParameter_FocalLength"                       , PI_Param("FloatingPoint", "None",        146) ),
    ("PicamParameter_InclusionAngle"                    , PI_Param("FloatingPoint", "None",        147) ),
    ("PicamParameter_SensorAngle"                       , PI_Param("FloatingPoint", "None",        148) ),
    #/***************************************************************************************/
    #/* Camera/Accessory Parameters *********************************************************/
    #/***************************************************************************************/
    #/*-------------------------------------------------------------------------------------*/
    #/* Laser ------------------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_LaserOutputMode"                   , PI_Param("Enumeration",   "Collection",  137) ),
    ("PicamParameter_LaserPower"                        , PI_Param("FloatingPoint", "Range",       138) ),
    ("PicamParameter_LaserWavelength"                   , PI_Param("FloatingPoint", "None",        167) ),
    ("PicamParameter_LaserStatus"                       , PI_Param("Enumeration",   "None",        157) ),
    ("PicamParameter_InputTriggerStatus"                , PI_Param("Enumeration",   "None",        158) ),
    #/***************************************************************************************/
    #/* Accessory Parameters ****************************************************************/
    #/***************************************************************************************/
    #/*-------------------------------------------------------------------------------------*/
    #/* Lamp -------------------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_LightSource"                       , PI_Param("Enumeration",   "Collection",  133) ),
    ("PicamParameter_LightSourceStatus"                 , PI_Param("Enumeration",   "None",        134) ),
    ("PicamParameter_Age"                               , PI_Param("FloatingPoint", "None",        135) ),
    ("PicamParameter_LifeExpectancy"                    , PI_Param("FloatingPoint", "None",        136) )
     #/*-------------------------------------------------------------------------------------*/
    ])
for name,param in PicamParameter.items():
    param.name = name
    param.short_name = name.split("_")[1]
    if param.param_type == "Enumeration":
        if param.short_name in ["TimeStamps", "CcdCharacteristics", "Orientation"]:
            param.enum_type = f"Picam{param.short_name}MaskEnum"
        elif param.short_name == "ReadoutOrientation":
            param.enum_type = "PicamOrientationMaskEnum"
        else:
            param.enum_type = f"Picam{param.short_name}Enum"

PicamParam = dict()
for name, param in PicamParameter.items():
    PicamParam[param.short_name] = param

#provide a direct enum to parameters
PicamParameterEnum = PI_Enum(
    "PicamParameter",
    {name:param.enum for name,param in PicamParameter.items()})

class PicamRoi(ctypes.Structure):
    _fields_ = [("x", piint),
                ("width", piint),
                ("x_binning", piint),
                ("y", piint),
                ("height", piint),
                ("y_binning", piint),
                ]
    def __str__(self):
        return "PicamRoi: "+" ".join(["{}->{}; ".format(fname, getattr(self, fname))
                          for fname, ftype in self._fields_])
            
class PicamRois(ctypes.Structure):
    _fields_ = [("roi_array", ctypes.POINTER(PicamRoi)),
                ("roi_count", piint),
                ]
    
class PicamModulation(ctypes.Structure):
    _fields_ = [
        ("duration", ctypes.c_double),
        ("frequency", ctypes.c_double),
        ("phase", ctypes.c_double),
        ("output_signal_frequency", ctypes.c_double)
    ]

class PicamModulations(ctypes.Structure):
    _fields_ = [
        ("modulation_array", ctypes.POINTER(PicamModulation)),
        ("modulation_count", ctypes.c_int)
    ]

class PicamPulse(ctypes.Structure):
    _fields_ = [
        ("delay", ctypes.c_double),
        ("width", ctypes.c_double)
    ]

class PicamStatusPurview(ctypes.Structure):
    _fields_ = [
        ("values_array", ctypes.POINTER(ctypes.c_int)),
        ("values_count", ctypes.c_int)
    ]

class PicamCollectionConstraint(ctypes.Structure):
    _fields_ = [
        ("scope", ctypes.c_int),  # Assuming PicamConstraintScope is an enumeration
        ("severity", ctypes.c_int),  # Assuming PicamConstraintSeverity is an enumeration
        ("values_array", ctypes.POINTER(ctypes.c_double)),
        ("values_count", ctypes.c_int)
    ]

class PicamRangeConstraint(ctypes.Structure):
    _fields_ = [
        ("scope", ctypes.c_int),  # Assuming PicamConstraintScope is an enumeration
        ("severity", ctypes.c_int),  # Assuming PicamConstraintSeverity is an enumeration
        ("empty_set", ctypes.c_int),  # Assuming pibln is an integer
        ("minimum", ctypes.c_double),
        ("maximum", ctypes.c_double),
        ("increment", ctypes.c_double),
        ("excluded_values_array", ctypes.POINTER(ctypes.c_double)),
        ("excluded_values_count", ctypes.c_int),
        ("outlying_values_array", ctypes.POINTER(ctypes.c_double)),
        ("outlying_values_count", ctypes.c_int)
    ]

class PicamRoisConstraint(ctypes.Structure):
    _fields_ = [
        ("scope", ctypes.c_int),  # Assuming PicamConstraintScope is an enumeration
        ("severity", ctypes.c_int),  # Assuming PicamConstraintSeverity is an enumeration
        ("empty_set", ctypes.c_int),  # Assuming pibln is an integer
        ("rules", ctypes.c_uint),  # Assuming PicamRoisConstraintRulesMask is an unsigned integer
        ("maximum_roi_count", ctypes.c_int),
        ("x_constraint", PicamRangeConstraint),
        ("width_constraint", PicamRangeConstraint),
        ("x_binning_limits_array", ctypes.POINTER(ctypes.c_int)),
        ("x_binning_limits_count", ctypes.c_int),
        ("y_constraint", PicamRangeConstraint),
        ("height_constraint", PicamRangeConstraint),
        ("y_binning_limits_array", ctypes.POINTER(ctypes.c_int)),
        ("y_binning_limits_count", ctypes.c_int)
    ]

class PicamPulseConstraint(ctypes.Structure):
    _fields_ = [
        ("scope", ctypes.c_int),  # Assuming PicamConstraintScope is an enumeration
        ("severity", ctypes.c_int),  # Assuming PicamConstraintSeverity is an enumeration
        ("empty_set", ctypes.c_int),  # Assuming pibln is an integer
        ("delay_constraint", PicamRangeConstraint),
        ("width_constraint", PicamRangeConstraint),
        ("minimum_duration", ctypes.c_double),
        ("maximum_duration", ctypes.c_double)
    ]

class PicamModulationsConstraint(ctypes.Structure):
    _fields_ = [
        ("scope", ctypes.c_int),  # Assuming PicamConstraintScope is an enumeration
        ("severity", ctypes.c_int),  # Assuming PicamConstraintSeverity is an enumeration
        ("empty_set", ctypes.c_int),  # Assuming pibln is an integer
        ("maximum_modulation_count", ctypes.c_int),
        ("duration_constraint", PicamRangeConstraint),
        ("frequency_constraint", PicamRangeConstraint),
        ("phase_constraint", PicamRangeConstraint),
        ("output_signal_frequency_constraint", PicamRangeConstraint)
    ]

PicamActiveShutterEnum = PI_Enum(
    "PicamActiveShutter", dict(
    PicamActiveShutter_None     = 1,
    PicamActiveShutter_Internal = 2,
    PicamActiveShutter_External = 3
    ))

PicamAdcAnalogGainEnum = PI_Enum(
    "PicamAdcAnalogGain", dict(
    PicamAdcAnalogGain_Low    = 1,
    PicamAdcAnalogGain_Medium = 2,
    PicamAdcAnalogGain_High   = 3
    ))

PicamAdcQualityEnum = PI_Enum(
    "PicamAdcQuality", dict(
    PicamAdcQuality_LowNoise           = 1,
    PicamAdcQuality_HighCapacity       = 2,
    PicamAdcQuality_HighSpeed          = 4,
    PicamAdcQuality_ElectronMultiplied = 3
    ))

PicamCcdCharacteristicsMaskEnum = PI_Enum(
    "PicamCcdCharacteristicsMask", dict(
    PicamCcdCharacteristicsMask_None                 = 0x000,
    PicamCcdCharacteristicsMask_BackIlluminated      = 0x001,
    PicamCcdCharacteristicsMask_DeepDepleted         = 0x002,
    PicamCcdCharacteristicsMask_OpenElectrode        = 0x004,
    PicamCcdCharacteristicsMask_UVEnhanced           = 0x008,
    PicamCcdCharacteristicsMask_ExcelonEnabled       = 0x010,
    PicamCcdCharacteristicsMask_BackIlluminatedandExcelonEnabled = 0x011, #TODO make code that determines the & of two values to remove this line
    PicamCcdCharacteristicsMask_SecondaryMask        = 0x020,
    PicamCcdCharacteristicsMask_Multiport            = 0x040,
    PicamCcdCharacteristicsMask_AdvancedInvertedMode = 0x080,
    PicamCcdCharacteristicsMask_HighResistivity      = 0x100
    ))

PicamCenterWavelengthStatusEnum = PI_Enum(
    "PicamCenterWavelengthStatus", dict(
    PicamCenterWavelengthStatus_Moving     = 1,
    PicamCenterWavelengthStatus_Stationary = 2,
    PicamCenterWavelengthStatus_Faulted    = 3        
    ))

PicamCoolingFanStatusEnum = PI_Enum(
    "PicamCoolingFanStatus", dict(
    PicamCoolingFanStatus_Off      = 1,
    PicamCoolingFanStatus_On       = 2,
    PicamCoolingFanStatus_ForcedOn = 3        
    ))

PicamEMIccdGainControlModeEnum = PI_Enum(
    "PicamEMIccdGainControlMode", dict(
    PicamEMIccdGainControlMode_Optimal = 1,
    PicamEMIccdGainControlMode_Manual  = 2
    ))

PicamGateTrackingMaskEnum = PI_Enum(
    "PicamGateTrackingMask", dict(
    PicamGateTrackingMask_None  = 0x0,
    PicamGateTrackingMask_Delay = 0x1,
    PicamGateTrackingMask_Width = 0x2
    ))

PicamGatingModeEnum = PI_Enum(
    "PicamGatingMode", dict(
    PicamGatingMode_Disabled   = 4,
    PicamGatingMode_Repetitive = 1,
    PicamGatingMode_Sequential = 2,
    PicamGatingMode_Custom     = 3
    ))

PicamGatingSpeedEnum = PI_Enum(
    "PicamGatingSpeed", dict(
    PicamGatingSpeed_Fast = 1,
    PicamGatingSpeed_Slow = 2
    ))

PicamGratingCoatingEnum = PI_Enum(
    "PicamGratingCoating", dict(
    PicamGratingCoating_Al     = 1,
    PicamGratingCoating_AlMgF2 = 4,
    PicamGratingCoating_Ag     = 2,
    PicamGratingCoating_Au     = 3
    ))


PicamGratingTypeEnum = PI_Enum(
    "PicamGratingType", dict(
    PicamGratingType_Ruled              = 1,
    PicamGratingType_HolographicVisible = 2,
    PicamGratingType_HolographicNir     = 3,
    PicamGratingType_HolographicUV      = 4,
    PicamGratingType_Mirror             = 5
    ))

PicamIntensifierOptionsMaskEnum = PI_Enum(
    "PicamIntensifierOptionsMask", dict(
    PicamIntensifierOptionsMask_None                = 0x0,
    PicamIntensifierOptionsMask_McpGating           = 0x1,
    PicamIntensifierOptionsMask_SubNanosecondGating = 0x2,
    PicamIntensifierOptionsMask_Modulation          = 0x4
    ))

PicamIntensifierStatusEnum = PI_Enum(
    "PicamIntensifierStatus", dict(
    PicamIntensifierStatus_PoweredOff = 1,
    PicamIntensifierStatus_PoweredOn  = 2
    ))

PicamLaserOutputModeEnum = PI_Enum(
    "PicamLaserOutputMode", dict(
    PicamLaserOutputMode_Disabled       = 1,
    PicamLaserOutputMode_ContinuousWave = 2,
    PicamLaserOutputMode_Pulsed         = 3        
    ))

PicamLaserStatusEnum = PI_Enum(
    "PicamLaserStatus", dict(
    PicamLaserStatus_Disarmed = 1,
    PicamLaserStatus_Unarmed  = 2,
    PicamLaserStatus_Arming   = 3,
    PicamLaserStatus_Armed    = 4
    ))

PicamLightSourceEnum = PI_Enum(
    "PicamLightSource", dict(
    PicamLightSource_Disabled = 1,
    PicamLightSource_Hg       = 2,
    PicamLightSource_NeAr     = 3,
    PicamLightSource_Qth      = 4
    ))

PicamLightSourceStatusEnum = PI_Enum(
    "PicamLightSourceStatus", dict(
    PicamLightSourceStatus_Unstable = 1,
    PicamLightSourceStatus_Stable   = 2
    ))

PicamModulationTrackingMaskEnum = PI_Enum(
    "PicamModulationTrackingMask", dict(
    PicamModulationTrackingMask_None                  = 0x0,
    PicamModulationTrackingMask_Duration              = 0x1,
    PicamModulationTrackingMask_Frequency             = 0x2,
    PicamModulationTrackingMask_Phase                 = 0x4,
    PicamModulationTrackingMask_OutputSignalFrequency = 0x8
    ))

PicamOrientationMaskEnum = PI_Enum(
    "PicamOrientationMask", dict(
    PicamOrientationMask_Normal              = 0x0,
    PicamOrientationMask_FlippedHorizontally = 0x1,
    PicamOrientationMask_FlippedVertically   = 0x2
    ))

PicamOutputSignalEnum = PI_Enum(
    "PicamOutputSignal", dict(
    PicamOutputSignal_Acquiring                      =  6,
    PicamOutputSignal_AlwaysHigh                     =  5,
    PicamOutputSignal_AlwaysLow                      =  4,
    PicamOutputSignal_AuxOutput                      = 14,
    PicamOutputSignal_Busy                           =  3,
    PicamOutputSignal_EffectivelyExposing            =  9,
    PicamOutputSignal_EffectivelyExposingAlternation = 15,
    PicamOutputSignal_Exposing                       =  8,
    PicamOutputSignal_Gate                           = 13,
    PicamOutputSignal_InternalTriggerT0              = 12,
    PicamOutputSignal_NotReadingOut                  =  1,
    PicamOutputSignal_ReadingOut                     = 10,
    PicamOutputSignal_ShiftingUnderMask              =  7,
    PicamOutputSignal_ShutterOpen                    =  2,
    PicamOutputSignal_WaitingForTrigger              = 11
    ))

PicamPhosphorTypeEnum = PI_Enum(
    "PicamPhosphorType", dict(
    PicamPhosphorType_P43 = 1,
    PicamPhosphorType_P46 = 2
    ))

PicamPhotocathodeSensitivityEnum = PI_Enum(
    "PicamPhotocathodeSensitivity", dict(
    PicamPhotocathodeSensitivity_RedBlue          =  1,
    PicamPhotocathodeSensitivity_SuperRed         =  7,
    PicamPhotocathodeSensitivity_SuperBlue        =  2,
    PicamPhotocathodeSensitivity_UV               =  3,
    PicamPhotocathodeSensitivity_SolarBlind       = 10,
    PicamPhotocathodeSensitivity_Unigen2Filmless  =  4,
    PicamPhotocathodeSensitivity_InGaAsFilmless   =  9,
    PicamPhotocathodeSensitivity_HighQEFilmless   =  5,
    PicamPhotocathodeSensitivity_HighRedFilmless  =  8,
    PicamPhotocathodeSensitivity_HighBlueFilmless =  6
    ))

PicamPhotonDetectionModeEnum = PI_Enum(
    "PicamPhotonDetectionMode", dict(
    PicamPhotonDetectionMode_Disabled     = 1,
    PicamPhotonDetectionMode_Thresholding = 2,
    PicamPhotonDetectionMode_Clipping     = 3
    ))

PicamPixelFormatEnum = PI_Enum(
    "PicamPixelFormat", dict(
    PicamPixelFormat_Monochrome16Bit = 1,
    PicamPixelFormat_Monochrome32Bit = 2
    ))

PicamReadoutControlModeEnum = PI_Enum(
    "PicamReadoutControlMode", dict(
    PicamReadoutControlMode_FullFrame           = 1,  
    PicamReadoutControlMode_FrameTransfer       = 2,
    PicamReadoutControlMode_Interline           = 5,
    PicamReadoutControlMode_RollingShutter      = 8,
    PicamReadoutControlMode_ExposeDuringReadout = 9,
    PicamReadoutControlMode_Kinetics            = 3,
    PicamReadoutControlMode_SpectraKinetics     = 4,
    PicamReadoutControlMode_Dif                 = 6,
    PicamReadoutControlMode_SeNsR               = 7
    ))

PicamSensorTemperatureStatusEnum = PI_Enum(                                
    "PicamSensorTemperatureStatus" , dict(
    PicamSensorTemperatureStatus_Unlocked = 1,
    PicamSensorTemperatureStatus_Locked   = 2,
    PicamSensorTemperatureStatus_Faulted  = 3
    ))

PicamSensorTypeEnum = PI_Enum(
    "PicamSensorType", dict(
    PicamSensorType_Ccd    = 1,
    PicamSensorType_InGaAs = 2,
    PicamSensorType_Cmos   = 3
    ))

PicamShutterStatusEnum = PI_Enum(
    "PicamShutterStatus", dict(
    PicamShutterStatus_NotConnected = 1,
    PicamShutterStatus_Connected    = 2,
    PicamShutterStatus_Overheated   = 3
    ))

PicamShutterTimingModeEnum = PI_Enum(
    "PicamShutterTimingMode", dict(
    PicamShutterTimingMode_Normal            = 1,
    PicamShutterTimingMode_AlwaysClosed      = 2,
    PicamShutterTimingMode_AlwaysOpen        = 3,
    PicamShutterTimingMode_OpenBeforeTrigger = 4
    ))

PicamShutterTypeEnum = PI_Enum(
    "PicamShutterType", dict(
    PicamShutterType_None               = 1,
    PicamShutterType_VincentCS25        = 2,
    PicamShutterType_VincentCS45        = 3,
    PicamShutterType_VincentCS90        = 9,
    PicamShutterType_VincentDSS10       = 8,
    PicamShutterType_VincentVS25        = 4,
    PicamShutterType_VincentVS35        = 5,
    PicamShutterType_ProntorMagnetic0   = 6,
    PicamShutterType_ProntorMagneticE40 = 7    
    ))

PicamTimeStampsMaskEnum = PI_Enum(
    "PicamTimeStampsMask", dict(
    PicamTimeStampsMask_None            = 0x0,
    PicamTimeStampsMask_ExposureStarted = 0x1,
    PicamTimeStampsMask_ExposureEnded   = 0x2,
    PicamTimeStampsMask_ExposureStartedandEnded = 0x3
    ))

PicamTriggerCouplingEnum = PI_Enum(
    "PicamTriggerCoupling", dict(
    PicamTriggerCoupling_AC = 1,
    PicamTriggerCoupling_DC = 2
    ))

PicamTriggerDeterminationEnum = PI_Enum(
    "PicamTriggerDetermination", dict(
    PicamTriggerDetermination_PositivePolarity       = 1,
    PicamTriggerDetermination_NegativePolarity       = 2,
    PicamTriggerDetermination_RisingEdge             = 3,
    PicamTriggerDetermination_FallingEdge            = 4,
    PicamTriggerDetermination_AlternatingEdgeRising  = 5,
    PicamTriggerDetermination_AlternatingEdgeFalling = 6
    ))

PicamTriggerResponseEnum = PI_Enum(
    "PicamTriggerResponse", dict(
    PicamTriggerResponse_NoResponse               = 1,
    PicamTriggerResponse_StartOnSingleTrigger     = 5,
    PicamTriggerResponse_ReadoutPerTrigger        = 2,
    PicamTriggerResponse_ShiftPerTrigger          = 3,
    PicamTriggerResponse_GatePerTrigger           = 6,
    PicamTriggerResponse_ExposeDuringTriggerPulse = 4
    ))

PicamTriggerSourceEnum = PI_Enum(
    "PicamTriggerSource", dict(
    PicamTriggerSource_None     = 3,
    PicamTriggerSource_Internal = 2,
    PicamTriggerSource_External = 1
    ))

PicamTriggerStatusEnum = PI_Enum(
    "PicamTriggerStatus", dict(
    PicamTriggerStatus_NotConnected = 1,
    PicamTriggerStatus_Connected    = 2    
    ))

PicamTriggerTerminationEnum = PI_Enum(
    "PicamTriggerTermination", dict(
    PicamTriggerTermination_FiftyOhms     = 1,
    PicamTriggerTermination_HighImpedance = 2
    ))

PicamVacuumStatusEnum = PI_Enum(
    "PicamVacuumStatus", dict(
    PicamVacuumStatus_Sufficient = 1,
    PicamVacuumStatus_Low        = 2        
    ))

PicamValueAccessEnum = PI_Enum(
    "PicamValueAccess", dict(
    PicamValueAccess_ReadOnly         = 1,
    PicamValueAccess_ReadWriteTrivial = 3,
    PicamValueAccess_ReadWrite        = 2        
    ))
PicamValueAccess_num = dict(
    PicamValueAccess_ReadOnly         = 1,
    PicamValueAccess_ReadWriteTrivial = 3,
    PicamValueAccess_ReadWrite        = 2                        
    )

PicamValueAccess = dict()
for k,v in PicamValueAccess_num.items():
    PicamValueAccess[v] = k

PicamRoisConstraintRulesMaskEnum = PI_Enum(
    "PicamRoisConstraintRulesMask", dict(
    PicamRoisConstraintRulesMask_None                  = 0x00,
    PicamRoisConstraintRulesMask_XBinningAlignment     = 0x01,
    PicamRoisConstraintRulesMask_YBinningAlignment     = 0x02,
    PicamRoisConstraintRulesMask_HorizontalSymmetry    = 0x04,
    PicamRoisConstraintRulesMask_VerticalSymmetry      = 0x08,
    PicamRoisConstraintRulesMask_SymmetryBoundsBinning = 0x10
    ))

class PicamAvailableData(ctypes.Structure):
    _fields_ = [("initial_readout",ctypes.c_void_p),
                ("readout_count",pi64s)
                ]

class PicamAcquisitionStatus(ctypes.Structure):
    _fields_ = [
        ("running", pibln),  # Assuming pibln is an integer
        ("errors", ctypes.c_uint),  # Assuming PicamAcquisitionErrorsMask is an unsigned integer
        ("readout_rate", piflt)
    ]
