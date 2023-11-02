import requests
# from lxml import etree
from bs4 import BeautifulSoup
import asyncio
import re
import os
from datetime import datetime
import csv
import json
import common
                
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
domain = "https://salefinder.com.au"

# date_str = None

# Read all post code from postcodes.txt, and get corresponding post code id of salefinder
def get_all_postcodeid():
    postcode_ids = {}

    i = 1
    with open("postcodes.txt", 'r') as input_file, open("postcode_ids.txt", "w", encoding='utf-8') as output_file:
        for line in input_file:
            postcode = line.strip()
            print(postcode)
            url = f"https://salefinder.com.au/ajax/locationsearch?query={postcode}"
    
            response = requests.get(url, headers=headers)

            # Sample: ({"Id":"5583","postcode":"3178","displayName":"ROWVILLE","suggestions":[{"data":"5583","value":"ROWVILLE, 3178"}]})
            page_content = response.text
            response.close()

            try:
                postcode_json = json.loads(page_content.strip(")").strip("("))
                postcodeid = postcode_json['Id']
                postcode_ids[postcode] = postcodeid
                output_file.write(postcodeid + '\n')
            except:
                pass

            i += 1

            # if i > 30:
            #     break

    print(postcode_ids)

# csv format
# cmpy, prod_id, name, brand, size, desc, aisle, catetory, sub-category, price, was, desc, img_url

def one_catalogue(url, csvwriter, retailer):
    print(f"one_catalogue START. url:{url}")
    one_page(url, csvwriter, retailer)
    
def one_page(url, csvwriter, retailer):
    print(f"one_page START. url:{url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            page_content = response.text
            response.close()

            page = BeautifulSoup(page_content, "html.parser")
            
            divs = page.find_all("div", attrs={
                "class": "item-landscape"
            })

            for div in divs:
                item_el = div.find("a", attrs={"class": "item-name"})
                name = item_el.text.strip()
                link = item_el.get("href").strip()
                price_desc = div.find("div", attrs={"class": "price-options"}).text.strip()
                img = div.find("a", attrs={"class": "item-image"}).find("img").get("src")
                # print(name, price, link)

                if "1/2 Price" not in price_desc:
                    continue

                price = div.find("span", attrs={"class": "price"}).text.strip()

                prod_data = link.strip("/").split("/")
                # print(prod_data)
                aisle = prod_data[1]
                catetory = prod_data[2]

                sub_category = ''
                if len(prod_data) > 5:
                    sub_category = prod_data[3]

                prod_id = prod_data[-1]
                full_desc = prod_data[-2]
                temp = full_desc.split("-")
                brand = temp[0]
                size = ''
                if 'ml' in temp[-1]:
                    size = temp[-1]

                line = common.product_list(cmpy=retailer['name'], prod_id=prod_id, name=name,
                    brand=brand, size=size, desc=full_desc, aisle=aisle, catetory=catetory,
                    sub_category=sub_category, price=price, was='', discount='1/2', img_url=img)
                # print(line)
                csvwriter.writerow(line)

            # if there is a "Next " page, do it
            divs = page.find_all("a", attrs={
                "class": "pagenumsblack"
            })
            for div in divs:
                pages = div.text.strip()
                if "Next" in pages:
                    page_url = div.get("href").strip()
                    one_page(domain + page_url, csvwriter=csvwriter, retailer=retailer)

            # print(page_content)
            # with open("ww.html", "w", encoding='utf-8') as file:
            #     file.write(page_content)
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Logic:
# 1. https://catalogues.woolworths.com.au/etc.clientlibs/wx-digital-catalogue/clientlibs/clientlib-site.lc-4a2da037d5291fed43cd25414d81864e-lc.min.js
# find apikey in it. there are 3 places, each of them can do. 
# 2. use https://webservice.salefinder.com.au/index.php/api/regions/search/?apikey=w00lw0rth5A48E69B9C93E236B&format=json&location=3178
# to get storeid
# 3. use https://webservice.salefinder.com.au/index.php/api/sales/retailer/?id=126&apikey=w00lw0rth5A48E69B9C93E236B&format=json&storeId=&storeId=5407
# to get catalogues, each catalogue has a saleId, like 52476
# 4. https://www.woolworths.com.au/shop/catalogue/view#view=list&saleId=52476&areaName=VIC 
# this is catalogue product list
# 5. https://embed.salefinder.com.au/catalogue/svgData/52476/?format=json&pagetype=catalogue2&retailerId=126&saleGroup=0&locationId=5420&token=570f5c4a44505b5f51477f531a03180a0e0b1c1362352b2e21363226253968717d7b77776363616163612b&size=518&preview=&callback=jQuery17206243237484621449_1698326873512&_=1698326873532
# looks it is pretty hard to get products this way

# option 2
# 1. https://salefinder.com.au/ajax/locationsearch?query=3178 to get postcodeid
# 2. https://salefinder.com.au/Woolworths-catalogue     Cookie: postcodeId=5583
#   it can get webpage of catalogus, 
# 3. https://salefinder.com.au/woolworths-catalogue/weekly-specials-catalogue-vic/52476/list 
#   it contains a procusts. 52476 comes from 2 
def specials(csvwriter, retailer):
    print(f"specials START")
    print()
    url = "https://salefinder.com.au/ajax/locationsearch?query=3178"
    
    try:
        # 1
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            # Sample: ({"Id":"5583","postcode":"3178","displayName":"ROWVILLE","suggestions":[{"data":"5583","value":"ROWVILLE, 3178"}]})
            page_content = response.text
            response.close()

            postcode_json = json.loads(page_content.strip(")").strip("("))
            postcodeid = postcode_json['Id']
            # print(postcodeid)

            # 2
            url = f"https://salefinder.com.au/{retailer['catalogue']}"
            cookie_header = headers.copy()
            cookie_header['Cookie'] = f"postcodeId={postcodeid}"
            
            response = requests.get(url, headers=cookie_header)
            page_content = response.text
            response.close()

            # print(page_content)
            # with open("ww.html", "w", encoding='utf-8') as file:
            #     file.write(page_content)

            page = BeautifulSoup(page_content, "html.parser")
            
            divs = page.find_all("div", attrs={
                "class": "retailer-catalogue"
            })

            for div in divs:
                name = div.find("div", attrs={"class": "catalogue-name"}).text
                a = div.find("a", attrs={"class": "catalogue-image"}).get("href")
                a = a.rsplit("/", 1)[0]

                # 3
                one_catalogue(domain + a + "/list", csvwriter, retailer)
        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    get_all_postcodeid()
    

    # common.prep()
    # # test("https://www.coles.com.au/on-special")

    # retailers = []
    # # retailers.append(
    # #     {
    # #         "name": "Woolworths",
    # #         "catalogue": "Woolworths-catalogue"
    # #     }
    # # )
    # retailers.append(
    #     {
    #         "name": "IGA",
    #         "catalogue": "IGA-catalogue"
    #     }
    # )
    
    # with open(common.csv_path, 'a', newline='', encoding='utf-8') as f:
    #     csvwriter = csv.writer(f)
    #     # asyncio.run(specials())
    #     for retailer in retailers:
    #         specials(csvwriter=csvwriter, retailer=retailer)

    #     # promotions("https://www.coles.com.au/promotions/venus?pid=ctatile(specials)_procter-gamble_br360_5089972417", csvwriter)