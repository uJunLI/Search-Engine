import json
import re
import numpy as np
import pandas as pd
import random
from elasticsearch import Elasticsearch
from insertElasticSearch import es
from insertElasticSearch import my_index
from insertElasticSearch import document_count


# 找到从i结点链接出去的网页，如果对面在数据库里则取对面的id，然后G[i][id] = 1 表示存在一条从i文档到id文档的边
def create_data(N):
    G = np.zeros((N,N))
    for i in range(N):
        # for j in range(N):
        #     if i==j:
        #         continue
        result = es.get(index=my_index, id=i)
        print(i)
        # 获取 "Links" 字段的值
        # 使用正则表达式去掉<span>和</span>中间的内容
        links = result['_source']['Links']
        # 使用json.loads()方法将JSON字符串解析为Python字典
        links = re.sub(r'<span.*?>.*?</span>', '', links)
        links = links.replace('"Anchor_Text": "', '"Anchor_Text": ')
        links = links.replace('"}', "}")

        links = links.replace('"', '')
        links = links.replace("'", '"')
        links = links.replace('"s', "'s")
        links = links.replace('"t', "'t")
        links = links.replace("\\'s", "'s")
        links = links.replace("\\'t", "'t")

        links = links.replace('"Anchor_Text": ', '"Anchor_Text": "')
        links = links.replace('}', '"}')
        links = links.replace('""', '"')
        links = links.replace('"}"}', '"}')
        links = links.replace('\\xa0', '')
        links = links.replace('"Link_URL": h', '"Link_URL": "h')
        links = links.replace('/, "', '/", "')
        # 使用正则表达式匹配 "Anchor_Text" 和 "}" 之间的内容
        pattern = re.compile(r'"Anchor_Text": "(.*?)"}')
        # 使用 findall 查找所有匹配
        matches = pattern.findall(links)
     # 如果有匹配，则去除匹配到的内容中的引号
        if matches:
            for match in matches:
                replaced_match = match.replace('"', "'")
                links = links.replace(match, replaced_match)

            #print(stringa)  # 打印修改后的字符串
        else:
            print("No matches found.")

        # 修正 Anchor_Text 中的引号问题
        # links['Anchor_Text'] = links['Anchor_Text'].replace('"', '\\"')
        es.update(index=my_index, id=i, body={'doc': {'Links': links}})
        try:
            links = json.loads(links)
        except json.JSONDecodeError as e:
            # 打印出错的位置和相关信息
            print("Error position:", e.pos)
            print("Error message:", e.msg)
            print("Error: ", e)
            # 找到出错位置附近的数据段
            error_position = e.pos
            error_context_length = 50  # 你可以根据需要调整数据段的长度
            error_snippet = links[max(0, error_position - error_context_length):error_position + 100]
            # 打印出错位置附近的数据段
            print("Error position:", error_position)
            print("Error context:", error_snippet)

        for link in links:
            link_URL = link['Link_URL']
            my_search = {
                "query": {
                    "match": {
                        "URL": link_URL
                    }
                }
            }
            # 执行查询
            result = es.search(index=my_index, body=my_search)
            # 检查结果
            if result['hits']['total']['value'] > 0:
                for hit in result['hits']['hits']:
                    coloum = (int)(hit['_id'])
                    G[i,coloum] = 1
    return G

filename = "matrixG.json"
# # 在下次运行时读取所有追加的数据
loaded_data = []
with open(filename, "r") as file:
    for line in file:
        loaded_data.append(json.loads(line.strip()))
G = loaded_data
# G = create_data(document_count['count'])
# G = G.tolist()
# # 将数据以追加模式写入文件
# with open(filename, "w") as file:
#     json.dump(G, file)
#     file.write("\n")  # 添加换行符，以便区分不同次追加的数据
# print(G)

def GtoM(G,N):
    M = np.zeros((N,N))
    for i in range(N):
        D_i = np.sum(G[i])
        if D_i == 0:
            continue
        for j in range(N):
            M[j][i] = G[i][j] / D_i
    return M
G = np.array(G)
G = G.reshape((473,473))
print(G.shape)
M = GtoM(G,document_count['count'])
filenameM = "matrixM.json"
M = M.tolist()
with open(filenameM, "w") as file:
    json.dump(M, file)
    file.write("\n")  # 添加换行符，以便区分不同次追加的数据


#
# Flow版本的PageRank
def PageRank(M,N,T=300,eps=1e-6):
    R = np.ones(N) / N
    for time in range(T):
        R_new = np.dot(M,R)
        if np.linalg.norm(R_new-R) < eps:
            break
        R = R_new.copy()
    return R_new / np.sum(R_new)

M = np.array(M)
M = M.reshape((473,473))
# 测试
valuesF = PageRank(M,document_count['count'],T=200)
filenameF = "matrixValueFlow.json"
valuesF = valuesF.tolist()
with open(filenameF, "w") as file:
    json.dump(valuesF, file)
    file.write("\n")  # 添加换行符，以便区分不同次追加的数据

##########################################
# Google Formula
def PageRank(M,N,T=300,eps=1e-6,beta=0.8):
    R = np.ones(N) / N
    teleport = np.ones(N) / N
    for time in range(T):
        R_new = beta * np.dot(M,R) + (1-beta) * teleport
        if np.linalg.norm(R_new - R) < eps:
            break
        R = R_new.copy()
    return R_new / np.sum(R_new)
M = np.array(M)
M = M.reshape((473,473))
# 测试
valuesG = PageRank(M,document_count['count'],T=200,beta=0.8)
filenameM = "matrixValueGoogle.json"
valuesG = valuesG.tolist()
with open(filenameM, "w") as file:
    json.dump(valuesG, file)
    file.write("\n")  # 添加换行符，以便区分不同次追加的数据










