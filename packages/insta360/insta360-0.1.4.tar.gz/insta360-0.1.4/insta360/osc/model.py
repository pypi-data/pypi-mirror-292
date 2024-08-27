import base64

from enum import Enum
from pydantic import BaseModel


class ListFileType(Enum):
    """
    Enum for listing file types.

    Attributes:
        IMAGE: Image files.
        VIDEO: Video files.
        ALL: All files.
    """

    IMAGE: str = "image"
    VIDEO: str = "video"
    ALL: str = "all"


class Thumbnail(BaseModel):
    """
    Model for thumbnail of a file.

    Attributes:
        base64: Base64 encoded thumbnail.
        content: Decoded content of the thumbnail.
    """

    def __init__(self, **data):
        super().__init__(**data)
        self.base64: str | None = data.get("thumbnail", None)
        self.content: bytes | None = None

        if self.base64 == "":
            self.base64 = None

        if self.base64:
            thumbnail_bytes = self.base64.encode()
            self.content = base64.b64decode(thumbnail_bytes)

    class Config:
        extra = "allow"


class Entry(BaseModel):
    """
    Model for file entries in list files response.

    Attributes:
        name: Name of the file.
        fileUrl: URL of the file.
        localFileUrl: Local URL of the file.
        size: Size of the file.
        width: Width of the file.
        height: Height of the file.
        dateTimeZone: Date time zone of the file.
        dateTime: Date time of the file.
        thumbnailSize: Thumbnail size of the file.
        isProcessed: Is the file processed.
        previewUrl: URL of the preview.
        thumbnail: Thumbnail object.
    """

    name: str
    fileUrl: str
    size: int
    width: int
    height: int
    dateTimeZone: str
    isProcessed: bool
    previewUrl: str

    def __init__(self, **data):
        super().__init__(**data)
        self.localFileUrl: str | None = data.get("_localFileUrl", None)
        self.dateTime: str | None = data.get("_dateTime", None)
        self.thumbnailSize: int | None = data.get("_thumbnailSize", None)
        self.thumbnail: Thumbnail = Thumbnail(**data)

    class Config:
        extra = "allow"


class ListFilesResults(BaseModel):
    """
    Model for results of list files response.

    Attributes:
        entries: List of file entries.
        totalEntries: Total number of entries.
    """

    entries: list[Entry]
    totalEntries: int


class DeleteFilesResults(BaseModel):
    """
    Model for results of delete files response.

    Attributes:
        fileUrls: List of file URLs.
    """

    fileUrls: list[str]


class OSCResponse(BaseModel):
    """
    Model for list files response.

    Attributes:
        name: Name of the response.
        state: State of the response.
    """

    name: str
    state: str


class Error(BaseModel):
    """
    Model for osc error.

    Attributes:
        code: Error code.
        message: Error message.
    """

    code: str
    message: str


class ErrorResponse(BaseModel):
    """
    Model for osc error response.

    Attributes:
        error: osc error.
    """

    error: Error


class ListFilesResponse(OSCResponse):
    """
    Model for list files response.

    Attributes:
        results: List files results.
    """

    results: ListFilesResults


class DeleteFilesResponse(OSCResponse):
    """
    Model for delete files response.

    Attributes:
        results: Delete files results.
    """

    results: DeleteFilesResults
