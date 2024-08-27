import os
import json
import sys

from networkx.algorithms.isomorphism.matchhelpers import tmpdoc

from .fd_httpclient import FDHttpClient
from .chat._client import FourthDimensionAI
from .fd_utils import *
fdHttpClient = FDHttpClient()
package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
resource_path = os.path.join(package_path, "resources")
config_path = os.path.join(resource_path, "fd_python_config.json")

class FDClient:
    def __init__(self, server_url=None):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 如果提供了server_url参数，则使用它，否则从配置文件中读取
        if server_url is not None:
            self.Baseurl = server_url + "/"
        else:
            self.Baseurl = self.config["url"]["base_url"] + "/"
        self.NO_OPERATION = 0x00
        self.CHUNK_EMBEDDING = 0x01
        self.SENTENCE_EMBEDDING = 0x02
        self.SUMMARIZING = 0x08
        self.CHUNK_SUMMARIZING = 0x10
        self.SELF_ASKING = 0x04
        # self.CHUNK_SELF_ASKING = 0x20

    def setServeUrl(self, serve_url):
        """用于设置BaseUrl"""
        self.Baseurl = serve_url + "/"

    def getKBInfo(self, KBName):
        """用于获取知识库信息"""
        try:
            requestdata = create_dict_from_kwargs(kbName=KBName)
            result = fdHttpClient.send_request(url=self.Baseurl + "getKBInfo", json_data=requestdata, method="POST")
            print("信息获取成功")
            return result["data"]
        except Exception as e:
            print(e)
            print("信息获取失败")
            return {"code": -1,"msg":"发生错误"}

    def getFDInfo(self):
        """用于获取知识库信息"""
        try:
            requestdata = create_dict_from_kwargs()
            result = fdHttpClient.send_request(url=self.Baseurl + "getFDInfo", json_data=requestdata, method="POST")
            print("信息获取成功")
            return result["data"]
        except Exception as e:
            print(e)
            print("信息获取失败")
            return {"code": -1,"msg":"发生错误"}


    def createKB(self, KBName):
        """用于创建知识库"""
        try:
            requestdata = create_dict_from_kwargs(kbName=KBName)
            result = fdHttpClient.send_request(url=self.Baseurl + "createKB", json_data=requestdata, method="POST")
            print(result["msg"] )
            return result
        except Exception as e:
            print(e)
            print("创建失败")
            return {"code": -1,"msg":"发生错误"}

    def deleteKB(self, KBName):
        """用于删除知识库"""
        try:
            requestdata = create_dict_from_kwargs(kbName=KBName)
            result = fdHttpClient.send_request(url=self.Baseurl + "deleteKB", json_data=requestdata, method="POST")
            print(result["msg"])
            return result
        except Exception as e:
            print(e)
            print("删除失败")
            return {"code": -1,"msg":"发生错误"}

    def importDocuments(self, KBName, targetFileName, rumination = 0):
        """用于导入文件夹"""
        try:
            print("开始文件的导入")
            data_url = get_absolute_path(targetFileName).replace(".", "").replace("//", "/")
            data_file_name = os.path.basename(targetFileName)
            Document_list = get_all_file_paths(targetFileName)
            for Document_Path in Document_list:
                files = {"file": open(Document_Path, "rb")}
                url = Document_Path[len(data_url) - len(data_file_name) - 1:].replace("\\", "/").replace(".", "")
                if url[0] != "/":
                    url = "/" + url
                requestdata = create_dict_from_kwargs(kbName=KBName, targetFileName=url, rumination=rumination)
                result = fdHttpClient.send_request_fromdata(url=self.Baseurl + "addDocument", data=requestdata,
                                                            files=files, method="POST")
                print(Document_Path + result["msg"])
            result["msg"] = "文件夹导入成功"
            return result
        except Exception as e:
            print(e)
            print("导入失败")
            return {"code": -1,"msg":"发生错误"}

    def addDocument(self, KBName, sourceFileName, rumination = 0):
        """用于添加文档"""
        try:
            files = {"file": open(sourceFileName, "rb")}
            sourceFileName = os.path.basename(sourceFileName)
            requestdata = create_dict_from_kwargs(kbName=KBName, targetFileName="/" + sourceFileName,
                                                  rumination=rumination)

            result = fdHttpClient.send_request_fromdata(url=self.Baseurl + "addDocument", data=requestdata, files=files,
                                                        method="POST")
            print(result["msg"])
            return result
        except Exception as e:
            print(e)
            print("添加失败")
            return {"code": -1,"msg":"发生错误"}

    def deleteDocument(self, KBName,  targetFileName):
        """用于删除文档"""
        # targetFileName = get_absolute_path(targetFileName)
        try:
            if (targetFileName[0] != "/"):
                targetFileName = "/" + targetFileName
            targetFileName.replace("\\", "/")
            requestdata = create_dict_from_kwargs(kbName=KBName, targetFileName=targetFileName)
            result = fdHttpClient.send_request(url=self.Baseurl + "deleteDocument", json_data=requestdata,
                                               method="POST")
            print(result["msg"])
            return result
        except Exception as e:
            print(e)
            print("删除失败")
            return {"code": -1,"msg":"发生错误"}

    def updateDocument(self, KBName, sourceFileName, targetFileName, rumination = 0):
        """用于更新文档"""
        try:
            sourceFileName = get_absolute_path(sourceFileName)
            if (targetFileName[0] != "/"):
                targetFileName = "/" + targetFileName
            targetFileName.replace("\\", "/")
            files = {"file": open(sourceFileName, "rb")}
            requestdata = create_dict_from_kwargs(kbName=KBName, sourceFileName=sourceFileName,
                                                  targetFileName=targetFileName, rumination=rumination)
            result = fdHttpClient.send_request_fromdata(url=self.Baseurl + "updateDocument", data=requestdata,
                                                        files=files, method="POST")
            print("更新成功" + "\n")
            return result
        except Exception as e:
            print(e)
            print("更新失败")
            return {"code": -1,"msg":"发生错误"}

    def recallDocuments(self, KBName, question):
        """用于查询"""
        try:
            requestdata = create_dict_from_kwargs(kbName=KBName, question=question)
            result = fdHttpClient.send_request(url=self.Baseurl + "recall", json_data=requestdata, method="POST")
            print(result["msg"])
            return result
        except Exception as e:
            print(e)
            print("查询失败")
            return {"code": -1,"msg":"发生错误"}

    def query(self, KBName, question):
        """获取查询和生成回答"""
        try:
            client = FourthDimensionAI(base_url=self.Baseurl + "query")
            result = client.chat.completions.create(
                model="qwen",
                question=question,
                kbName=KBName,
                messages=[],
                stream=False,
                rumination=None
            )
            return result.data
        except Exception as e:
            print(e)
            print("查询失败")
            return {"code": -1,"msg":"发生错误"}

    # def ruminate_stream(self, KBName, rumination):
    #     """流式获取反刍结果"""
    #     client = FourthDimensionAI(base_url=self.Baseurl + "ruminate_stream")
    #     result = client.chat.completions.create(
    #         model="qwen",
    #         question=None,
    #         kbName=KBName,
    #         rumination=rumination,
    #         messages=[],
    #         stream=True
    #     )
    #     # print(result)
    #     for chunk in result:
    #         i = int(float(chunk.choices[0].delta.content )*100)
    #         # print(chunk.choices[0].delta.content, end='')
    #         # print("\n")
    #         print("\r", end="")
    #         print("进度: {}%: ".format(i), "▓" * (i // 2), end="")
    #         sys.stdout.flush()
    #     return result

    def ruminate(self, KBName, rumination):
        """用于创建反刍线程以及进行轮询"""
        starttime = time.time()
        try:
            requestdata = create_dict_from_kwargs(kbName=KBName, rumination=rumination)
            fdHttpClient.send_request(url=self.Baseurl + "ruminate_start", json_data=requestdata, method="POST")
            result = {}
            tmp = ""
            cout = 5
            while (True):
                response_data = \
                    fdHttpClient.send_request(url=self.Baseurl + "ruminate_polling", json_data=requestdata,
                                              method="POST")[
                        "data"]

                if response_data["process_cout"] == None and response_data["process"] != None and response_data[
                    "process"] != "NO_OPERATION":
                    continue
                elif response_data["process"] == "NO_OPERATION":
                    cout = cout - 1
                    if cout == 0:
                        result["msg"] = "反刍完成"
                        result["data"] = None
                        result["code"] = 0
                        print("\n反刍完成")
                        break

                process = response_data["process"]
                if response_data["process_cout"] == None:
                    process_cout = {
                        "cout": 0,
                        "total": 1
                    }
                else:
                    process_cout = response_data["process_cout"]
                nowtime = time.time()
                usedtime = nowtime - starttime
                print("\r", end="")
                if process == "NO_OPERATION" or process == "PREPARED":
                    print("\nwaiting")
                    # sys.stdout.flush()
                    # pass
                else:
                    if process_cout["cout"] == 0:
                        print("知识库 " + process.strip("not_") + "反刍进度: {}%, ".format(
                            int(process_cout["cout"] * 100 / process_cout["total"])),
                              "▓" * (int(process_cout["cout"] * 100 / process_cout["total"]) // 2), end="")

                    else:
                        print("知识库 " + process.strip("not_") + "反刍进度: {}%, ".format(
                            int(process_cout["cout"] * 100 / process_cout["total"])),
                              "知识库 " + process.strip("not_") + "预计用时: {}s: ".format(
                                  int(usedtime / (process_cout["cout"] / process_cout["total"]))),
                              "▓" * (int(process_cout["cout"] * 100 / process_cout["total"]) // 2), end="")
                    sys.stdout.flush()
                if int(process_cout["cout"] * 100 / process_cout["total"]) == 100:
                    if process != "NO_OPERATION" and tmp != process:
                        print("\n\n\n")
                        starttime = time.time()
                time.sleep(2)
                tmp = process
            return result
        except Exception as e:
            print(e)
            print("创建反刍失败")
            return {"code": -1, "msg": "发生错误"}



