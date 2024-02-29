import base64

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
index_name = "108度"
def get_screenshot(url):
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"URL": {"query": url}}},
                ]
            }
        }
    }
    # 执行查询
    response = es.search(index=index_name, body=search_body, size=1, sort=["_score"])
    top_documents = response["hits"]["hits"]
    docid = 0
    if len(top_documents)>1:
        print("WRONG")
    if len(top_documents) == 1:
        docid = (int)(top_documents[0]['_id'])
    else:
        print("NO SUCH URL")
        return 0
    print("docid :",docid)
    file_path = f"screenshot/screenshot{docid}.png"
    img_stream = ''
    with open(file_path, 'rb') as img_f:
        img_binary = img_f.read()
        img_stream = base64.b64encode(img_binary).decode()
    return img_stream

