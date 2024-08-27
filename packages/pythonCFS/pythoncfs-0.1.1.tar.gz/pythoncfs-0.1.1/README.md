# Python CFS

![](https://github.com/m0ose01/pythonCFS/actions/workflows/test.yml/badge.svg)
![](https://github.com/m0ose01/pythonCFS/actions/workflows/publish.yml/badge.svg)

The Cambridge Electronic Design File System (CFS) is the file format used by the Signal Software Suite to record electrophysiological data, such as data from Transcranial Magnetic Stimulation experiments.

This is a Python wrapper for my [other project](https://github.com/m0ose01/CFS), which reimplements some of the public API of CED's own C library to read CFS files.

## Installation

Download the latest release of pythonCFS using pip:
```
pip install pythonCFS
```

If you have problems installing pythonCFS, file an [issue](https://github.com/m0ose01/pythonCFS/issues).

## Example Usage

This script loads a CFS file, `my_cfs_file.cfs`, and plots a single data section, from the first channel.

```python
from CFS.CFSFile import CFSFile
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    # Load a CFS file by creating an instance of the 'CFS' class.
    file = Path("./my_cfs_file.cfs")
    data = CFSFile(file)

    channel = 0
    data_section = 0

    # Channel data are stored as native python arrays.
    plt.plot(data.channel_data[channel][data_section])
    plt.show()

if __name__ == '__main__':
    main()
```

## Future Goals

- Document public interface.
- Allow access to file/data section variables.
- Fix bugs, improve usability of public API.
- Implement support for data types other than INT2 and RL4 (will require additions to underlying C library).
