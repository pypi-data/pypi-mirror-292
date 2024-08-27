import array
import pathlib

class CFSFile:
    time: bytes
    date: bytes
    comment: bytes

    channel_data: list[list[array.array]]
    channel_info: list[dict]

    def __init__(self, filename: pathlib.Path) -> None: ...
