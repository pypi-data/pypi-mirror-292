from CFS cimport api

cpdef enum CFSFlag:
    flag_7 = api.FLAG7
    flag_6 = api.FLAG6
    flag_5 = api.FLAG5
    flag_4 = api.FLAG4
    flag_3 = api.FLAG3
    flag_2 = api.FLAG2
    flag_1 = api.FLAG1
    flag_0 = api.FLAG0
    flag_15 = api.FLAG15
    flag_14 = api.FLAG14
    flag_13 = api.FLAG13
    flag_12 = api.FLAG12
    flag_11 = api.FLAG11
    flag_10 = api.FLAG10
    flag_9 = api.FLAG9
    flag_8 = api.FLAG8
    no_flags = api.noFlags

cpdef enum CFSDataKind:
    equalspaced = api.EQUALSPACED
    matrix = api.MATRIX
    subsidiary = api.SUBSIDIARY

cpdef enum CFSDataType:
    int_1 = api.INT1 
    int_2 = api.INT2
    word_1 = api.WRD1
    word_2 = api.WRD2
    int_4 = api.INT4
    real_4 = api.RL4
    real_8 = api.RL8
    string = api.LSTR
