import pandas as pd
from elasticsearch import Elasticsearch

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

# from elasticsearch_dsl import Document, Text, Keyword
def createIndex(my_index):
    # index settings
    settings = \
        {
            "mappings": {
                "_doc": {
                    "properties": {
                        "URL": {"type": "keyword"},
                        "title": {"type": "text"},
                        "Text_Content" : {"type": "text"},
                        "Links": {
                              "type": "nested",
                              "properties": {
                                "Link_URL": {"type": "keyword"},
                                "Anchor_Text": {"type": "text"}
                         }
                        }
                    }
                }
            }
        }
    # create index
    es.indices.create(index=my_index, ignore=400, body=settings)
    print("创建index成功！")

def read_from_csv_and_save_to_elasticsearch(csv_filename, index_name='108度', doc_type='_doc', es_host='localhost', es_port=9200):
    # Read data from CSV file
    df = pd.read_csv(csv_filename)
    print(df.shape[0])
    # 替换所有 NaN 值为一个默认值，例如空字符串
    df.fillna("", inplace=True)
    # 删除名为 "title" 的列
    df = df.drop("Depth", axis=1)
    df.rename(columns={'Text Content': 'Text_Content'}, inplace=True)
    column_names = df.columns.tolist()
    print(column_names)
    i = 0
    for _, row in df.iterrows():
        print(i)
        document = row.to_dict()
        # Index the document in Elasticsearch
        es.index(index=index_name,id=i, body=document)
        i = i + 1

    print(f"Data indexed to Elasticsearch in index: {index_name}")

my_index = "108度"
# 创建新的索引 已经创建成功了 不用再创建
# createIndex(my_index)
# Example usage
csv_filename = 'output.csv'
# read_from_csv_and_save_to_elasticsearch(csv_filename, index_name=my_index)
document_count = es.count(index=my_index)
print(document_count)
# 发送 DELETE 请求来删除整个索引
# 使用 Elasticsearch.options() 设置参数
# 删除全部索引
# 使用 indices.delete 方法删除所有索引
# es.indices.delete(index=my_index, ignore=[400, 404])
# 发送 count 请求来获取索引中的文档数量



