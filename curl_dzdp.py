# -*- coding:utf-8 -*-
import requests
import re
from math import ceil
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
}
Cookies={'cy':'16',
         'cye':'wuhan',
         '_lxsdk_cuid':'1696b22adf1c8-0dec8e1e589ef7-58432916-1fa400-1696b22adf1c8',
         ' _lxsdk':'1696b22adf1c8-0dec8e1e589ef7-58432916-1fa400-1696b22adf1c8',
         ' _hc.v':'dbeeff87-3d4c-3e46-b45f-58dcb8231745.1552280629',
         ' _lx_utm':'utm_source%3DBaidu%26utm_medium%3Dorganic',
         ' s_ViewType':'10',
         ' default_ab':'shopList%3AA%3A1',
         ' cityid':'1',
         '_lxsdk_s':'16980368964-575-705-d8d%7C%7C256'}
con = requests.get("http://www.dianping.com/wuhan/ch11", headers=headers).content.decode("utf-8")

def get_class_name(con):
    class_content = re.findall('<div class="txt">(.*?)<div class="operate J_operate Hide">',con, re.S)
    # print(class_content)
    class_shop_names =[]
    class_attributes_names =[]
    shop_infos = []
    class_shop_names.append(re.findall('data-hippo-type="shop" title="(.*?)" target="_blank"', con, re.S))
    for i in class_content:
        #获取值然后将这个值替换为字典，然后回到原文，然后进行<span class="(.*?)"><\/span>替换为具体的数字
        #采用正则表达式取出5位数字或者字母
        class_attributes_names.extend(re.findall('<span class="([a-zA-Z0-9]{5,})"></span',i, re.S))
        #获取相应的属性
        shop_name = re.findall('<h4>(.*?)</h4>',i, re.S)[0]
        shop_review = re.findall('nofollow">(.*?)条点评</a>',i, re.S)[0][3:-4]
        shop_tag = re.findall('<span class="tag">(.*?)</span></a>',i, re.S)[0]
        shop_addr = re.findall('pan class="addr">(.*?)</div>',i, re.S)[:-6]
        shop_price = re.findall('<b>￥(.*?)</b>',i, re.S)[0]

        shop_info = {'shop_name':shop_name,
                     'shop_rwview':shop_review.strip()[3:-1],
                     'shop_tag':shop_tag,
                     'shop_price':shop_price}
        shop_infos.append(shop_info)
        # print(shop_info)
    #一共得到15个商家的值（店名和具体的被加密的数字的属性）
    # print(class_attributes_names)
    if len(class_content):
        print(len(class_content))
    else:
        print('error,not found ')
        class_name = []
        #返回数据的信息
    return shop_infos,list(set(class_attributes_names))

def get_css_href(con):
    css_back = re.findall(' <link rel="stylesheet" type="text/css" href="//s3plus.meituan.net/v1/(.*?)">',con, re.S)
    if len(css_back):
        css_href = 'http://s3plus.meituan.net/v1/'+css_back[0]
    else:
        print('error,not found css_href')
        css_href = []
    return css_href

def get_svg_href(css_href,class_name=None,):
    con = requests.get(css_href, headers=headers,cookies=Cookies).content.decode("utf-8")
    # print(con)
    #在这里可以看到fvj77的211.0px -114.0px;这个用来计算
    svg_items = re.findall('class\^="(.*?)"(.*?): url\(\/\/(.*?)\)', con, re.S)
    for item in svg_items:
        # if class_name in item:
            yield [item[0],item[2]]

def get_dict_of_svg(svg_hrefs):
    list1 = []
    for label,svg_href in svg_hrefs:
        dict ={}
        con = requests.get('http://'+svg_href, headers=headers).content.decode("utf-8")
        dict_svg = re.findall('y="(.*?)">(.*?)</text>', con, re.S)
        # print('dict_svg:',dict_svg)
        dict['label'] = label
        if len(dict_svg):
            for i in dict_svg:
                dict[str(i[0])] = i[1]
        else:
            print('error not found this svg')
        print(dict)
        list1.append(dict)
    return list1

def set_class_dict(con,css_href):
    #返回一个迭代器，
    dict= {}
    con = requests.get(css_href, headers=headers, cookies=Cookies).content.decode("utf-8")
    dict_class_px = re.findall('.([a-zA-Z0-9]{5,}){background:-(.*?).0px -(.*?).0px;}', con, re.S)
    for i in dict_class_px:
        dict[i[0]]=[i[1],i[2]]
    return dict

shop_infos,class_names=get_class_name(con)
css_href = get_css_href(con)
# print(css_href)
svg_href = get_svg_href(css_href,'fv')

list1 = get_dict_of_svg(svg_href)
#进行替换字典的建立，将<span class="(.*?)"><\/span>替换为具体的数字或者是汉字
dict_repalce = {}
dict_class=set_class_dict(con,css_href)
# print(dict_class)

dict_repalce_content = {}
for i in class_names:
    for j in list1:
        if i[0:2] == j['label']:
            x = int(dict_class[i][0])
            y = int(dict_class[i][1])
            #固定font_size 为12px
            offset = x//12+1
            #进行遍历获得key,进行对比
            for k in j.keys():
                if k != 'label':
                    # print(k)
                    if y<int(k):
                        str1 = j[k]
                        break
                        # print(str1)
            value = str1[offset-1]
            dict_repalce_content[i] = value
            # print(i,x,y,value)
# print(dict_repalce_content)

#将得到的网页利用得到的字典进行转换正常格式的信息
#只能进行循环遍历
for shop_info in shop_infos:
    for k,info in shop_info.items():
        if k != 'shop_name':
            class_names_1 = re.findall('<span class="([a-zA-Z0-9]{5,})"></span>',info,re.S)
            # print(class_names_1)
            for i in class_names_1:
                # print('shop_info[k]',shop_info[k])
                # print(i,dict_repalce_content[i])
                shop_info[k] =shop_info[k].replace('<span class="'+i+'"></span>',dict_repalce_content[i])
    print(shop_info)
