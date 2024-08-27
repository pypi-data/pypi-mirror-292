import CFS._routines as routines
from os import fsencode
from pathlib import Path

TEST_FILENAME = Path(__file__).parent.joinpath("test_data/test_file.cfs")

def test_open_cfsfile():
    assert routines.open_cfs_file(str(TEST_FILENAME)) > 0
