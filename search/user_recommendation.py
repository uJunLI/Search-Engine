import os
# from random import random
import random


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

def get_results(top_documents):
    scores = []
    number = len(top_documents)
    result = [{'url': top_documents[i]['_source']['URL'],
               'title': top_documents[i]['_source']['title']} for i in range(number)]
    return result

def get_recommendations(username):
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
    loaded_data = docids_relative
    loaded_data = list(loaded_data)
    print("采样数据: " ,loaded_data)

    filenameG = "user_search_doc_ids/global_search_doc_ids.json"
    # 判断文件是否存在，如果不存在则创建一个新文件
    if not os.path.exists(filenameG):
        with open(filenameG, "w", encoding="utf-8"):
            pass  # 创建一个空文件
    # 读取文件中的数据，构建字典
    global_docids_relative = {}
    if os.path.exists(filenameG):
        with open(filenameG, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                data_dict = json.loads(line.strip())
                docid_number_pairs = {int(doc_id): number for doc_id, number in data_dict.items()}
                global_docids_relative.update(docid_number_pairs)
    # 从 global_docids_relative 中选择 number 最大的三个 doc_id
    selected_doc_ids = sorted(global_docids_relative, key=global_docids_relative.get, reverse=True)[:3]

    # 冷启动 推荐PageRank权重最高的
    if len(loaded_data) == 0:
        # 导入PageRank权重
        filename = "matrixValueGoogle.json"
        # # 在下次运行时读取所有追加的数据
        page_rank = []
        with open(filename, "r") as file:
            for line in file:
                page_rank.append(json.loads(line.strip()))
        page_rank = np.array(page_rank)
        page_rank = page_rank.reshape(473)
        # 使用argsort获取从大到小的索引数组
        sorted_indices = np.argsort(page_rank)[::-1]
        # 选择前20个索引
        top_20_indices = list(sorted_indices[:20])
        loaded_data = random.sample(top_20_indices,8)
    elif len(loaded_data) > 6:
        loaded_data = random.sample(loaded_data, 6)

    for ids in selected_doc_ids:
        loaded_data.append(ids)
    # 根据历史记录进行查询 然后将随机抽到的最多八条数据进行一个排序
    search_body = {
        "query": {
            "terms": {"_id": loaded_data}  # 使用terms查询匹配文档id
        }
    }
    # 执行查询
    response = es.search(index=index_name, body=search_body, size=len(loaded_data), sort=["_score"])
    # 获取匹配的文档
    top_documents = response["hits"]["hits"]
    result = get_results(top_documents)
    return result