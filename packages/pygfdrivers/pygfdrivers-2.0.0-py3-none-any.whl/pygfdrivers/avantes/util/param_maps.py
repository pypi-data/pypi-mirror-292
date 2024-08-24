conn_type_map = {
    'usb'       : 0,
    'ethernet'  : 256,
    'both'      : -1
}

trig_config_maps = {
    'Mode' : {
        'software'      : 0,
        'hardware'      : 1,
        'single_scan'   : 2
    },
    'Source' : {
        'external'      : 0,
        'sync_input'    : 1
    },
    'SourceType' : {
        'edge'  : 0,
        'level' : 1
    }
}

inverted_trig_config_maps = {
    top_key: {value: sub_key for sub_key, value in sub_dict.items()}
    for top_key, sub_dict in trig_config_maps.items()
}

status_map = {
    b'\x00' : 'unknown',
    b'\x01' : 'usb_available',
    b'\x02' : 'usb_in_use_by_application',
    b'\x03' : 'usb_in_use_by_other',
    b'\x04' : 'eth_available',
    b'\x05' : 'eth_in_use_by_application',
    b'\x06' : 'eth_in_use_by_other',
    b'\x07' : 'eth_already_in_use_usb'
}

detector_map = {
    0 : 'unknown',
    1 : 'AS5216',
    2 : 'ASMini',
    3 : 'AS7010',
    4 : 'AS7007',
}
