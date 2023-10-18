import logger
import requests
import re
import csv
from bs4 import BeautifulSoup
from lxml import etree
import time
import asyncio
import os
import json

# 课程
# https://www.bilibili.com/video/BV1ZT4y1d7JM?p=82&spm_id_from=pageDriver&vd_source=e45321bd05d9abd3707ff2c5fe9fc6d8

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

# 不显示selenium窗口工作
def selenium_quiet():
    from selenium.webdriver import Chrome
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.select import Select
    from selenium.webdriver.chrome.options import Options

    opt = Options()
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    web = Chrome(options=opt)

    web.get("https://www.endata.com.cn/BoxOffice/BO/Year/index.html")
    sel_el = web.find_element(By.XPATH, '//*[@id="OptionDate"]')
    sel = Select(sel_el)

    # web.page_source == 浏览器中的elements 
    print(web.page_source)

    for i in range(len(sel.options)):
        sel.select_by_index(i)
        time.sleep(2)       # 因为每次换年份都有一个http请求，页面需要刷新
        table = web.find_element(By.XPATH, '//*[@id="TableList"]/table')
        print(table.text)

    web.close()

# https://www.endata.com.cn/BoxOffice/BO/Year/index.html 返回数据需要解密
# https://www.lagou.com/ 需要选择城市
def selenium():
    from selenium.webdriver import Chrome
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys

    web = Chrome()
    web.get("https://www.lagou.com/")

    el = web.find_element(By.XPATH, '//*[@id="changeCityBox"]/ul/li[1]/a')
    el.click()

    time.sleep(1) # 如果是需要动态加载的页面，sleep保证下次查找时页面已经准备好; 页面跳转的不用等待
    web.find_element(By.XPATH, '//*[@id="search_input"]').send_keys("python", Keys.ENTER)

    # divs = web.find_elements(By.XPATH, '//*[@id="jobList"]/div[1]/div')

    # for div in divs:
    #     title = div.find_element(By.ID, 'openWinPostion').text
    #     price = div.find_element(By.CLASS_NAME, 'money__3Lkgq').text
    #     print(title, price)

    # 点击打开新tab，因为默认打开新窗口后selenium停留在旧窗口
    web.find_element(By.XPATH, '//*[@id="openWinPostion"]').click()
    web.switch_to.window(web.window_handles[-1])

    job_details = web.find_element(By.XPATH, '//*[@id="job_detail"]/dd[2]/div').text
    print(job_details)

    web.close()
    web.switch_to.window(web.window_handles[0])

    # 如果要切换到iframe, 使用web.switch_to.frame；切换回来，web.switch_to.default_content()
    # iframe = web.find_element(By.XPATH, '//*[@id="player_iframe"]')
    # web.switch_to.frame(iframe)
    # web.switch_to.default_content()

    while True:
        pass
    # time.sleep(20)
    # web.quit()
    # print(web.title)


# <video src="xxx.mp4"></video>
# 一般视频网站的做法：用户上传 -> 转码 -> 切片，每片约10秒
# m3u文件记录播放顺序和视频存放的路径 m3u使用utf-8编码就是m3u8
#
# 抓取视频
#   1 找到m3u8
#   2 通过m3u8下载ts文件
#   3 将ts文件合并为mp4文件
#     关于合并，可以简单的使用 copy /b 1.ts+2.ts a.mp4
def m3u8_sample():
    url = "https://m3u.haiwaikan.com/xm3u8/d61179fb8ada50b199bebdf47a6230c4ed2c2901a1bf1038a40df49dc2f53a209921f11e97d0da21.m3u8"
    response = requests.get(url, headers=headers)
    # print(response.content)

    # m3u8 应该使用mode='w'存储，并且存储response.context
    with open("越狱/1.m3u8", mode="wb") as f:
        f.write(response.content)

    with open("越狱/1.m3u8", mode="r", encoding='utf-8') as f:
        for line in f:
            line = line.strip()     # 去掉空格，空行，换行符

            if line.startswith("#"):
                continue

            name = line.rsplit("/", 1)[1]
            ts_resp = requests.get(line, headers=headers)
            with open(f"越狱/{name}", mode="wb") as f:
                f.write(ts_resp.content)

    response.close()

