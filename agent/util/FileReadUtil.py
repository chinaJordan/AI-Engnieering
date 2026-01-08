import os
from dotenv import dotenv_values

from agent.util import log

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def readPropertyFile(path: str, fileName: str ) -> dict:
    """
    根据传入的路径路径读取properties 格式文件，以字典形式返回读取的内容
    Example:
        path = "dev" , filename = "dev.properties",
        the complete file path is : BASE_PATH + "/" +path + "/" + filename,
        BASE_PATH is the project root directory, which is system default acquire!

        Note: path param don't start with "/", otherwise the finally value is :
        path + filename.

    :param path:
    :param fileName:
    :return:
    """
    if not fileName:
        raise Exception("filename param can't be Null!")
    if not path:
        path = "/resource"
    completePath = os.path.join(BASE_PATH, path, fileName)
    readContent = dotenv_values(completePath,encoding="utf-8")
    log.debug(f"Read file content: {readContent},basePath; {BASE_PATH}, filePath: {completePath}")
    return readContent;


if __name__ == "__main__":
    path = "resource"
    filename = "application.properties"
    readcontent = readPropertyFile(path,fileName=filename)
    for k, v in readcontent.items():
        log.info(f"K: {k}, value: {v}")