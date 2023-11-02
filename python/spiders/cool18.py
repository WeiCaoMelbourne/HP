import requests
from bs4 import BeautifulSoup
import os
from lxml import etree
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

domain = "https://www.cool18.com/bbs4/"

def artical_download(url):
    print(f"artical_download START. url:{url}")
    # url = "https://sis001.com/forum/thread-9684603-1-5.html"
    # domain = "https://sis001.com/forum/"
    title = None
    author = None

    def artical_page_download(page_url, title, section_title):
        print(f"artical_page_download START. page_url:{page_url}, {title}, {section_title}")
        try:
            response = requests.get(page_url, headers=headers)
            if response.status_code == 200:

                page_content = response.text
                response.close()

                # print(page_content)
                page = BeautifulSoup(page_content, "html.parser")
                content = page.find("td", attrs={"class": "show_content"}).find("pre").text.strip()
                content = content.replace("www.6park.com", "\r\n")
                content = content.replace("cool18.com", "\r\n")
                # print(content)
                print(f"{title}.txt")
                with open(f"temp.txt", mode="a", encoding="utf-8") as file:
                    file.write("\r\n" + content)
                
            else:
                print(f"Failed to retrieve data. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    # 首页，获取基本信息，作者，后续章节url
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            # print(page_content)
            page = BeautifulSoup(page_content, "html.parser")
            
            if not author:
                author_el = page.find("td", attrs={"height": "23px"}).text
                author_el = author_el.strip().strip("送交者:").strip()
                author = author_el.split("[")[0].strip()
                print(author)

            if not title:
                title = page.find("font", attrs={"size": "6"}).find("b").text
                title = title.replace("【", "")
                title = title.replace("】", "")
                title = title.replace(":", "")
                print(title)

            articals = {}
            content = page.find("td", attrs={"class": "show_content"}).find("pre").text.strip()
            if len(content) > 10000:
                # 当前页面就是文章内容页面
                tid = url.rsplit("=", 1)[1]
                articals[tid] = {
                    "link": url,
                    "sec_title": ""
                }

                # 得到所有链接
                divs = page.find("td", attrs={"class": "show_content"}).find("pre").find_all("a")
                for div in divs:
                    a = div.get("href").strip()
                    tid = a.rsplit("=", 1)[1]
                    sec_title = div.text.strip()
                    # print(a, tid)
                    articals[tid] = {
                        "link": a,
                        "sec_title": sec_title
                    }
            else:
                divs = page.find_all("li")
                for div in divs:
                    # print(div.text)

                    # re_obj = re.compile(r"<div class='.*?'><span id='(?P<id>\d+)'>(?P<actor>.*?)</span></div>", re.S) #re.S: 让.能匹配换行符
                    # 同一作者，字数大于10000
                    # re_obj = re.compile(rf"- {author}.*?((?P<size>\d+) bytes)", re.S) #re.S: 让.能匹配换行符
                    re_obj = re.compile(r"((?P<size>\d+) bytes)", re.S) #re.S: 让.能匹配换行符
                    result = re_obj.finditer(div.text)

                    valid_artical = False
                    for iter in result:
                        size = iter.group("size")
                        if int(size) > 10000:
                            valid_artical = True
                            break

                    if valid_artical:
                        a = div.find("a").get("href").strip()
                        tid = a.rsplit("=", 1)[1]
                        sec_title = div.find("a").text.strip()
                        # print(a, tid)
                        articals[tid] = {
                            "link": domain + a,
                            "sec_title": sec_title
                        }
                    
            print(dict(sorted(articals.items())))
            # for key, value in dict(sorted(articals.items())).items():
            #     artical_page_download(value['link'], title=title, section_title=value['sec_title'])
                
            # 全部完成后重新整理txt文件，删除多余的空行
            # with open("temp.txt", 'r', encoding="utf-8") as input_file, open(f"{title}.txt", 'w', encoding="utf-8") as output_file:
            #     empty_line = 0
            #     for line in input_file:
            #         # print(line)
            #         line = line.rstrip()
            #         if len(line) == 0:
            #             if empty_line == 1:
            #                 output_file.write("\r\n")

            #             empty_line += 1
            #         else:
            #             if empty_line == 1:
            #                 output_file.write("\r\n")
            #             empty_line = 0

            #         output_file.write(line)
            
            # os.remove("temp.txt")
                
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    



if __name__ == "__main__":
    # articals = [
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13925752',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13869897',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13863838',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=78294',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=42132',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=82478',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=51914',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=40782',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13873242',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=18630',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13870519',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=70905',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=66150',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13869807',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13869309',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13869864',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13866629',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=68327',
    #     'https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13962841'
    # ]
    # for artical in articals:
    #     artical_download(artical)
    artical_download("https://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=13962841")


    # print(check_thanks("https://sis001.com/forum/thread-11320608-1-1.html", 1))
        # with open("temp.txt", 'r', encoding="utf-8") as input_file, open(f"1.txt", 'w', encoding="utf-8") as output_file:
        #     empty_line = 0
        #     for line in input_file:
        #         print(line)
        #         line = line.rstrip()
        #         if len(line) == 0:
        #             if empty_line == 1:
        #                 output_file.write("\r\n")

        #             empty_line += 1
        #         else:
        #             if empty_line == 1:
        #                 output_file.write("\r\n")
        #             empty_line = 0

        #         output_file.write(line)