import os

import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
import json
import math

es = Elasticsearch(
    [
        {
            'host':"localhost",
            'port':9200,
            'scheme': "http"
        }
    ],
    basic_auth=("elastic", "Liyujun88")
)
index_name = "108度"

# PageRank权重
alpha = 0.5

# 导入PageRank权重
filename = "matrixValueGoogle.json"
# # 在下次运行时读取所有追加的数据
page_rank = []
with open(filename, "r") as file:
    for line in file:
        page_rank.append(json.loads(line.strip()))
page_rank = np.array(page_rank)
page_rank = page_rank.reshape(473)
page_rank = page_rank*1000

def insert_into_history(query, username):
    filenameH = "users_histories/" + username + "_history.json"
    # 判断文件是否存在，如果不存在则创建一个新文件
    if not os.path.exists(filenameH):
        with open(filenameH, "w", encoding="utf-8"):
            pass  # 创建一个空文件
    lines = []
    # 打开文件并读取内容
    with open(filenameH, "r", encoding="utf-8") as file:
        lines = file.readlines()
    # 在列表的开头插入新数据
    lines.insert(0, json.dumps(query) + '\n')
    # 将更新后的内容写回文件
    with open(filenameH, "w", encoding="utf-8") as file:
        file.writelines(lines)

def insert_into_docids(docids,username):
    filenameS = "user_search_doc_ids/" + username + ".json"
    lines = []
    with open(filenameS, "r",encoding="utf-8") as file:
        lines = file.readlines()

    # 在列表的开头插入新数据
    lines.insert(0, json.dumps(docids) + '\n')

    if len(lines)>10:
        lines = lines[0:10]
    # 将更新后的内容写回文件
    with open(filenameS, "w",encoding="utf-8") as file:
        file.writelines(lines)

    filenameG = "user_search_doc_ids/global_search_doc_ids.json"
    lines = []
    # 读取文件内容
    with open(filenameG, "r", encoding="utf-8") as file:
        lines = file.readlines()
    # 解析原有数据
    if lines:
        existing_data = json.loads(lines[0])
    else:
        existing_data = {}
    # 更新数据
    for doc_id in docids:
        existing_data[doc_id] = existing_data.get(doc_id, 0) + 1
    # 将更新后的内容写回文件
    with open(filenameG, "w", encoding="utf-8") as file:
        file.write(json.dumps(existing_data))

# 根据用户搜索历史记录进行加权
def get_relative_docids_set(username):
    filenameS = "user_search_doc_ids/" + username + ".json"
    # 判断文件是否存在，如果不存在则创建一个新文件
    if not os.path.exists(filenameS):
        with open(filenameS, "w", encoding="utf-8"):
            pass  # 创建一个空文件
    lines = []
    with open(filenameS, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line.strip()))
    docids_relative = set()
    for line in lines:
        for id in line:
            docids_relative.add(id)

    filenameG = "user_search_doc_ids/global_search_doc_ids.json"
    # 判断文件是否存在，如果不存在则创建一个新文件
    if not os.path.exists(filenameG):
        with open(filenameG, "w", encoding="utf-8"):
            pass  # 创建一个空文件
    # 读取文件中的数据，构建字典
    global_docids_relative = {}
    if os.path.exists(filenameG):
        with open(filenameG, "r", encoding="utf-8") as file:
            # 实际上只有一行
            lines = file.readlines()
            for line in lines:
                data_dict = json.loads(line.strip())
                docid_number_pairs = {int(doc_id): number for doc_id, number in data_dict.items()}
                global_docids_relative.update(docid_number_pairs)

    return docids_relative,global_docids_relative
# 根据用户属性进行加权
def get_user_attribute_docids_set(username):
    file_path_user = 'users_attribute/' + username + '.json'
    # 判断文件是否存在，如果不存在则返回空字典
    attribute = {}
    if not os.path.exists(file_path_user):
        return {}
    # 读取文件中的用户属性数据
    try:
        with open(file_path_user, "r", encoding="utf-8") as file:
            file_content = file.read()
            if not file_content.strip():
                # 文件为空，返回默认值
                return {}
            data = json.loads(file_content)
            attribute = data.get('user_attribute', {})
    except json.decoder.JSONDecodeError as e:
        # JSON 解码失败的处理
        print(f"JSON Decode Error: {e}")
        return {"error": "Invalid JSON format"}

    lines = []
    filename = "users_attribute/" + attribute + ".json"
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line.strip()))
    attribute_relative = set()
    for line in lines:
        for id in line:
            attribute_relative.add(id)
    return attribute_relative

