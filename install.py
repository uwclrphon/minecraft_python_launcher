from urllib.request import urlretrieve, install_opener, build_opener # 导入下载函数
from random import choice
from sys import stdout
from os.path import exists
from os import makedirs
from json import loads
from os.path import split
from os import system
from threading import Thread

#下载文件函数
def download(url: str, path: str):
    try:
        (filepath, filename) = split(path)
        opener = build_opener()
        # 构建请求头列表每次随机选择一个
        ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'
                ]
        opener.addheaders = [('User-Agent', choice(ua_list))]
        install_opener(opener)
        if not exists(filepath):
            makedirs(filepath)
        def hook(blocknum, bs, size): # urlretrieve 的回调函数 
            # blocknum:数据块数量
            # bs:数据块大小
            # size:下载下来的总大小
            # 下载进度=(blocknum x bs) / size
            a = int(float(blocknum * bs) / size * 100)
            if a > 100:
                a = 100
            stdout.write("\r >>正在下载" + filename + ":" + str(a) + "%")
        urlretrieve(url=url, filename=path, reporthook=hook)
        print("\n")
    except:
        print("\n由于网络原因,下载发生错误,正在尝试重新下载\n")
        download(url=url, path=path)

# 下载版本清单文件
def downloadList(downloadFrom: str):
    # 下载版本清单文件
    if downloadFrom == "mojang":
        url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    elif downloadFrom == "BMCLAPI":
        url = "https://bmclapi2.bangbang93.com/mc/game/version_manifest.json"
    elif downloadFrom == "MCDDS":
        url = "https://download.mcbbs.net/mc/game/version_manifest.json"
    path = "./version_manifest.json"
    download(url=url, path=path)
    print("下载完成\n")

# 输出版本清单
def OutVersion(downloadFrom: str, isOut = False, release = False, snapshot = False, old = False):
    # isOut:是否在屏幕上输出版本列表
    # release:是否输出或返回正式版本
    # snapshot:是否输出或返回测试版本
    # old:是否输出或返回远古版本
    if not exists("./version_manifest.json"):
        downloadList(downloadFrom)
    file = open("./version_manifest.json")
    VersionListDict = loads(file.read())
    for v in VersionListDict["versions"]:
        if isOut: # 输出版本列表
            if release:
                if v["type"] == "release":
                    print("版本号:" + v["id"] + " 版本类型:" + v["type"])
            if snapshot:
                if v["type"] == "release":
                    print("版本号:" + v["id"] + " 版本类型:" + v["type"])
            if old:
                if "old" in v["type"]: # 这里判断old是否在类型里面
                    print("版本号:" + v["id"] + " 版本类型:" + v["type"])

    return VersionListDict

# 判断版本是否在版本清单内
def isRightVersion(version: str, downloadFrom: str):
    VLD = OutVersion(downloadFrom)
    flag = False # 判断参数中的版本号是否与版本列表相匹配
    for v in VLD["versions"]:
        if v["id"] == version:
            flag = True
    return flag


