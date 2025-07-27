"""Data buffer decoder for the embedded Radiacode library."""

import datetime
import struct
from typing import List, Union

from ..bytes_buffer import BytesBuffer
from ..types import DoseRateDB, Event, EventId, RareData, RawData, RealTimeData


def decode_VS_DATA_BUF(
    br: BytesBuffer, base_time: datetime.datetime, ignore_errors: bool = True
) -> List[Union[RealTimeData, DoseRateDB, RareData, RawData, Event]]:
    """Decode VS_DATA_BUF data from the device.

    Args:
        br: BytesBuffer containing the data
        base_time: Base time for timestamp calculations
        ignore_errors: Whether to ignore decoding errors

    Returns:
        List of decoded data records
    """
    ret: List[Union[RealTimeData, DoseRateDB, RareData, RawData, Event]] = []
    next_seq = None
    
    while br.remaining() >= 7:
        seq, eid, gid, ts_offset = br.read_uint8(), br.read_uint8(), br.read_uint8(), struct.unpack('<i', br.read(4))[0]
        dt = base_time + datetime.timedelta(milliseconds=ts_offset * 10)
        
        if next_seq is not None and next_seq != seq:
            if not ignore_errors:
                print(f'seq jump while processing {eid=} {gid=}, expect:{next_seq}, got:{seq} {br.remaining()=}')
            break

        next_seq = (seq + 1) % 256
        
        if eid == 0 and gid == 0:  # GRP_RealTimeData
            count_rate, dose_rate, count_rate_err, dose_rate_err, flags, rt_flags = struct.unpack('<ffHHHB', br.read(17))
            ret.append(
                RealTimeData(
                    dt=dt,
                    count_rate=count_rate,
                    count_rate_err=count_rate_err / 10,
                    dose_rate=dose_rate,
                    dose_rate_err=dose_rate_err / 10,
                    flags=flags,
                    real_time_flags=rt_flags,
                )
            )
        elif eid == 0 and gid == 1:  # GRP_RawData
            count_rate, dose_rate = struct.unpack('<ff', br.read(8))
            ret.append(
                RawData(
                    dt=dt,
                    count_rate=count_rate,
                    dose_rate=dose_rate,
                )
            )
        elif eid == 0 and gid == 2:  # GRP_DoseRateDB
            count, count_rate, dose_rate, dose_rate_err, flags = struct.unpack('<IffHH', br.read(20))
            ret.append(
                DoseRateDB(
                    dt=dt,
                    count=count,
                    count_rate=count_rate,
                    dose_rate=dose_rate,
                    dose_rate_err=dose_rate_err / 10,
                    flags=flags,
                )
            )
        elif eid == 0 and gid == 3:  # GRP_RareData
            duration, dose, temperature, charge_level, flags = struct.unpack('<IfHHH', br.read(16))
            ret.append(
                RareData(
                    dt=dt,
                    duration=duration,
                    dose=dose,
                    temperature=(temperature - 2000) / 100,
                    charge_level=charge_level / 100,
                    flags=flags,
                )
            )
        elif eid == 0 and gid == 4:  # GRP_UserData:
            count, count_rate, dose_rate, dose_rate_err, flags = struct.unpack('<IffHH', br.read(20))
            # TODO: Implement user data handling
        elif eid == 0 and gid == 5:  # GRP_SheduleData
            count, count_rate, dose_rate, dose_rate_err, flags = struct.unpack('<IffHH', br.read(20))
            # TODO: Implement schedule data handling
        elif eid == 0 and gid == 6:  # GRP_AccelData
            acc_x, acc_y, acc_z = struct.unpack('<HHH', br.read(6))
            # TODO: Implement accelerometer data handling
        elif eid == 0 and gid == 7:  # GRP_Event
            event, event_param1, flags = struct.unpack('<BBH', br.read(4))
            ret.append(
                Event(
                    dt=dt,
                    event=EventId(event),
                    event_param1=event_param1,
                    flags=flags,
                )
            )
        elif eid == 0 and gid == 8:  # GRP_RawCountRate
            count_rate, flags = struct.unpack('<fH', br.read(6))
            # TODO: Implement raw count rate handling
        elif eid == 0 and gid == 9:  # GRP_RawDoseRate
            dose_rate, flags = struct.unpack('<fH', br.read(6))
            # TODO: Implement raw dose rate handling
        elif eid == 1 and gid == 1:  # ???
            samples_num, smpl_time_ms = struct.unpack('<HI', br.read(6))
            br.skip(8 * samples_num)  # skip
        elif eid == 1 and gid == 2:
            samples_num, smpl_time_ms = struct.unpack('<HI', br.read(6))
            br.skip(16 * samples_num)  # skip
        elif eid == 1 and gid == 3:  # ???
            samples_num, smpl_time_ms = struct.unpack('<HI', br.read(6))
            br.skip(14 * samples_num)  # skip
        else:
            if not ignore_errors:
                print(f'Unknown eid:{eid} gid:{gid}')
            break

    return ret