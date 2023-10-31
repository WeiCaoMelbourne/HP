from datetime import datetime
import os 

csv_path = None

# csv format
# cmpy, prod_id, name, brand, size, desc, aisle, catetory, sub-category, price, was, discount, img_url
def product_list(
        cmpy,
        prod_id,
        name, 
        brand, 
        size, 
        desc, 
        aisle, 
        catetory, 
        sub_category, 
        price, 
        was,
        discount,
        img_url
    ):
    return [
        cmpy,
        prod_id,
        name, 
        brand, 
        size, 
        desc, 
        aisle, 
        catetory, 
        sub_category, 
        price, 
        was,
        discount,
        img_url
    ]

def prep():
    global csv_path
    date_str = datetime.today().strftime('%Y-%m-%d')
    if not os.path.isdir(date_str):
        os.mkdir(date_str)

    csv_file = f"{date_str}.csv"
    csv_path = os.path.join(date_str, csv_file)
    # print(csv_path)
    if os.path.exists(csv_path):
        os.remove(csv_path)

# def save_to_csv(f, line):
# with open('douban250.csv', 'w', newline='', encoding='utf-8') as f:
#                 csvwriter = csv.writer(f)
                
#                 # re_obj = re.compile(r'<li>.*?<span class="title">(?P<title>.*?)</span>', re.S)
#                 re_obj = re.compile(r'<li>.*?<span class="title">(?P<title>.*?)</span>'
#                                     r'.*?<p class="">.*?<br>(?P<year>.*?)&nbsp'
#                                     r'.*?<span class="rating_num" property="v:average">(?P<score>.*?)</span>'
#                                     r'.*?<span>(?P<number>.*?)人评价</span>', re.S)
#                 result = re_obj.finditer(page_content)
#                 for iter in result:
#                     # print(iter.group("title"), iter.group("year").strip(), iter.group("score"), iter.group("number"))

#                     d = iter.groupdict()
#                     d['year'] = d['year'].strip()
#                     csvwriter.writerow(d.values())