# 下载游戏版本
def downloadVersion(version: str, mcDir: str, downloadFrom: str):
    Threads = []#线程池

    #version:要下载的版本
    #mcDir:要下载到的.minecraft根目录

    #1,下载版本json文件
    if isRightVersion(version, downloadFrom):
        VLD = OutVersion(downloadFrom)
        for v in VLD["versions"]:
            if v["id"] == version:
                if downloadFrom == "mojang":
                    url = v["url"]
                elif downloadFrom == "BMCLAPI":
                    url = str(v["url"]).replace("https://launchermeta.mojang.com/", "https://bmclapidoc.bangbang93.com/")
                elif downloadFrom == "MCBBS":
                    url = str(v["url"]).replace("https://launchermeta.mojang.com/", "https://download.mcbbs.net/")
                path = mcDir + "\\versions\\" + version + "\\" + version + ".json"
                download(url=url, path=path)
    print("\n版本json文件下载完成\n")
    #2,下载客户端文件
    file = open(mcDir + "\\versions\\" + version + "\\" + version + ".json")
    VersionDict = loads(file.read())
    #url = VersionDict["downloads"]["client"]["url"]
    url = f"https://bmclapi2.bangbang93.com/version/{version}/client"
    path = mcDir + "\\versions\\" + version + "\\" + version + ".jar"
    download(url=url, path=path)
    print("\n客户端文件下载完成\n")

    #3, 下载依赖库
    for lib in VersionDict["libraries"]:
        #下载普通库
        if "artifact" in lib["downloads"] and not "classifiers" in lib["downloads"]:
            if downloadFrom == "mojang":
                url = str(lib["downloads"]["artifact"]["url"])
            elif downloadFrom == "BMCLAPI":
                url = str(lib["downloads"]["artifact"]["url"]).replace("https://libraries.minecraft.net/", "https://bmclapi2.bangbang93.com/maven/")
            elif downloadFrom == "MCBBS":
                url = str(lib["downloads"]["artifact"]["url"]).replace("https://libraries.minecraft.net/", "https://download.mcbbs.net/maven/")
            path = mcDir + "\\libraries\\" + lib["downloads"]["artifact"]["path"]
    
            download(url=url, path=path)
        #下载natives库
        if "classifiers" in lib["downloads"]:
            #下载natives库中的artifact部分
            if "artifact" in lib["downloads"]:
                if downloadFrom == "mojang":
                    url = str(lib["downloads"]["artifact"]["url"])
                elif downloadFrom == "BMCLAPI":
                    url = str(lib["downloads"]["artifact"]["url"]).replace("https://libraries.minecraft.net/", "https://bmclapi2.bangbang93.com/maven/")
                elif downloadFrom == "MCBBS":
                    url = str(lib["downloads"]["artifact"]["url"]).replace("https://libraries.minecraft.net/", "https://download.mcbbs.net/maven/")
                path = mcDir + "\\libraries\\" + lib["downloads"]["artifact"]["path"]
            
                download(url=url, path=path)
            #下载classifiers部分
            for cl in lib["downloads"]["classifiers"].values():
                if downloadFrom == "mojang":
                    url = cl["url"]
                elif downloadFrom == "BMCLAPI":
                    url = str(cl["url"]).replace("https://libraries.minecraft.net/", "https://bmclapi2.bangbang93.com/maven/")
                elif downloadFrom == "MCBBS":
                    url = str(cl["url"]).replace("https://libraries.minecraft.net/", "https://download.mcbbs.net/maven/")
            
                path = mcDir + "\\libraries\\" + cl["path"]
          
                download(url=url, path=path)
    print("\n依赖库下载完成\n")

    #4,下载资源索引
    if downloadFrom == "mojang":
        url = VersionDict["assetIndex"]["url"]
    elif downloadFrom == "BMCLAPI":
        url = str(VersionDict["assetIndex"]["url"]).replace("https://launcher.mojang.com/", "https://bmclapi2.bangbang93.com/")
    elif downloadFrom == "MCBBS":
        url = str(VersionDict["assetIndex"]["url"]).replace("https://launcher.mojang.com/", "https://download.mcbbs.net/")
    path = mcDir + "\\assets\\indexes\\" + VersionDict["assetIndex"]["id"] + ".json"
    download(url=url, path=path)
    print("\n资源索引文件下载完成\n")

    #5,下载资源文件(增加下载速度，用多线程下载)
    #解析资源索引文件
    for object in loads(open(path, "r").read())["objects"].values():
        if downloadFrom == "mojang":
            url = f"https://resources.download.minecraft.net/{object['hash'][0:2]}/{object['hash']}"
        elif downloadFrom == "BMCLAPI":
            url = f"https://bmclapi2.bangbang93.com/assets/{object['hash'][0:2]}/{object['hash']}"
        elif downloadFrom == "MCBBS":
            url = f"https://download.mcbbs.net/assets/{object['hash'][0:2]}/{object['hash']}"
        path = f"{mcDir}\\assets\\objects\\{object['hash'][0:2]}\\{object['hash']}"
        if not exists(path):
            def runnable():
                if not exists(f"{mcDir}\\assets\\objects\\{object['hash'][0:2]}"):
                    makedirs(f"{mcDir}\\assets\\objects\\{object['hash'][0:2]}")
                print(object['hash'])
                urlretrieve(url=url, filename=path)
            thread = Thread(target=runnable)
            thread.start()
            Threads.append(thread)
            #少许停顿，避免冲突
            i = 7
            while i > 0:
                i -= 1

    #等待线程池中的所有线程进行完成:
    for th in Threads:
        th.join()
    #download_version("1.18.2")
