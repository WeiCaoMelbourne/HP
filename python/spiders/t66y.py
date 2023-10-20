import requests
# from lxml import etree
from bs4 import BeautifulSoup
import re

url = "https://t66y.com/htm_data/1404/20/999224.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def txt(page_url=None):
    if not page_url:
        page_url = url

    DIV_CLEANR = re.compile('<div.*?/div>') 
    FONT_CLEANR = re.compile('<font.*?/font>') 

    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            # print(page_content)
            page = BeautifulSoup(page_content, "html.parser")
            divs = page.find_all("div", attrs={
                "class": "t t2"
            })

            i = 0
            for div in divs:
                tr = div.find("tr", attrs={
                    "class": "tr1 do_not_catch"
                    })
                
                if tr:
                    author_el = tr.find("b")
                    if not author_el:
                        continue
                    # print(author_el.text.strip().split()[0])
                    if i == 0:
                        # 作者
                        author = author_el.text.strip().split()[0]
                        content_el = div.find("div", attrs={
                            "class": "tpc_content do_not_catch"
                            })
                        # print("<br>" in content_el.extract())

                        # extract()可以保留<br>, text去掉所有tag
                        # print(content_el.extract())
                        # content_el.div.decompose()
                        # content_el.font.decompose()
                        for sub_div in content_el.find_all("div"):
                            sub_div.decompose()

                        for sub_div in content_el.find_all("font", attrs={"color":"gray"}):
                            sub_div.decompose()

                        content = content_el.text.strip()
                        
                        content = content.replace("　　", "\r\n")

                        with open("1.txt", mode="w", encoding="utf-8") as file:
                            # Write the string to the file
                            file.write("\r\n" + content)

                        # content = content_el.extract()
                        # print(content)
                        # cleantext = re.sub(DIV_CLEANR, '', str(content))
                        # cleantext = re.sub(FONT_CLEANR, '', str(cleantext))
                        # cleantext = cleantext.replace('<br/><br/>', "\r\n")
                        # cleantext = cleantext.replace('<br/>', "")
                        # # print(cleantext)
                        # with open("1.txt", mode="w", encoding="utf-8") as file:
                        #     # Write the string to the file
                        #     file.write(cleantext)
                    else:
                        # 只看作者
                        pass
                        # if author in author_el.text.strip().split()[0]:
                        #     content_el = div.find("div", attrs={
                        #         "class": "tpc_content do_not_catch"
                        #         })
                        #     print(content_el.text.strip())

                i += 1
                # content_el = div.find("div", attrs={
                #     "class": "c"
                #     })
                # if not content_el:
                #     continue
                
                # print(content_el.text)
            
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    txt()