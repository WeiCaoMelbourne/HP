import requests
# from lxml import etree
from bs4 import BeautifulSoup

domain = "https://www.coles.com.au"

# In specials, when it is div and class is product__title_area, then it is a promoption
def promotions():
    pass

def specials(page_num=1):
    print(f"Page {page_num}")
    print()
    url = domain + f"/on-special?sortBy=priceAscending&page={page_num}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()
            
            # print(page_content)
            # html = etree.HTML(page_content)
            # divs = html.xpath('//*[@id="coles-targeting-browse-content-container"]/div[4]/div')
            # for div in divs:
            #     price = div.xpath('./section/div[1]/a/div[1]/span/span[1]/text()')
            #     print(price)

            page = BeautifulSoup(page_content, "html.parser")
            divs = page.find_all("section", attrs={
                "data-testid": "product-tile"
            })
            for div in divs:
                discount_el = div.find("span", attrs={"class": "is-half-price"})
                if not discount_el:
                    continue
                discount = discount_el.text.strip()
                # if price != '1/2':  # Only need 1/2
                #     continue

                # it is a half-price presentation, get product title
                title_el = div.find("h2", attrs={"class": "product__title"})
                if not title_el:
                    continue
                title = title_el.text.strip()

                price_el = div.find("span", attrs={"class": "price__value"})
                if not price_el:
                    continue
                price = price_el.text.strip()

                was_el = div.find("span", attrs={"class": "price__was"})
                if not was_el:
                    continue
                was = was_el.text.strip().split("$")[1].strip()

                img_el = div.find("img", attrs={
                    "data-testid": "product-image",
                    "loading":"lazy"
                    })
                img_src = ""
                if img_el:
                    img_src = img_el.get("src")

                print(title, discount, price, was, img_src)

            print()
            divs = page.find_all("div", attrs={
                "data-testid": "unit"
            })
            for div in divs:
                discount_el = div.find("span", attrs={"class": "is-half-price"})
                if not discount_el:
                    continue
                
                link_el = div.find("a", attrs={"class": "product__link"})
                if link_el:
                    link = link_el.get("href").strip()
                    print(link)
                    promotions()

            # response.encoding = 'utf-8'
            # print(response.text)

            # with open("coles.html", "w", encoding='utf-8') as file:
            #     file.write(response.text)

            # 下一页
            button_el = page.find("button", disabled=False, attrs={
                "id": "pagination-button-next"
            })

            if button_el:
                specials(page_num + 1)
            else:
                print()
                print("Done")
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    specials()