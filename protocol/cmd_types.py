from enum import Enum

class cmd_type(Enum):
    HUB_PROPERTIES          = 0x01
    PORT_INPUT_FORMAT       = 0x41
    PORT_INFORMATION        = 0x43
    PORT_MODE_INFORMATION   = 0x44
    PORT_VALUE              = 0x45
    PORT_OUTPUT_COMMAND     = 0x81