import MicAuth#微软登录模块
import launcher#启动模块
import install#安装模块
from os.path import exists 
from json import dumps
from json import loads
from sys import maxsize

def help():
    print("欢迎使用启动器\n"
    "下面是命令帮助:\n"
    "")

if __name__ == "__main__":
    if not exists("launcherOptions.json"):
        launcher_options_json = open("launcherOptions.json", "w")
        launcherOptions = {#默认启动器设置
            "game": {
                "maxMen": "1024M", #最大内存
                "mcDir": "./.minecraft", #mc根目录
                "javawPath": "", #javaw.exe的路径
                "downloadFrom": "mojang"
            },
            "user": {
                "username": "",
                "userType": "",
                "access_token": "",
                "uuid": "",
            }
        }
        launcher_options_json.write(dumps(launcherOptions))#把json写入文件
        launcher_options_json.close()
    else:
        launcher_options_json = open("launcherOptions.json", "r")#读取
        launcherOptions = loads(launcher_options_json.read())
    #用户信息
    username = launcherOptions["user"]["username"]
    userType = launcherOptions["user"]["userType"]
    access_token = launcherOptions["user"]["access_token"]
    uuid = launcherOptions["user"]["uuid"]
    #游戏信息
    maxMen = launcherOptions["game"]["maxMen"]
    mcDir = launcherOptions["game"]["mcDir"]
    javawPath = launcherOptions["game"]["javawPath"]
    downloadFrom = launcherOptions["game"]["downloadFrom"]
    #游戏信息的读取
    help()
    while True:
        #命令输入
        command = input(">>>")

        if(command == "MaxMen"):
            maxMen = input("\n请输入最大运行内存:")
            launcherOptions["game"]["maxMen"] = maxMen
        elif(command == "mcDir"):
            mcDir = input("\n请输入游戏根目录:")
            launcherOptions["game"]["mcDir"] = mcDir
        elif(command == "javawPath"):
            javawPath = input("\n请输入javaw.exe路径:")
            launcherOptions["game"]["javawPath"] = javawPath
        elif(command == "downloadFrom"):
            downloadFrom = input("\n请输入下载源名称(mojang/BMCLAPI/MCBBS):")
            launcherOptions["game"]["downloadFrom"] = downloadFrom
        
        #登录
        elif(command == "login"):
            type = input("\n请输入登陆方式(离线/微软):")
            if(type == "离线"):
                userType = "Legacy"
                username = input("\n请输入用户名:")
                uuid = "{}"
                access_token = "{}"
            elif(type == "微软"):
                userType = "mca"
                loginm = MicAuth.OAuth()
                username = loginm["username"]
                uuid = loginm["uuid"]
                access_token = loginm["access_token"]
            launcherOptions["user"]["username"] = username
            launcherOptions["user"]["uuid"] = uuid
            launcherOptions["user"]["access_token"] = access_token
            launcherOptions["user"]["userType"] = userType
        elif(command == "quit"):
            break
        elif(command == "help"):
            help()
        
        #启动游戏
        elif(command == "run"):
            version = input("\n请输入要启动的版本:")
            #检测信息是否齐全
            if username == "":
                print("\n您尚未登录,请先登录")
            elif mcDir == "":
                print("\n您的游戏根目录为空")
            elif maxMen == "":
                print("\n您的最大运行内存为空")
            else:
                print("\n正在为您启动游戏")
                launcher.run(mcDir, version, javawPath, maxMen, username, userType, uuid, access_token)
        #安装游戏
        elif(command == "install"):
            version = input("\n请输入要安装的游戏版本:")
            install.downloadVersion(version, mcDir, downloadFrom)
        
        #放在循环里面，好让启动器设置及时更新
        launcher_options_json = open("launcherOptions.json", "w")#写入
        launcher_options_json.write(dumps(launcherOptions))#将修改后的信息写入json文件
        launcher_options_json.close()


