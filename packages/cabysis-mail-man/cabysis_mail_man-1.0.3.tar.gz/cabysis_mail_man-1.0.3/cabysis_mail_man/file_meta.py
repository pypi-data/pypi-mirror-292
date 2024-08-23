import mimetypes


def get_file_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "application/octet-stream"


class FileMeta:
    def __new__(cls, *args, **kwargs):
        file_path = kwargs.get("file_path")
        buffer = kwargs.get("buffer")

        if file_path is not None and buffer is None:
            return super(FileMeta, cls).__new__(FileMetaPath)
        elif buffer is not None and file_path is None:
            if "file_name" in kwargs:
                return super(FileMeta, cls).__new__(FileMetaBuffer)
            else:
                raise ValueError(
                    "FileMetaBuffer requires 'file_name' when 'buffer' is provided."
                )
        else:
            raise ValueError(
                "FileMeta requires either 'file_path' or 'buffer', but not both."
            )

    def __init__(
        self,
        file_path: str = None,
        file_type: str = None,
        buffer: any = None,
        file_name: str = None,
    ):
        pass


class FileMetaPath(FileMeta):
    def __init__(self, *args, **kwargs):
        self.file_path = kwargs.get("file_path")
        self.file_type = get_file_type(self.file_path)
        self.buffer = None
        self.file_name = None

        super().__init__(*args, **kwargs)


class FileMetaBuffer(FileMeta):
    def __init__(self, *args, **kwargs):
        self.file_path = None
        self.file_type = None
        self.buffer = kwargs.get("buffer")
        self.file_name = kwargs.get("file_name")

        super().__init__(*args, **kwargs)
