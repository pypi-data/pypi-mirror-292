import array
import cython
from CFS._constants import CFSDataType, CFSDataKind
from cython.cimports.CFS import api
from cython.cimports.cpython import array

cpdef (api.cfs_short) open_cfs_file(filename: str):
    filename_bytes = filename.encode("ascii")
    cdef char *filename_c = filename_bytes
    handle = api.OpenCFSFile(filename_c, 0, 1)
    if handle < 0:
        raise Exception("Invalid File Handle")
    return handle

cpdef close_cfs_file(handle: api.cfs_short):
    api.CloseCFSFile(handle)

cpdef tuple[str, str, str] get_gen_info(handle: api.cfs_short):
    cdef char[9] c_time
    cdef char[9] c_date
    cdef char[73] c_comment
    api.GetGenInfo(handle, c_time, c_date, c_comment)

    time = <bytes> c_time
    date = <bytes> c_date
    comment = <bytes> c_comment

    return (time, date, comment)

cpdef tuple[int, int, int, int] get_file_info(handle: api.cfs_short):
    channels: api.cfs_short = 0
    file_vars: api.cfs_short = 0
    data_section_vars: api.cfs_short = 0
    data_sections: api.WORD = 0

    api.GetFileInfo(handle, &channels, &file_vars, &data_section_vars, &data_sections)

    return (channels, file_vars, data_section_vars, data_sections)

cpdef tuple[str, str, str, CFSDataType, CFSDataKind, int, int] get_file_chan(handle: api.cfs_short, channel: api.cfs_short):
    cdef char[21] c_channel_name
    cdef char[9] c_y_units
    cdef char[9] c_x_units
    data_type: api.TDataType
    data_kind: api.TCFSKind
    spacing: api.cfs_short
    other: api.cfs_short

    api.GetFileChan(handle, channel, c_channel_name, c_y_units, c_x_units, &data_type, &data_kind, &spacing, &other)

    channel_name = <bytes> c_channel_name
    y_units = <bytes> c_y_units
    x_units = <bytes> c_x_units

    return (channel_name, y_units, x_units, CFSDataType(data_type), CFSDataKind(data_kind), spacing, other)

cpdef tuple[api.cfs_long, api.cfs_long, float, float, float, float] get_ds_chan(handle: api.cfs_short, channel: api.cfs_short, data_section: api.WORD):
    channel_offset: api.cfs_long
    points: api.cfs_long = 0
    cdef float y_scale
    cdef float y_offset
    cdef float x_scale
    cdef float x_offset

    api.GetDSChan(handle, channel, data_section, &channel_offset, &points, &y_scale, &y_offset, &x_scale, &x_offset)

    return (channel_offset, points, y_scale, y_offset, x_scale, x_offset)

cpdef array.array get_chan_data(handle: api.cfs_short, channel: api.cfs_short, data_section: api.WORD, point_offset: api.cfs_long, points_to_read: api.WORD, data_type: CFSDataType):
    array_type = ''
    if data_type == CFSDataType.int_2:
        array_type = 'h'
    elif data_type == CFSDataType.real_4:
        array_type = 'f'
    else:
        raise NotImplementedError("Support for types other than Int16 or Float32 is not implemented.")
    cdef array.array array_template = array.array(array_type, [])
    cdef array.array data
    data = array.clone(array_template, points_to_read, zero=True)
    size_of_element_bytes = data.itemsize
    cdef (api.cfs_long) area_size = points_to_read * size_of_element_bytes
    api.GetChanData(handle, channel, data_section, point_offset, points_to_read, data.data.as_voidptr, area_size)
    return data