def get_result(top_documents,username):
    # 存取包括了PageRank和TF-IDF综合的比分
    scores = []
    docids_relative,global_docids_relative = get_relative_docids_set(username)
    attribute_relative = get_user_attribute_docids_set(username)
    # 个性化查询 之前改用户查询的相关文档会有1.5倍分数加成
    docids_relative = list(docids_relative)
    docids_relative = [int(x) for x in docids_relative]

    attribute_relative = list(attribute_relative)
    attribute_relative = [int(x) for x in attribute_relative]
    for i, doc in enumerate(top_documents):
        scoreTF_IDF = doc['_score']
        id = (int)(doc['_id'])
        scorePage_Rank = page_rank[id]
        score = alpha * scorePage_Rank + (1 - alpha) * scoreTF_IDF
        # 属性的加权不应该有最多最近排名前10的历史记录的加权大 这也是可以理解的 毕竟属性有的时候只能模糊的反应，历史记录更能直接反应用户偏好
        if id in attribute_relative:
           if id in docids_relative:
               if global_docids_relative.get(id)!= None and global_docids_relative[id]>3:
                    scores.append(3*score)
               else:
                    scores.append(3.5 * score)
           else:
               if global_docids_relative.get(id)!= None and global_docids_relative[id]>3:
                    scores.append(1.2*score)
               else:
                    scores.append(1.5 * score)
        elif id in docids_relative:
            if global_docids_relative.get(id)!= None and global_docids_relative[id]>3:
                scores.append(2 * score)
            else:
                scores.append(2.5 * score)
        else:
            if global_docids_relative.get(id)!= None and global_docids_relative[id]>3:
                scores.append(0.9 * score)
            else:
                scores.append(1 * score)
    # 获取从高到低的索引
    sorted_indices = np.argsort(scores)[::-1]
    # print(scores)
    # 返回综合排名前十的文档
    number = 10
    if len(sorted_indices) < 10:
        number = len(sorted_indices)
    docids = []
    for i in range(number):
        print(f"Rank {i + 1}: Document ID {top_documents[sorted_indices[i]]['_id']} with score {scores[sorted_indices[i]]}")
        print(f"网址是: {top_documents[sorted_indices[i]]['_source']['URL']}")
        docids.append(top_documents[sorted_indices[i]]['_id'])
    insert_into_docids(docids,username)
    result = [{'url':top_documents[sorted_indices[i]]['_source']['URL'],'title':top_documents[sorted_indices[i]]['_source']['title']} for i in range(number)]
    return result

def site_search(site_url,query,username):
    # 假设你已经创建了 Elasticsearch 客户端 es，index 是你的索引名称
    # 构建查询DSL
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                                "query": query,
                                "fields": ["title^2.0", "Text_Content^1.0"]  # 设置字段和权重
                        }
                    }
                ],
                "filter": [
                    {"wildcard": {"URL": f"*{site_url}*"}}
                ]
            }
        }
    }
    # 执行查询
    response = es.search(index=index_name, body=search_body, size=50, sort=["_score"])
    # 获取TF-IDF排名前二十的文档
    top_documents = response["hits"]["hits"]
    print("命中总个数: ",len(top_documents))
    result = get_result(top_documents,username)
    return result

def Phrase_Query(query,username):
    # 构建短语查询的 DSL
    # 增加查询可扩展性
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"title": {"query": query, "boost": 2.0}}},
                    {"match_phrase": {"Text_Content": {"query": query, "boost": 1.0}}}
                ]
            }
        }
    }
    if len(query) < 10 and len(query) >= 3:
        query_add = query[0:2]
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"title": {"query": query, "boost": 5.0}}},
                        {"match_phrase": {"Text_Content": {"query": query, "boost": 4.0}}},
                        {"match_phrase": {"title": {"query": query_add, "boost": 1.0}}},
                        {"match_phrase": {"Text_Content": {"query": query_add, "boost": 1.0}}}
                    ]
                }
            }
        }

    # 执行查询
    response = es.search(index=index_name, body=search_body, size=20, sort=["_score"])
    # 获取TF-IDF排名前二十的文档
    top_documents = response["hits"]["hits"]
    result = get_result(top_documents,username)
    return result

