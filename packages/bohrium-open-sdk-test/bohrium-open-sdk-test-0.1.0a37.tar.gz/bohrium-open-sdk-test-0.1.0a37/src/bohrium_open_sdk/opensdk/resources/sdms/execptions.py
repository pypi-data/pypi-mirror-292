__all__ = [
    "SdmsException",
    "SdmsFileNotFoundError",
    "SdmsFileDuplicateError",
    "SdmsInvalidFileFormatError",
    "SdmsUnknownError",
    "SdmsSampleNotFoundError",
]


class SdmsException(Exception):
    """基础异常类"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SdmsFileNotFoundError(SdmsException):
    """当文件不存在时抛出此异常"""

    pass


class SdmsFileDuplicateError(SdmsException):
    """当文件重名时抛出此异常"""

    pass


class SdmsInvalidFileFormatError(SdmsException):
    """当文件格式不正确时抛出此异常"""

    pass


class SdmsUnknownError(SdmsException):
    """当发生未知错误时抛出此异常"""

    pass


class SdmsSampleNotFoundError(SdmsException):
    """当样品不存在时抛出此异常"""

    pass
