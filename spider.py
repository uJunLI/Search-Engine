import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
import random

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
}

user_agents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
# 完成随机选取 user-agnet，实现 反 反爬 操作
request_headers = {
    'user-agent': random.choice(user_agents),
    'Connection': "keep-alive",
    #'Referer': 'www.cgris.net/'
}

def crawl_webpages(seed_url, max_pages=10):
    visited_urls = set()
    queue = [(seed_url, 0)]  # URL, depth
    data = []
    number_crawl_all = 0
    while queue and len(visited_urls) < max_pages:
        current_url, depth = queue.pop(0)
        print("已爬数据量: ",number_crawl_all,"  已爬网站个数: ",len(visited_urls))
        if current_url not in visited_urls:
            visited_urls.add(current_url)
            try:
                response = requests.get(current_url,headers=request_headers)
                # 查看原网页编码方式charset为utf-8 而response是iso什么，因此要重新编码否则会出现乱码的情况
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Extract text content
                    # 提取 <p> 标签内的文本内容
                    # 提取网页标题、内容和锚文本
                    title = soup.title.text.strip() if soup.title else ''
                    if title=='':
                        print("empty title")
                    text_content = []
                    paragraphs = soup.select('p')
                    # 遍历每个 <p> 标签，获取文本内容
                    for paragraph in paragraphs:
                        if paragraph.get_text().strip() == '':
                            continue
                        text_content.append(paragraph.get_text().strip())  # strip=True 去除文本前后的空格和换行
                    if text_content == []:
                        print("empty text")
                    # Extract links
                    links = [{'Link_URL': urljoin(current_url, a['href']), 'Anchor_Text': a.get_text(strip=True)} for a in
                             soup.find_all('a', href=True) if a.get_text(strip=True) != '' and urljoin(current_url, a['href']).startswith('h')]
                    # Save data
                    data.append({'URL': current_url, 'title':title, 'Text Content': text_content, 'Links': links, 'Depth': depth})
                    if len(links)==0:
                        print("empty link")
                    # Add new links to the queue with increased depth
                    new_links = [(link['Link_URL'], depth + 1) for link in links]
                    queue.extend(new_links)
                    number_crawl_all = number_crawl_all + len(links) + len(text_content)
                    if number_crawl_all>100000:
                        print("超过最大爬虫十万条数据限制")
                        break
            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
    return data


def save_to_csv(data, filename='output.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


# Test the web crawler
seed_url_to_crawl = "https://www.nankai.edu.cn/"
max_pages_to_crawl = 500
crawl_data = crawl_webpages(seed_url_to_crawl, max_pages_to_crawl)

if len(crawl_data)>100:
    save_to_csv(crawl_data)

for i,data in enumerate(crawl_data):
    if len(data['Links'])>0:
        data['Links'][0]['Anchor_Text'] = data['Links'][0]['Anchor_Text'].replace('"', '')
        data['Links'][0]['Anchor_Text'] = data['Links'][0]['Anchor_Text'].replace("'", '')

# Save the data to CSV
if len(crawl_data)>100:
    save_to_csv(crawl_data)

