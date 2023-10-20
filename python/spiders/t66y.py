import requests
from bs4 import BeautifulSoup
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def main():
    url = "https://t66y.com/htm_data/1404/20/999224.html"
    domain = "https://t66y.com/"
    title = None
    author = None

    def extract_save(div):
        print("extract_save")
        content_el = div.find("div", attrs={
            "class": "tpc_content"
            })

        # to remove all tags in this content
        for sub_div in content_el.find_all("div"):
            sub_div.decompose()

        for sub_div in content_el.find_all("font", attrs={"color":"gray"}):
            sub_div.decompose()

        content = content_el.text.strip()
        content = content.replace("　　", "\r\n")

        with open(f"{title}.txt", mode="a", encoding="utf-8") as file:
            # Write the string to the file
            file.write("\r\n" + content)

    
    def page_download(page_url):
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
                    title = title_el.split('-')[0].strip()
                    try:
                        os.remove(f"{title}.txt")
                    except OSError:
                        pass
                    title = 1   # TODO 

                divs = page.find_all("div", attrs={
                    "class": "t t2"
                })
                for div in divs:
                    tr = div.find("tr", attrs={
                        "class": "tr1"
                        })
                    
                    if tr:
                        author_el = tr.find("b")
                        if not author_el:
                            continue
                        # print(author, author_el.text.strip().split()[0])
                        if not author:
                            # 作者
                            author = author_el.text.strip().split()[0]
                            extract_save(div)
                        else:
                            # 只看作者
                            if author in author_el.text.strip().split()[0]:
                                extract_save(div)

                next_el = page.find("a", string="下一頁")
                if next_el:
                    href = next_el.get("href")
                    grey = next_el.get("class")
                    # print(href, grey)
                    if grey == "gray":
                        return
                    a = href.rsplit("/", 1)
                    if len(a) > 1:
                        page_download(domain + a[1])
                    else:
                        page_download(domain + href)
                
            else:
                print(f"Failed to retrieve data. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    page_download(url)
    

if __name__ == "__main__":
    main()