import struct
from pydantic import BaseModel

# Lecroy provides the x_div as an enumerated value so we have to decipher it
tdiv_enum = [
    200e-12, 500e-12,
    1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
    1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
    1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3,
    1, 2, 5, 10, 20, 50, 100, 200, 500, 1000
]


class WaveformPreamble(BaseModel):
    desc_name: str
    template_name: str
    comm_type: int
    comm_order: int
    wave_desc_length: int
    wave_array_1: int
    instr_name: str
    wave_array_count: int
    first_point: int
    data_interval: int
    read_frames: int
    sum_frames: int
    y_div: float
    y_offset: float
    code_per_div: float
    adc_bit: int
    frame_index: int
    x_interval: float
    x_offset: float
    x_div_index: int
    x_div: float
    ch_coupling: int
    probe: float
    fixed_probe: float
    bw_limit: int
    wave_source: int

    @staticmethod
    def from_byte_block(byte_block: bytes) -> "WaveformPreamble":
        # Ensure the byte block is the correct length
        expected_length = 346
        if len(byte_block) != expected_length:
            raise ValueError(f"Expected byte block of {expected_length} bytes, but got {len(byte_block)} bytes.")

        # format_str structure found in page 725 in T3DSO4000L-HD programming manual
        format_str = (
            '<'     # Little-endian and informing struct not to add padding
            '16s'   # desc_name (char): Always starts with "WAVEDESC"
            '16s'   # template_name (char): Always starts with "WAVEACE"
            'h'     # comm_type (short): 0 - byte, 1 - word; default is 0.
            'h'     # comm_order (short): 0 - LSB, 1 - MSB; default is 0.
            'l'     # wave_desc_length (long): Length in bytes of block WAVEDESC
            '20x'   # Reserved (20 bytes)
            'l'     # wave_array_1 (long): Number of transmitted bytes set by :WAVeform:POINt (only for analog)
            '12x'   # Reserved (12 bytes)
            '16s'   # instr_name (char): Name of device; always "Teledyne Test Tools"
            '4x'    # Reserved (4 bytes)
            '16x'   # Reserved (16 bytes)
            '4x'    # Reserved (4 bytes)
            'l'     # wave_array_count (long): Number of data points in the data array. (only for analog)
            '12x'   # Reserved (12 bytes)
            'l'     # first_point (long): Offset relative to the start of trace buffer. Value same as :WAVeform:STARt
            'l'     # data_interval (long): Interval between data points transfer. Value same as :WAVeform:INTerval
            '4x'    # Reserved (4 bytes)
            'l'     # read_frames (long): Number of frames transferred
            'l'     # sum_frames (long): Number of frames acquired
            '4x'    # Reserved (4 bytes)
            'f'     # y_div (float): Vertical gain. The value of vertical scale without probe attenuation
            'f'     # y_offset (float): Vertical offset. The value of vertical offset without probe attenuation
            'f'     # code_per_div (float): Decimal value for each vertical division. Used to convert byte to volts
            '4x'    # Reserved (4 bytes)
            'h'     # adc_bit (short): Digitizer bit resolution
            'h'     # frame_index (short): Frame index of sequence set by :WAVefrom:SEQuence; default is 1.
            'f'     # x_interval (float): Sampling interval for time domain waveforms. x_interval = 1/sample_rate
            'd'     # x_offset (double): Trigger offset; seconds between the trigger and first data point (in seconds)
            '8x'    # Reserved (8 bytes)
            '48x'   # Reserved (48 bytes)
            '48x'   # Reserved (48 bytes)
            '4x'    # Reserved (4 bytes)
            '16x'   # Reserved (16 bytes)
            '4x'    # Reserved (4 bytes)
            '8x'    # Reserved (8 bytes)
            'h'     # time_base (short): Enumerated time/div
            'h'     # ch_coupling (short): Vertical coupling. 0 - DC, 1 - AC
            'f'     # probe (float): Probe attenuation
            'h'     # fixed_probe (short): Fixed vertical gain. Enumerated v_div
            'h'     # bw_limit (short): Bandwidth Limit. 0 - OFF, 1 - 20M, 2 - 200M
            '8x'    # Reserved (8 bytes)
            'h'     # wave_source (short): Active channel source. 0 - C1, 1 - C2, 2 - C3, 3 - C4
        )

        # Unpack the binary data using the format_str structure
        # NOTE: Any lines that have an 'x' indicates that struct places NULL byte(s) for those values,
        # which is then ignored and in the output.
        unpacked_data = struct.unpack(format_str, byte_block)

        desc_name = unpacked_data[0].decode('ascii')
        template_name = unpacked_data[1].decode('ascii')
        comm_type = unpacked_data[2]
        comm_order = unpacked_data[3]
        wave_desc_length = unpacked_data[4]
        wave_array_1 = unpacked_data[5]
        instr_name = unpacked_data[6].decode('ascii')
        wave_array_count = unpacked_data[7]
        first_point = unpacked_data[8]
        data_interval = unpacked_data[9]
        read_frames = unpacked_data[10]
        sum_frames = unpacked_data[11]
        y_div = unpacked_data[12]
        y_offset = unpacked_data[13]
        code_per_div = unpacked_data[14]
        adc_bit = unpacked_data[15]
        frame_index = unpacked_data[16]
        x_interval = unpacked_data[17]
        x_offset = unpacked_data[18]
        x_div_index = unpacked_data[19]
        x_div = tdiv_enum[x_div_index]
        ch_coupling = unpacked_data[20]
        probe = unpacked_data[21]
        fixed_probe = unpacked_data[22]
        bw_limit = unpacked_data[23]
        wave_source = unpacked_data[24]

        return WaveformPreamble(
            desc_name=desc_name,
            template_name=template_name,
            comm_type=comm_type,
            comm_order=comm_order,
            wave_desc_length=wave_desc_length,
            wave_array_1=wave_array_1,
            instr_name=instr_name,
            wave_array_count=wave_array_count,
            first_point=first_point,
            data_interval=data_interval,
            read_frames=read_frames,
            sum_frames=sum_frames,
            y_div=y_div,
            y_offset=y_offset,
            code_per_div=code_per_div,
            adc_bit=adc_bit,
            frame_index=frame_index,
            x_interval=x_interval,
            x_offset=x_offset,
            x_div_index=x_div_index,
            x_div=x_div,
            ch_coupling=ch_coupling,
            probe=probe,
            fixed_probe=fixed_probe,
            bw_limit=bw_limit,
            wave_source=wave_source
        )


def main():
    byte_block = (
        b'WAVEDESC\x00\x00\x00\x00\x00\x00\x00\x00WAVEACE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00'
        b'\x00Z\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Siglent SDS\x00\x00\x00\x00'
        b'\x00\xab\xcd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xf0\xfa'
        b'\x02\x80\xf0\xfa\x02~\xf0\xfa\x02\x00\x00\x00\x00\x7f\xf0\xfa\x02\xc0\x0e\x16\x02\x01\x00\x00\x00'
        b'\x01\x00\x00\x00@\r\x03\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\xc0\xbf\x00\x00'
        b'\xfeF\x00\x00\x00\xc7\x08\x00\x01\x00_p\x890\x9a\x99\x99\x99\x99\x99\x99\xbf\x9a\x99\x99\x99\x99'
        b'\x99\x99?V\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00S\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00_p'
        b'\x890\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x01\x00\x16\x00\x00\x00\x00\x00\x80?\x11\x00\x00\x00\x00\x00\x80?\x00\x00\xc0\xbf\x01\x00'
        )

    unpacked_data = WaveformPreamble.from_byte_block(byte_block)
    print(unpacked_data)


if __name__ == '__main__':
    main()