# Python CFS

![](https://github.com/m0ose01/pythonCFS/actions/workflows/test.yml/badge.svg)
![](https://github.com/m0ose01/pythonCFS/actions/workflows/publish.yml/badge.svg)

The Cambridge Electronic Design File System (CFS) is the file format used by the Signal Software Suite to record electrophysiological data, such as data from Transcranial Magnetic Stimulation experiments.

This is a Python wrapper for my [other project](https://github.com/m0ose01/CFS), which reimplements some of the public API of CED's own C library to read CFS files.

## Installation

Currently, pythonCFS is not available on PyPI.
As an alternative, you can download wheels directly from the [releases](https://github.com/m0ose01/pythonCFS/releases) page.
You will have to read the wheel's filename to determine the correct wheel for your system.

## Example Usage

This script loads a CFS file, `my_cfs_file.cfs`, and plots a single data section, from the first channel.

```python
from CFS.CFSFile import CFSFile
import matplotlib.pyplot as plt

def main():
    # Load a CFS file by creating an instance of the 'CFS' class.
    data = CFSFile(b"./my_cfs_file.cfs")

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
