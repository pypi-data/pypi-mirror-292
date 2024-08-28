# 导包
import os
import shutil
import random
import time
import re

def delete(Path) -> str:# 用来删除文件
    if os.path.isdir(Path):
        shutil.rmtree(Path)
    else:
        os.remove(Path)

def random_list_select(LiSt,number) -> list|int:# 随机选取LiSt中的number个元素组成一个新列表
    New_LiSt = []
    for i in range(number):
        element = LiSt[random.randint(0,len(LiSt)-1)]
        New_LiSt.append(element)
    return New_LiSt
    
def random_list(num:int,small:int,big:int):# 随机生成一个长度为num的数字列表,取值范围是small-big
    LiSt = []
    while True:
        # 防止有重复
        a = random.randint(small,big)
        if a in LiSt:
            pass
        else:
            LiSt.append(a)
        if len(LiSt) == num:
            break
    return LiSt

def str_today():#用“年_月_ 日”的字符串方式输出现在的时间
    nowtime = time.strftime("%Y_%m_%d")
    return nowtime

def ListElement_exist(LiSt:list,Element):#判断LiSt中是否有Element这个元素,有则返回True,没有则返回False
    # 统计次数,大于0则为True,等于0则为False
    result = LiSt.count(Element)
    return result

def ExtractNums(Str:str):# 提取字符串里面的数字,返回一个新数字
    NumberList = re.findall("\d+",Str)
    Str = "".join(NumberList)
    Int = int(Str)
    return Int



