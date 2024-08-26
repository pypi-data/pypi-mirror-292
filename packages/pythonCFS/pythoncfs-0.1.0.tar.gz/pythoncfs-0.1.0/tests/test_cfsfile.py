from CFS.CFSFile import CFSFile
from pathlib import Path

TEST_FILENAME = Path(__file__).parent.joinpath("test_data/test_file.cfs")
TEST_FILE = CFSFile(TEST_FILENAME)

def test_file_info():
    assert TEST_FILE.date == b"10/08/24"
    assert TEST_FILE.time == b"12:03:14"
    assert TEST_FILE.comment == b"Demonstration of C version"

def test_channel_info():
    assert TEST_FILE.channel_info[0]['name'] == b"ECG"
    assert TEST_FILE.channel_info[0]['y_units'] == b"mV"
    assert TEST_FILE.channel_info[0]['x_units'] == b"s"

    assert TEST_FILE.channel_info[1]['name'] == b"Blood Pressure"
    assert TEST_FILE.channel_info[1]['y_units'] == b"Pa"
    assert TEST_FILE.channel_info[1]['x_units'] == b"s"

def test_channel_data():
    assert len(TEST_FILE.channel_data) == 2
    assert len(TEST_FILE.channel_data[0]) == 3
    assert len(TEST_FILE.channel_data[1]) == 3

    assert len(TEST_FILE.channel_data[0][0]) == 256
    assert len(TEST_FILE.channel_data[0][2]) == 256

    # Test channel 0, data section 0
    assert TEST_FILE.channel_data[0][0][0] == 0.0
    assert TEST_FILE.channel_data[0][0][1] == 27.033599853515625
    assert TEST_FILE.channel_data[0][0][-1] == -27.033599853515625

    # Test channel 0, data section 1
    assert TEST_FILE.channel_data[0][2][0] == 0.0
    assert TEST_FILE.channel_data[0][2][1] == 27.033599853515625
    assert TEST_FILE.channel_data[0][2][-1] == -27.033599853515625

    assert TEST_FILE.channel_data[1][0][0] == 0.0
    assert TEST_FILE.channel_data[1][0][1] == 13.516799926757812
    assert TEST_FILE.channel_data[1][0][-1] == -13.516799926757812

    assert TEST_FILE.channel_data[1][2][0] == 0.0
    assert TEST_FILE.channel_data[1][2][1] == 13.516799926757812
    assert TEST_FILE.channel_data[1][2][-1] == -13.516799926757812
