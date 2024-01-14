#这个py文件最好用vscode打开，用vs community 2022打开也行，但是需要在最顶上添加"#coding = gbk"注释，不然会报错


from os.path import exists
from json import loads
from os import system
from os import remove#这个函数用于把指定的文件给删掉 
from os.path import join
from sys import maxsize
import zipfile

#巨多for循环警告
#定义要启动的版本信息.exe"

'''
filename:需要解压的文件名
path:解压到的路径
'''
def unpress(filename: str, path: str):#解压文件
    try:
        Zip = zipfile.ZipFile(filename)
        for z in Zip.namelist():
            Zip.extract(z, path)
        Zip.close()
    except:
        return

def isMyversion(version: str, mcdir: str):#返回是否有这个版本
    print(mcdir + "\\versions\\" + version + "\\" +version + ".json")
    if(exists(mcdir + "\\versions\\" + version + "\\" +version + ".json")):
        return True
    else:
        return False

'''
version:游戏版本
javaw_path:javaw.exe路径
maxMen:最大运行内存
username:用户名
mcdir:Minecraft路径
'''
def run(mcdir: str, version: str, javaw_path: str, maxMen: str, username: str, userType: str, uuid: str, access_token: str):#启动游戏
    #微软登录
    # res_auth = MicAuth.OAuth()
    #if not res_auth == {}:
    commandLine = str("")#启动命令
    JVM = str("")#JVM参数
    classpath = str("")#普通库文件路径
    mc_args = str("")#mc参数

    if((not javaw_path == "")\
        and (not version == "")\
        and (not maxMen == "")\
        and (not username == "")\
        and (not mcdir == "")):
        if(isMyversion(version, mcdir)):
            version_json = open(mcdir + "\\versions\\" + version + "\\" +version + ".json", "r")
            dic = loads(version_json.read())
            version_json.close()
            #将本地库文件解压至natives文件夹
            for lib in dic["libraries"]:
                if "classifiers" in lib['downloads']:
                    for native in lib['downloads']:#这一步是因为本地库里面有多个库,所以要历遍所有库
                        if native == "artifact":
                            dirct_path = mcdir + "\\versions\\" + version + "\\" + version + "-natives"#解压到的目标路径
                            filepath = mcdir + "\\libraries\\" + lib["downloads"][native]['path']#要解压的artifact库
                            unpress(filepath, dirct_path)
                        elif native == 'classifiers':
                            for n in lib['downloads'][native].values():
                                #dirct_path = mcdir + "\\libraries\\" + lib["downloads"][native]['path']
                                dirct_path = mcdir + "\\versions\\" + version + "\\" + version + "-natives"
                                filepath = mcdir + "\\libraries\\" + n["path"]#classifiers的路径
                                unpress(filepath, dirct_path)
            JVM = '"'+javaw_path+'" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy' +\
            ' -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True '+\
            '-Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true '+\
            '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump '+\
            '-Dos.name="Windows 10" -Dos.version=10.0 -Djava.library.path="'+\
            mcdir + "\\versions\\" + version + "\\" + version + "-natives" +\
            '" -Dminecraft.launcher.brand=launcher '+\
            '-Dminecraft.launcher.version=1.0.0 -cp'
            classpath += '"'#这一句我在教程里面写错了，应该填加在这里，让-cp以引号开头
            '''
            #将普通库文件路径传入-cp参数
            for lib in dic["libraries"]:
                if not 'classifiers' in lib["downloads"]:
                    normal = mcdir + "\\libraries\\" +lib["downloads"]["artifact"]["path"]#普通库路径
                    classpath += normal + ";"#将普通库路径追加到-cp后面
            '''
            for libraries in dic['libraries']:
                if not 'classifiers' in libraries['downloads']:
                    normal_lib_path = join(
                        join(mcdir, "libraries"), libraries['downloads']['artifact']['path'])
                    if exists("C:\\Program Files (x86)"):#64位操作系统
                        if "3.2.1" in normal_lib_path:
                            continue
                        else:
                            classpath += normal_lib_path + ";"
                    else:#32位操作系统
                        if "3.2.2" in normal_lib_path:
                            continue
                        else:
                            classpath += normal_lib_path + ";"
            #将客户端文件传入-cp参数
            classpath = classpath + mcdir + "\\versions\\" + version + "\\" + version + ".jar" + '"'
            #设置最大运行内存
            JVM = JVM + " " + classpath + " -Xmx" + maxMen + " -Xmn256m -Dlog4j.formatMsgNoLookups=true"
            #最大内存由变量maxMen决定,最小内存是256M

            #配置Minecraft参数
            #将主类传入Minecraft参数
            mc_args += dic["mainClass"] + " "
            for arg in dic["arguments"]["game"]:
                if isinstance(arg, str):
                    mc_args += arg + " "
                elif isinstance(arg, dict):#无论是什么，只要是在大括号里括着的，都被python认为是字典类型
                    if isinstance(arg["value"], list):
                        for a in arg["value"]:
                            mc_args += a + " "
                    elif isinstance(arg["value"], str):
                        mc_args += arg["value"] + " "
            #将模板替换为具体数值
            mc_args = mc_args.replace("${auth_player_name}", username)#玩家名称
            mc_args = mc_args.replace("${version_name}", version)#版本名称
            mc_args = mc_args.replace("${game_directory}", mcdir)#mc路径
            mc_args = mc_args.replace("${assets_root}", mcdir + "\\assets")#资源文件路径
            mc_args = mc_args.replace("${assets_index_name}",dic["assetIndex"]["id"])#资源索引文件名称
            mc_args = mc_args.replace("${auth_uuid}", uuid)#由于没有写微软登录,所以uuid为空的
            mc_args = mc_args.replace("${auth_access_token}", access_token)#同上
            mc_args = mc_args.replace("${clientid}", version)#客户端id
            mc_args = mc_args.replace("${auth_xuid}", "{}")#离线登录,不填
            mc_args = mc_args.replace("${user_type}", userType)#用户类型,离线模式是Legacy
            mc_args = mc_args.replace("${version_type}", dic["type"])#版本类型
            mc_args = mc_args.replace("${resolution_width}", "1000")#窗口宽度
            mc_args = mc_args.replace("${resolution_height}", "800")#窗口高度
            mc_args = mc_args.replace("-demo ", "")#去掉-demo参数，退出试玩版
            #组装命令条
            commandLine = JVM + " " + mc_args
            #使用bat的方法运行过长的命令条
            bat = open("run.bat", "w")
            bat.write(commandLine)
            bat.close()
            system("run.bat")
            #视频中没有讲到的,在运行完Minecraft之后，删除run.bat，这样可以避免与其他文件冲突(如果真有人写了一个运行py文件的.bat文件，名字叫run.bat的话,别问我怎么知道的)
            remove("run.bat")
    #else:
        #print("登陆出现错误,请重试，可能是您没有购买Minecraft")


if __name__ == "__main__":
    run(".\\.minecraft", "1.14.4", "C:\\Program Files\\Java\\jdk-18.0.2\\bin\\javaw.exe", "1024m", "114514", "Legacy", "{}", "{}", 64)
