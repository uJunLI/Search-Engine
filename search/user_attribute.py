import os
import json

def saveuser_Attribute(username,userattribute):
    filePath_user = 'users_attribute/' + username +'.json'
    # 清空文件内容，保留文件结构
    with open(filePath_user, "w", encoding="utf-8") as file:
        json.dump({'user_attribute': userattribute}, file, ensure_ascii=False)
    return True