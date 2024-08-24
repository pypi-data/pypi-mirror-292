import socket
import os

# class to hold labview control loop states that are required by raspberry pi client
class LABVIEW_CONTROL_LOOP:
    IDLE        = 'idle'
    CHARGE      = 'charge'
    FIRING      = 'firing'
    DUMPING     = 'dumping'
    ARMING      = 'arming'
    DATA        = 'dataCollection'
    ABORT       = 'abort'
    UPDATE      = 'updateConfig'

class DEBUGGING:
    DEBUG_MODE_1  = False
    DEBUG_MODE_2  = False

class SLACK_MESSAGES:
    EVENTS_RECIPIENT                = 'ALI_ESBAK' if DEBUGGING.DEBUG_MODE_1 else 'PI3_EVENTS'
    ALARMS_RECIPIENT                = 'ALI_ESBAK' if DEBUGGING.DEBUG_MODE_1 else 'PI3_ALARMS'
    FILE_PERMISSION                 = 'ALI_ESBAK' if DEBUGGING.DEBUG_MODE_1 else 'FILE_PERMISSION'
    PI3_ACTIVITY_RECIPIENT          = 'ALI_ESBAK' if DEBUGGING.DEBUG_MODE_1 else 'PI3_ACTIVITY'

class ClientType:
    LABVIEW     =   0
    CAPBANK     =   1
    THOMPSON    =   2
    TEST        =   39

    NAME        = "name"
    TYPE        = "type"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'
    
    Bold       = "\033[1m"
    Dim        = "\033[2m"
    Underlined = "\033[4m"
    Blink      = "\033[5m"
    Reverse    = "\033[7m"
    Hidden     = "\033[8m"

    ResetBold       = "\033[21m"
    ResetDim        = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink      = "\033[25m"
    ResetReverse    = "\033[27m"
    ResetHidden     = "\033[28m"

    Default      = "\033[39m"
    Black        = "\033[30m"
    Red          = "\033[31m"
    Green        = "\033[32m"
    Yellow       = "\033[33m"
    Blue         = "\033[34m"
    Magenta      = "\033[35m"
    Cyan         = "\033[36m"
    LightGray    = "\033[37m"
    DarkGray     = "\033[90m"
    LightRed     = "\033[91m"
    LightGreen   = "\033[92m"
    LightYellow  = "\033[93m"
    LightBlue    = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan    = "\033[96m"
    White        = "\033[97m"

    BackgroundDefault      = "\033[49m"
    BackgroundBlack        = "\033[40m"
    BackgroundRed          = "\033[41m"
    BackgroundGreen        = "\033[42m"
    BackgroundYellow       = "\033[43m"
    BackgroundBlue         = "\033[44m"
    BackgroundMagenta      = "\033[45m"
    BackgroundCyan         = "\033[46m"
    BackgroundLightGray    = "\033[47m"
    BackgroundDarkGray     = "\033[100m"
    BackgroundLightRed     = "\033[101m"
    BackgroundLightGreen   = "\033[102m"
    BackgroundLightYellow  = "\033[103m"
    BackgroundLightBlue    = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan    = "\033[106m"
    BackgroundWhite        = "\033[107m"


# common default parameters used for communication
# Header size to not be messed with to be kept at 8
class DEFAULTS_COM:
    HOST        = socket.gethostname()
    PORT        = 8095
    # HEADER MUST BE 8
    HEADER      = 8
    FORMAT      = 'utf-8'
    DIS_MESS    = '!DISCONNECT'
    CLIENT_NAME = 'client_00'
    CLIENT_TYPE = ClientType.LABVIEW

class DEFAULTS_SQL:
    user        ='root'
    dbName      =['plasmaInjector_3','plasmaInjector_3']
    host        =['127.0.0.1', '172.30.5.1']
    port        =['3307','3307']
    password    =['Uline231', '123']

class GIT_CONFIG:
    GIT_TOKEN   = os.environ.get('GIT_TOKEN')
    REPO_NAME   = 'ccs-configuration'
    REPO_URL    = f"https://{GIT_TOKEN}@github.com/GeneralFusion/{REPO_NAME}.git"
    BRANCH_NAME = 'main'
    CFG_FLE_NAME= 'CCS_Config/CCS_Config.yml'

class CONFIG_KEYS:
    LABVIEW_CLIENT      = 'clients'
    DATABASES           = 'Databases'
    NAME                = 'name'
    TYPE                = 'type'
    CLIENTS             = 'clients'

class DEFAULTS_CL:
    SAVE_FILE_PATH_BASE_FOLDER      = r"C:/Users/ali.esbak/Desktop/PythonDAQ/" if 'nt' in os.name else r'/Data/ccs_utf/'
    VISA_SCOPES = [{
        "name": "IF_01", 
        "connectionString":'TCPIP0::172.25.226.126::inst0::INSTR', 
        "activeChannels":[1]}]
