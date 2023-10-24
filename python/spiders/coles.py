import requests
# from lxml import etree
from bs4 import BeautifulSoup
import asyncio
import re
import os
from datetime import datetime

domain = "https://www.coles.com.au"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
sub_folder = None

# In specials, when it is div and class is product__title_area, then it is a promoption
# For promoptions, it uses 2 requests:
#   1. https://www.coles.com.au/api/bff/products/categories?storeId=0584
#       store id is location-related
#       it returns all the products in json
#   2. https://www.coles.com.au/api/products
#       it is a post, with productIds and storeId 
#       TODO: where productIds come from
#       the productIds probabally directly from the url www.coles.com.au/promotions/mortein?pid=ctatile(specials)_rbhome_br360_5009899515
#       its source code has a "products":["3573557","4448029","3849115"...] 
def promotions(url):
    print(f"promotions START. storeId:{url}")

    # catetory_url = f"https://www.coles.com.au/api/bff/products/categories?storeId={storeId}"
    img_domain = "https://productimages.coles.com.au/productimages/6/6311080.jpg?w=200"
    products_url = "https://www.coles.com.au/api/products"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            re_obj = re.compile(r'"products":\[(?P<products>.*?)]', re.S)
            result = re_obj.finditer(page_content)
            for iter in result:
                products = iter.group("products").split(",")

            products = [item.replace('"', '') for item in products]
            data = {
                "productIds": ",".join(products),
                "filters": {},
                "storeId": "0584"   # TODO hardcoded now
            }

            response = requests.post(products_url, headers=headers, data=data)
            # print(response.status_code)
            if response.status_code == 200:
                # print(response.json())
                product_json = response.json()
                response.close()

                product_results = product_json['results']
                # print(product_results)
                for product in product_results:
                    # print(product)
                    try:
                        id = product['id']
                        price = product['pricing']['now']
                        was = product['pricing']['was']
                        
                        try:
                            discount = product['pricing']['savePercent']
                        except:
                            discount = (price / was) * 100

                        # print(id, price, was, discount)
                        if discount <= 50:
                            brand = product['brand']
                            name = product['name']
                            size = product['size']
                            desc = brand + " " + name + " | " + size
                            img = product['imageUris'][0]['uri']
                            img_url = f"https://productimages.coles.com.au/productimages{img}?w=200"
                            img_name = img_url.split("?")[0].split("/")[-1]

                            # print(desc, price, discount, was, img_name, img_url)
                            download_img(img_url, img_name)
                    except:
                        pass
            
            # print()
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# how many pages
def get_pages(page):
    divs = page.find("nav", attrs={
            "data-testid": "pagination"
        }).find_all("a", attrs={"class": "MuiButtonBase-root"})
    max_page = 0
    for div in divs:
        # page_el = div.find("a", attrs={"class": "MuiButtonBase-root"})
        # # print(page_el)
        page_num = int(div.text.strip())
        if page_num > max_page:
            max_page = page_num

    # return max_page
    return 1    # TODO TEST ONLY

def test(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        page_content = response.text
        response.close()

        with open("coles.html", "w", encoding='utf-8') as file:
            file.write(response.text)

# 
def prep():
    global sub_folder
    date_str = datetime.today().strftime('%Y-%m-%d')
    if not os.path.isdir(date_str):
        os.mkdir(date_str)
    sub_folder =  date_str

def download_img(url, name):
    file_path = os.path.join(sub_folder, name)
    if os.path.exists(file_path):
        return
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(f"{file_path}", "wb") as file:
                file.write(response.content) 
            response.close()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")    

def one_page(url):
    print(f"one_page START. url:{url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

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
                img_name = ""
                if img_el:
                    img_src = img_el.get("src")
                    img_name = img_src.split("?")[0].split("/")[-1]

                print(title, discount, price, was, img_name, img_src)
                download_img(img_src, img_name)

            print()
            divs = page.find_all("div", attrs={
                "data-testid": "unit"
            })

            for div in divs:
                prod_area = div.find("div", attrs={"class": "product__title_area"})
                if prod_area:
                    link_el = prod_area.find("a", attrs={"class": "product__link"})
                    if link_el:
                        link = link_el.get("href").strip()
                        # print(link)
                        promotions(domain + link)

            # response.encoding = 'utf-8'
            # print(response.text)

            # with open("coles.html", "w", encoding='utf-8') as file:
            #     file.write(response.text)
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
def specials(page_num=1):
    print(f"Page {page_num}")
    print()
    url = domain + f"/on-special?sortBy=priceAscending&page={page_num}"

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
            max_page = get_pages(page)
            # print(max_page)

            for i in range(1, max_page + 1):
                one_page(f"https://www.coles.com.au/on-special?page={i}")
            
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    prep()
    # test("https://www.coles.com.au/on-special")

    # asyncio.run(specials())
    # specials()

    promotions("https://www.coles.com.au/promotions/mortein?pid=ctatile(specials)_rbhome_br360_5009899515")