import logger
import requests
import re
import csv
from bs4 import BeautifulSoup
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

# 线程池：一次性开辟一些线程，用户直接给线程池提交任务
def thread_pool():
    from concurrent.futures import ThreadPoolExecutor
    def f(name):
        for i in range(1000):
            print(name, i)

    with ThreadPoolExecutor(5) as t:   # 线程池有5个线程
        for i in range(100):
            t.submit(f, name=f"线程{i}")

    # 在with外面的语句等待线程池中所有线程结束才执行(守护)
    print("全部线程结束")

def proxy_sample():
    url = "https://www.google.com"

    proxies = {
        "https": "https://212.34.4.5:3112"
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            page_content = response.text
            print(page_content)
            response.close()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# 防盗链
# 原始url: https://www.pearvideo.com/video_1721628
# 获取视频信息url: https://www.pearvideo.com/videoStatus.jsp?contId=1721628&mrd=0.8113572607835571 
# 从上面获取的视频地址： https://video.pearvideo.com/mp4/adshort/20210227/1697541236103-15618162_adpkg-ad_hd.mp4
# 真实视频地址：        https://video.pearvideo.com/mp4/adshort/20210227/cont-1721628-15618162_adpkg-ad_hd.mp4
# 将视频写入文件中
def pearvideo():
    url = "https://www.pearvideo.com/video_1721628"
    cont_id = url.split("_")[1]
    status_url = f"https://www.pearvideo.com/videoStatus.jsp?contId={cont_id}&mrd=0.8113572607835571"

    headers['Referer'] = 'https://www.pearvideo.com/video_1721628'  # 使用Referer反防盗链
    response = requests.get(status_url, headers=headers)
    status = response.json()
    response.close()
    # print(status)

    src_url = status['videoInfo']['videos']['srcUrl']
    sys_time = status['systemTime']
    video_url = src_url.replace(sys_time, f"cont-{cont_id}")
    response = requests.get(video_url, headers=headers)
    
    with open("pearvideo.mp4", mode="wb") as f:
        f.write(response.content)

    response.close()
    

# 1. 登录
# 2. 使用cookies取得后续数据
def session_sample():
    url = "https://www.oursteps.com.au/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
    session = requests.session()

    response = session.post(url, headers=headers, data={
        'fastloginfield': 'username',
        'username': 'DavidC',
        'password': 'Abcdef12',
        'quickforward': 'yes',
        'handlekey': 'ls'
    })

    print(response.cookies)
    response.close()

    # 此时session中是有cookies的, 等同于requests.get(url, headers={"Cookie":""})
    url = "https://www.oursteps.com.au/bbs/home.php?mod=space"
    response = session.get(url, headers=headers)
    print(response.text)
    response.close()

# xpath
# [] 从1开始
# 使用 @属性 拿到属性值
def xpath_sample():
    url = "https://www.zbj.com/fw/?k=saas"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_content = response.text
            response.close()
            
            # print(page_content)
            html = etree.HTML(page_content)

            divs = html.xpath('//*[@id="__layout"]/div/div[3]/div[1]/div[4]/div/div[2]/div[1]/div')
            
            for div in divs:
                price = div.xpath('./div/div[3]/div[1]/span/text()')[0].strip("¥")
                title = "Saas".join(div.xpath('./div/div[3]/div[2]/a/text()'))
                print(price, title)

        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# 使用 BeautifulSoup 解析HTML
# 下载图片
def bs4_sample():
    url = "https://movie.douban.com/top250"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_content = response.text
            response.close()
            
            # print(page_content)

            page = BeautifulSoup(page_content, "html.parser")

            # find(标签, 属性=值) /find_all(标签, 属性=值)
            # ol_item = page.find("ol", class_="grid_view")
            divs = page.find_all("div", attrs={
                "class": "item"
            })
            # print(ol_item)

            for div in divs:
                titles = div.find_all("span", attrs={
                    "class": "title"
                })
                href = div.find("div", attrs={"class": "hd"}).find("a")
                img = div.find("img")

                # .text 拿到被标签标记的内容, .get() 可以拿到属性的值
                print(titles[0].text, href.get("href"), img.get("src"))  

                img_response = requests.get(img.get("src"), headers=headers)
                img_name = img.get("src").split("/")[-1]
                with open(img_name, mode="wb") as f:
                    f.write(img_response.content)

                img_response.close()
                break   #TEST ONLY
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# 1. https 证书验证 
# 2. encoding 指定字符集
def verify_false():
    url = "https://dytt89.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        # response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            response.encoding = 'gb2312'    # <META http-equiv=Content-Type content="text/html; charset=gb2312">
            page_content = response.text

            response.close()
            
            # print(page_content)

            re_obj = re.compile(r'2023必看热片.*?<ul>(?P<ul>.*?)</ul>', re.S)
            re_obj2 = re.compile(r"<a href='(?P<href>.*?)'", re.S)
            re_obj3 = re.compile(r"◎片　　名(?P<title>.*?)<br", re.S)
            result = re_obj.finditer(page_content)
            # iter = result.__next__()
            # iter = next(result)
            # print(iter.group("ul"))

            child_url_list = []

            for iter in result:
                # print(iter.group("ul"))
                ul = iter.group("ul")
                results2 = re_obj2.finditer(ul)
                for iter2 in results2:
                    # print(iter2.group("href"))
                    href = iter2.group("href")
                    child_url = url + href.strip("/")
                    child_url_list.append(child_url)

            # child pages
            for herf in child_url_list:
                response = requests.get(herf, headers=headers)
                response.encoding = 'gb2312'    # <META http-equiv=Content-Type content="text/html; charset=gb2312">
                page_content = response.text
                # print(page_content)
                results2 = re_obj3.finditer(page_content)
                for iter2 in results2:
                    print(iter2.group("title").strip())
                    
                response.close()
                break   # TEST ONLY

        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# view-source:https://movie.douban.com/top250 
# 1. 拿到页面源代码
# 2. 通过re来提取有效信息
# 3. 保存到csv
def re_douban():
    url = "https://movie.douban.com/top250"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_content = response.text
            response.close()
            
            with open('douban250.csv', 'w', newline='', encoding='utf-8') as f:
                csvwriter = csv.writer(f)
                
                # re_obj = re.compile(r'<li>.*?<span class="title">(?P<title>.*?)</span>', re.S)
                re_obj = re.compile(r'<li>.*?<span class="title">(?P<title>.*?)</span>'
                                    r'.*?<p class="">.*?<br>(?P<year>.*?)&nbsp'
                                    r'.*?<span class="rating_num" property="v:average">(?P<score>.*?)</span>'
                                    r'.*?<span>(?P<number>.*?)人评价</span>', re.S)
                result = re_obj.finditer(page_content)
                for iter in result:
                    # print(iter.group("title"), iter.group("year").strip(), iter.group("score"), iter.group("number"))

                    d = iter.groupdict()
                    d['year'] = d['year'].strip()
                    csvwriter.writerow(d.values())
                    # print(d.values())

            logger.info("Done")

        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# \d+ 匹配数字串 .*? 匹配所有, (?P<group_name>re) 会讲匹配内容给变量v_name
def re_sample():
    s = """
    <div class='Jay'><span id='1'>路易斯·莫里斯</span></div>
    <div class='Julio'><span id='2'>朱里奥巴蒂费里</span></div>
    <div class='Don'><span id='3'>唐·司徒奥德</span></div>
    <div class='Chally'><span id='4'>查尔斯·布朗森</span></div>
    <div class='San'><span id='5'>安托万圣约翰</span></div>
    """

    # compile 将长正则预加载，方面后面使用
    re_obj = re.compile(r"<div class='.*?'><span id='(?P<id>\d+)'>(?P<actor>.*?)</span></div>", re.S) #re.S: 让.能匹配换行符
    result = re_obj.finditer(s)
    for iter in result:
        print(iter.group("id"))
        print(iter.group("actor"))

# use get + params
def get_params_sample():
    url = "https://movie.douban.com/j/chart/top_list"

    # User-Agent 处理一个简单的反爬
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    params = {
        'type': 27,
        'interval_id': '100:90',
        'action': None,
        'start': 0,
        'limit': 20
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        # logger.debug(f"url: {response.request.url}")
        # logger.debug(f"headers: {response.request.headers}")
        if response.status_code == 200:
            print(response.json())
            response.close()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# use post; use json()
def post_sample():
    url = "https://fanyi.baidu.com/sug"

    # User-Agent 处理一个简单的反爬
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    data = {
        "kw": "dog"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print(response.json())
            response.close()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def basic_sample():
    url = "https://www.coles.com.au/on-special?pid=homepage_cat_explorer_specials"

    # User-Agent 处理一个简单的反爬
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # print(response.text)
            with open("coles.html", mode="w", encoding="utf-8") as file:
                # Write the string to the file
                file.write(response.text.replace("\xa9", " "))

            response.close()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    logger.init()
    # basic_sample()
    # post_sample()
    # get_params_sample()
    # re_sample()
    # re_douban()
    # verify_false()
    # bs4_sample()
    # xpath_sample()
    # session_sample()
    # pearvideo()
    # proxy_sample()
    thread_pool()
    # logger.warn("Hello, world")

    # test2.f()