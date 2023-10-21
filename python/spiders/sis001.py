import requests
from bs4 import BeautifulSoup
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def artical_download(url):
    # url = "https://sis001.com/forum/thread-9684603-1-5.html"
    domain = "https://sis001.com/forum/"
    title = None
    author = None

    def extract_save(div):
        # print("extract_save")
        content_el = div.find("div", attrs={
            "class": "t_msgfont noSelect"
            })

        # to remove all tags in this content
        for sub_div in content_el.find_all("i"):
            sub_div.decompose()

        content = content_el.text.strip()
        content = content.replace("\r\n", "")
        content = content.replace("[]", "")

        # 这个网站不按照作者，字数太少的不要
        if len(content) < 500:
            return
        
        with open(f"{title}.txt", mode="a", encoding="utf-8") as file:
            # Write the string to the file
            file.write("\r\n" + content)

        # with open(f"1.txt", mode="w", encoding="utf-8") as file:
        #     # Write the string to the file
        #     file.write("\r\n" + content)


    def page_download(page_url, first_page=False):
        print(page_url)
        nonlocal title, author
        try:
            response = requests.get(page_url, headers=headers)
            if response.status_code == 200:

                page_content = response.text
                response.close()

                # print(page_content)
                page = BeautifulSoup(page_content, "html.parser")
                
                if not title:
                    title_el = page.find("title").text
                    title = title_el.split('- 长')[0].strip()
                    try:
                        os.remove(f"{title}.txt")
                    except OSError:
                        pass

                divs = page.find_all("div", attrs={
                    "class": "mainbox viewthread"
                })

                post = 1
                for div in divs:
                    # 1楼
                    if first_page and post == 1:
                        thanks_el = div.find("a", attrs={
                            "class": "comment_digg"
                            })
                        thanks = thanks_el.text.strip()
                        print(f"thanks: ${thanks}")

                    # content_el = div.find("div", attrs={"class":"t_msgfont noSelect"})
                    extract_save(div)

                    post += 1
                    
                next_el = page.find("a", attrs={"class":"next"})
                if next_el:
                    href = next_el.get("href")
                    page_download(domain + href)
                
            else:
                print(f"Failed to retrieve data. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    page_download(url, first_page = True)
    
# 下载一批
def articals_download():
    articles = [
        'https://sis001.com/forum/thread-10193527-1-8.html',
        'https://sis001.com/forum/thread-10193524-1-5.html'
    ]
    for artical in articles:
        artical_download(artical)

def check_thanks(page_url, name):
    print(f"check_thanks START. url:{page_url}, name:{name}")
    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            # print(page_content)
            page = BeautifulSoup(page_content, "html.parser")
            divs = page.find_all("div", attrs={
                "class": "mainbox viewthread"
            })

            post = 1
            for div in divs:
                # 1楼
                thanks_el = div.find("a", attrs={
                    "class": "comment_digg"
                    })
                thanks = thanks_el.text.strip()
                return int(thanks)
        else:
                print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def check_page(url):
    print(f"check_page START. url:{url}")

    THRED_HOLD = 200
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            page = BeautifulSoup(page_content, "html.parser")

            articals = page.findAll(lambda tag:tag.name == "tbody" and "normalthread" in tag.attrs["id"])
            # articals = page.findAll("tbody", {"id":"normalthread"})
            for artical in articals:
                
                link_el = artical.find("span").find("a")
                artical_url = "https://sis001.com/forum/" + link_el.get("href")
                # print(link_el.text.strip(), link_el.get("href"), artical_url)
                thanks = check_thanks(artical_url, link_el.text.strip())
                if thanks < THRED_HOLD:
                    continue

                artical_download(artical_url)
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# 浏览所有，只下载点赞超过200的
def review_n_download():
    start_url = "https://sis001.com/forum/forum-334-1.html"
    forum_base = "https://sis001.com/forum/forum-334"
    
    try:
        response = requests.get(start_url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            page = BeautifulSoup(page_content, "html.parser")

            max_page = page.find("a", attrs={"class":"last"}).text.strip()
            max_page = int(max_page.split(" ")[1])
            
            pages = []
            for i in range(1, max_page + 1):
                pages.append(f"https://sis001.com/forum/forum-334-{i}.html")
                check_page(f"https://sis001.com/forum/forum-334-{i}.html")
                break   # TODO TEST
            
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # articals_download()
    review_n_download()