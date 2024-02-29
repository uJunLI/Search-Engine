from elasticsearch import Elasticsearch
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# ...
def take_screenshot(url,docid):
    print("号码是",docid)
    if docid>250:
        save_path = f"screenshot/screenshot{docid}.png"
        # 设置浏览器窗口大小为 1920x1080（可根据需要调整）
        driver.set_window_size(1920, 1080)
        # 打开网页
        driver.get(url)
        # 等待直到页面加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))
        # 截取屏幕快照
        driver.save_screenshot(save_path)


# 示例
def getall_urls_ids():
    # 定义查询
    search_body = {
        "query": {
            "match_all": {}
        }
    }
    document_count = es.count(index=index_name)
    # 执行查询
    response = es.search(index=index_name, body=search_body,size= 475)
    top_documents = response["hits"]["hits"]
    urls = []
    ids = []
    for i, doc in enumerate(top_documents):
         urls.append(top_documents[i]['_source']['URL'])
         ids.append(top_documents[i]['_id'])
    return urls,ids


urls,ids = getall_urls_ids()
ids = [int(x) for x in ids]
print(len(urls))
for i in range(len(urls)):
    take_screenshot(urls[i],ids[i])