# query = "计算机"
# Phrase_Query(query)

def wildcard_query(query,username):
    # 构建 dis_max 查询的 DSL，同时设置字段和权重
    search_body = {
        "query": {
            "dis_max": {
                "queries": [
                    {"wildcard": {"title": {"value":query}}},
                    {"wildcard": {"Text_Content": {"value":query}}},
                    {"wildcard": {"title.keyword": query}},
                    {"wildcard": {"Text_Content.keyword": query}}
                ],
                "tie_breaker": 0.7  # 调整权重
            }
        }
    }
    # 执行查询
    response = es.search(index=index_name, body=search_body, size=20, sort=["_score"])
    # 获取TF-IDF排名前二十的文档
    top_documents = response["hits"]["hits"]
    result = get_result(top_documents,username)
    return result

# query = "南开*"
# wildcard_query(query)

def search(query,username):
    result = 0
    insert_into_history(query,username)
    # 站内查询
    if query.startswith("site:"):
        query = query.replace("site:","")
        parts= query.split(' ')
        site_url = parts[0] if len(parts)>0 else ''
        query = parts[1] if len(parts)>1 else ''
        result = site_search(site_url,query,username)
    # 短语查询（精确查询）
    elif query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
        result = Phrase_Query(query,username)
    elif '*' in query or '?' in query:
        result = wildcard_query(query,username)
    # 对于 长城 这种搜索也用短语查询  正常要写成 "长城"
    else:
        result = Phrase_Query(query,username)
    return result


# 获得属性相关数据
# query = "留学生"
# search_body = {
#     "query": {
#         "bool": {
#             "should": [
#                 {"match_phrase": {"title": {"query": query, "boost": 2.0}}},
#                 {"match_phrase": {"Text_Content": {"query": query, "boost": 1.0}}}
#             ]
#         }
#     }
# }
# if len(query) < 10 and len(query) >= 3:
#     query_add = query[0:2]
#     search_body = {
#         "query": {
#             "bool": {
#                 "should": [
#                     {"match_phrase": {"title": {"query": query, "boost": 5.0}}},
#                     {"match_phrase": {"Text_Content": {"query": query, "boost": 4.0}}},
#                     {"match_phrase": {"title": {"query": query_add, "boost": 1.0}}},
#                     {"match_phrase": {"Text_Content": {"query": query_add, "boost": 1.0}}}
#                 ]
#             }
#         }
#     }
#
# # 执行查询
# response = es.search(index=index_name, body=search_body, size=30, sort=["_score"])
# # 获取TF-IDF排名前二十的文档
# top_documents = response["hits"]["hits"]
# scores = []
# for i, doc in enumerate(top_documents):
#     scoreTF_IDF = doc['_score']
#     id = (int)(doc['_id'])
#     scorePage_Rank = page_rank[id]
#     scores.append(alpha * scorePage_Rank + (1 - alpha) * scoreTF_IDF)
# # 获取从高到低的索引
# sorted_indices = np.argsort(scores)[::-1]
# number = 20
# if len(sorted_indices) < 20:
#     number = len(sorted_indices)
# docids = []
# for i in range(number):
#     print(f"Rank {i + 1}: Document ID {top_documents[sorted_indices[i]]['_id']} with score {scores[sorted_indices[i]]}")
#     print(f"网址是: {top_documents[sorted_indices[i]]['_source']['URL']}")
#     docids.append(top_documents[sorted_indices[i]]['_id'])
#
# filename = "users_attribute/" + query + ".json"
# # 将整数列表转换为字符串列表
# docids = list(map(str, docids))
# # 将更新后的内容写回文件
# with open(filename, "w", encoding="utf-8") as file:
#     json.dump(docids, file)
