# 获取最近前二十条query 加载num条
import json
def history(username):
    filenameH = "users_histories/" + username + "_history.json"
    loaded_data = []

    with open(filenameH, "r", encoding="utf-8") as file:
        for line in file:
            loaded_data.append(json.loads(line.strip()))
    if len(loaded_data) > 20:
        loaded_data = loaded_data[0:20]
    with open(filenameH, "w", encoding="utf-8") as file:
        for item in loaded_data:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')
    num = 8
    if len(loaded_data) < num:
        num = len(loaded_data)
    return loaded_data[0:num]