# 使用协程下载整部小说
# 下载大约100个章节
def baidu_xiyouji():
    # 小说
    # https://dushu.baidu.com/api/pc/getCatalog?data={%22book_id%22:%224306063500%22}
    # 章节内容
    # https://dushu.baidu.com/api/pc/getChapterContent?data={%22book_id%22:%224306063500%22,%22cid%22:%224306063500|1569782244%22,%22need_bookinfo%22:1}

    # 1 同步操作，访问getCatalog得到所有章节的cid和名称
    # 2 异步操作，访问getChapterContent 下载所有文章的内容
    # 3 异步操作 IO 
    async def aiodownload(url, title):
        import aiohttp, aiofiles
        # s = aiohttp.ClientSesion() <==> requests
        # requests.get() <==> s.get()

        filepath = os.path.join("西游记", title)
        filepath += ".txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                logger.debug("here")
                data = await resp.json()  # 这里必须await resp.json()
                # print(data['data']['novel']['content'])
                async with aiofiles.open(filepath, mode="w", encoding="utf-8") as f:
                    await f.write(data['data']['novel']['content'])

    async def do_ur_job(items):
        tasks = []
        for item in items:
            # logger.log(item)
            cid = item['cid']
            title = item['title']

            params = {
                "book_id": bid,
                "cid": f"{bid}|{cid}",
                "need_bookinfo":0
            }
            str_params = json.dumps(params)
            chapter_url = f"https://dushu.baidu.com/api/pc/getChapterContent?data={str_params}"
            logger.debug("chapter_url:" + chapter_url)
            tasks.append(asyncio.create_task(aiodownload(chapter_url, title)))

        await asyncio.wait(tasks)

    bid = "4306063500"
    url = 'https://dushu.baidu.com/api/pc/getCatalog?data={"book_id":"' + bid + '"}'
    # print(url)
    response = requests.get(url, headers=headers)
    result = response.json()
    items = result['data']['novel']['items']

    asyncio.run(do_ur_job(items))

    response.close()

# 使用协程下载多个图片文件
def coroutine_download():
    urls = [
        "https://images.pexels.com/photos/40896/larch-conifer-cone-branch-tree-40896.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/776656/pexels-photo-776656.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/1612351/pexels-photo-1612351.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    ]

    async def aiodownload(url):
        import aiohttp
        # s = aiohttp.ClientSesion() <==> requests
        # requests.get() <==> s.get()

        name = url.rsplit("/", 1)[1]
        name = name.split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(name, mode="wb") as f:
                    f.write(await resp.content.read())  # 所有异步操作需要async

    async def do_ur_job():
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(aiodownload(url)))

        await asyncio.wait(tasks)

    asyncio.run(do_ur_job())

# General pattern of coroutine spider
def coroutine_spider():
    async def download(url):
        print(f"to download {url}")
        await asyncio.sleep(4)      # 模拟下载
        print(f"Downloading {url} finishes")

    async def do_ur_job():
        urls = [
            "https://1",
            "https://2",
            "https://3", 
            "https://4"
        ]

        tasks = []
        for url in urls:    
            tasks.append(asyncio.create_task(download(url)))    # after py3.8, need to use asyncio.create_task

        await asyncio.wait(tasks)

    asyncio.run(do_ur_job())

# 协程：当程序处于阻塞状态时，例如IO操作，可以选择性的切换到其他任务上
# 在微观上是一个任务一个任务的进行切换，切换条件一般是IO
# 在宏观上，我们看到的是多个任务一起执行
# 多任务异步操作，这一切都是在单线程的条件下
# 协程不是操作系统完成切换，是程序指明的
def coroutine_sample():
    async def f1():
        print("In f1")
        # time.sleep(1)   # 当函数中出现同步操作，异步就中断了
        await asyncio.sleep(1)
        print("In f1")

    async def f2():
        print("In f2")
        # time.sleep(2)
        await asyncio.sleep(2)
        print("In f2")

    async def f3():
        print("In f3")
        # time.sleep(3)
        await asyncio.sleep(3)
        print("In f3")

    # 执行多个任务
    # tasks = [f1(), f2(), f3()]
    # t1 = time.time()
    # asyncio.run(asyncio.wait(tasks))
    # t2 = time.time()
    # print(t2 - t1)

    # 第二种方法
    async def wrapper():
        tasks = [f1(), f2(), f3()]
        await asyncio.wait(tasks)

    t1 = time.time()
    asyncio.run(wrapper())
    t2 = time.time()
    print(t2 - t1)

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
    # logger.debug("main START")
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
    # thread_pool()
    # coroutine_sample()
    # coroutine_spider()
    # coroutine_download()
    # baidu_xiyouji()
    # m3u8_sample()
    # selenium()
    selenium_quiet()
    # logger.warn("Hello, world")

    # test2.f()