import os
import sys
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
import yaml

from agent.util import log


# from agent.config import ServerConfigDTO

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def readPropertyFile(path: str, fileName: str) -> dict:
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
        completePath = os.path.join(BASE_PATH, fileName)
    else:
        completePath = os.path.join(BASE_PATH, path, fileName)
    readContent = dotenv_values(completePath, encoding="utf-8")
    log.debug(f"Read file content: {readContent}, basePath; {BASE_PATH}, filePath: {completePath}")
    return readContent


def __convertYamlToDict(yamlData, parentKey="", separator=".") -> dict[str, Any]:
    """
    将yaml 文件中配置的参数，转换成扁平化的key,value 对，处理后返回字典格式的数据
    Example:
        yaml 文件：
            server:
                ip: 127.0.0.1
                port: 3000
            names:
                - "Alice"
                - "join"
                - "peter"

        经过处理后输出：
            server.ip: 127.0.0.1
            server.port: 3000
            names.0: Alice
            names.1: join
            names.2: peter


    :param yamlData:
    :param parentKey:
    :param separator:
    :return:
    """
    if not yamlData:
        return
    items = []
    # 处理字典类型
    if isinstance(yamlData, dict):
        for k, v in yamlData.items():
            curKey = f"{parentKey}{separator}{k}" if parentKey else k
            # 递归处理嵌套字典，列表
            if isinstance(v, (dict, list)):
                items.extend(__convertYamlToDict(v, curKey, separator).items())
            else:
                # 非嵌套形式，直接添加到列表中
                items.append((curKey, v))
    elif isinstance(yamlData, list):
        for i, v in enumerate(yamlData):
            curKey = f"{parentKey}{separator}{i}" if parentKey else str(i)
            if isinstance(v, (dict, list)):
                items.extend(__convertYamlToDict(v, curKey, separator).items())
            else:
                items.append((curKey, v))

    return dict(items)

def get_file_absolute_path(target_path: str) -> Path:
    """ 统一获取文件绝对路径，兼容单文件打包， docker, 虚拟环境下打包
        返回： 绝对路径
    """
    if hasattr(sys, "_MEIPASS"):
        """ 适配 PyInstaller 打包， 临时文件目录 -》 真实文件目录 """
        project_root = Path(sys._MEIPASS)
    else:
        """ Docker, 开发环境， 虚拟环境 """
        currentModuler = Path(__file__).resolve()
        project_root = currentModuler.parent.parent
        # log.info(f"Parents: {project_root}, root: {currentModuler.root}")

    #  直接通过 / 拼接，会自动适配
    target_file_path = project_root / target_path

    if not target_file_path.exists():
        log.error(f"Can't find file: {target_path} in current find path: {target_file_path} !")
        raise Exception(f"Can't find file: {target_path} in current find path: {target_file_path} !")

    return target_file_path


def loadYamlToDict(fileName: str) -> dict[str, Any]:
    absolute_file_path = get_file_absolute_path(fileName)
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        configContent = yaml.safe_load(file)
        log.info(f"Yaml content: {configContent}")
        return __convertYamlToDict(configContent)

def loadYamlFile(fileName: str) -> Any:

    absolute_file_path = get_file_absolute_path(fileName)
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        configContent = yaml.safe_load(file)
        log.info(f"Yaml content: {configContent}")
        return configContent


if __name__ == "__main__":
    path = "resource"
    filename = "resource/application.yaml"
    # readcontent = readPropertyFile(path, fileName=filename)
    readcontent = loadYamlFile(fileName=filename)

    # serverConfigDto = ServerConfigDTO.model_validate(readcontent)
    log.info(f"ServerConfigDto: {readcontent}")
    # for k, v in readcontent.items():
    #     log.info(f"K: {k}, value: {v}")
