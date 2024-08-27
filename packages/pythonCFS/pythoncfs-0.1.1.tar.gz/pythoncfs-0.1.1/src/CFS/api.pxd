from libc.stdint cimport int16_t, uint16_t, int32_t
cdef extern from "cfsapi.h":
    # Constants to select between file variables and data section variables
    cdef const int FILEVAR "FILEVAR"
    cdef const int DSVAR "DSVAR"

    # Constants defining flag bits
    cdef const int FLAG7 "FLAG7"
    cdef const int FLAG6 "FLAG6" 
    cdef const int FLAG5 "FLAG5"
    cdef const int FLAG4 "FLAG4"
    cdef const int FLAG3 "FLAG3"
    cdef const int FLAG2 "FLAG2"
    cdef const int FLAG1 "FLAG1"
    cdef const int FLAG0 "FLAG0"
    cdef const int FLAG15 "FLAG15"
    cdef const int FLAG14 "FLAG14"
    cdef const int FLAG13 "FLAG13"
    cdef const int FLAG12 "FLAG12"
    cdef const int FLAG11 "FLAG11"
    cdef const int FLAG10 "FLAG10"
    cdef const int FLAG9 "FLAG9"
    cdef const int FLAG8 "FLAG8"
    cdef const int noFlags "noFlags"

    cdef const int INT1 "INT1" # 1 byte int
    cdef const int WRD1 "WRD1" # 1 byte unsigned int
    cdef const int INT2 "INT2" # 2 byte int
    cdef const int WRD2 "WRD2" # 2 byte int
    cdef const int INT4 "INT4" # 4 byte int
    cdef const int RL4 "RL4" # 4 byte float
    cdef const int RL8 "RL8" # 8 byte double
    cdef const int LSTR "LSTR" # variable length string

    # Constants defining different channel storage methods/data kinds
    cdef const int EQUALSPACED "EQUALSPACED"
    cdef const int MATRIX "MATRIX"
    cdef const int SUBSIDIARY "SUBSIDIARY"

    # Constants defining max lengths for various parts of the CFS file
    cdef const int DESCCHARS "DESCCHARS" # description max length: 20 characters
    cdef const int FNAMECHARS "FNAMECHARS" # filename max length: 12 characters
    cdef const int COMMENTCHARS "COMMENTCHARS" # comment max length: 72 characters
    cdef const int UNITCHARS "UNITCHARS"  # units max length: 8 characters

    ctypedef uint16_t TSFlags;
    ctypedef char TDataType;
    ctypedef char TCFSKind;

    ctypedef char TDesc[DESCCHARS + 2];
    ctypedef char TFilename[FNAMECHARS + 2];
    ctypedef char TComment[COMMENTCHARS + 2];
    ctypedef char TUnits[UNITCHARS + 2];

    ctypedef struct TVarDesc:
        TDesc varDesc; # Variable Description
        TDataType vType; # INT1,WRD1 etc.
        char zerobyte; # for MS Pascal compatibility
        TUnits varUnits; # variable units
        short vSize; # no. of characters if LSTR

    # Some function expect a certain number of bytes.
    # CFS was originally written for 32-bit systems,
    # so we have to redefine some of the types.
    ctypedef int16_t cfs_short;
    ctypedef int32_t cfs_long;

    ctypedef uint16_t WORD;
    ctypedef char *TpStr;
    ctypedef cfs_short *TpShort;
    ctypedef float *TpFloat;
    ctypedef cfs_long *TpLong;
    ctypedef void *TpVoid;
    ctypedef TSFlags *TpFlags;
    ctypedef TDataType *TpDType;
    ctypedef TCFSKind *TpDKind;
    ctypedef WORD *TpUShort;

    # TODO: Implement these functions
    cfs_short CloseCFSFile(cfs_short handle);
    cfs_short OpenCFSFile(TpStr fName, cfs_short enableWr, cfs_short memTable);
    void GetGenInfo(cfs_short handle, TpStr time, TpStr date, TpStr comment);
    void GetFileInfo(cfs_short handle, TpShort channels, TpShort fileVars, TpShort DSVars, TpUShort dataSects);
    void GetVarDesc(cfs_short handle, cfs_short varNo, cfs_short varKind, TpShort varSize, TpDType varType, TpStr units, TpStr about);
    void GetVarVal(cfs_short handle, cfs_short varNo, cfs_short vaKind, WORD dataSect, TpVoid varADS);
    void GetFileChan(cfs_short handle, cfs_short channel, TpStr chanName, TpStr yUnits, TpStr xUnits, TpDType dataType, TpDKind dataKind, TpShort spacing, TpShort other);
    void GetDSChan(cfs_short handle, cfs_short channel, WORD dataSect, TpLong chOffset, TpLong points, TpFloat yScale, TpFloat yOffset, TpFloat xScale, TpFloat xOffset);
    WORD GetChanData(cfs_short handle, cfs_short channel, WORD dataSect, cfs_long pointOff, WORD points, TpVoid dataADS, cfs_long areaSize);
    cfs_long CFSFileSize(cfs_short handle);
    cfs_long GetDSSize(cfs_short handle, WORD dataSect);
    cfs_short ReadData(cfs_short handle, WORD dataSect, cfs_long byteOff, WORD bytes, TpVoid dataADS);
    WORD DSFlagValue(int nflag);
    DSFlags(cfs_short handle, WORD dataSect, short setIt, TpFlags pflagSet);
    cfs_short FileError(TpShort handleNo, TpShort procNo, TpShort errNo);

