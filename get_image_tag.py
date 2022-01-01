import yaml
import json
import collections as cl
from datetime import datetime as dt
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.request import urlopen
from multiprocessing import Pool
import csv
import os

def info():

    tmp = cl.OrderedDict()
    tmp["description"] = "nikoniko image"
    tmp["url"] = "https://seiga.nicovideo.jp/seiga/"
    tmp["version"] = "0.01"
    tmp["year"] = "2021"
    tmp["contributor"] = ""
    tmp["data_created"] = "2021/12/26"
    return tmp

def licenses(data):
    tmp = cl.OrderedDict()
    tmp["id"] = int(data["id"][2:])
    tmp["url"] =data["url"]
    tmp["name"] =data["title"]

    return tmp
def makelicenses(datas):
    tmps = []
    for i,data in enumerate(datas):
        tmps.append(licenses(data))
    return tmps

def images(data):

    tmp = cl.OrderedDict()
    tmp["license"] = 0
    tmp["id"] = int(data["id"][2:])
    tmp["file_name"] = data["id"] + ".jpg"
    tmp["width"] = 0
    tmp["height"] = 0
    tmp["date_captured"] = data["time"][:20]
    tmp["coco_url"] = data["url"]
    tmp["flickr_url"] = data["url"]
    return tmp
def makeimages(datas):
    tmps = []
    for i,data in enumerate(datas):
        tmps.append(images(data))
    return tmps

def annotations(data,category):
    tmp = cl.OrderedDict()

    tmp_segmentation = cl.OrderedDict()
    tmp["segmentation"] = [[]]
    tmp["id"] = int(str(1000)+ str(data["id"][2:]))
    tmp["image_id"] =  int(data["id"][2:])
    tmp["category_id"] = category
    tmp["area"] = 0
    tmp["iscrowd"] = 0
    tmp["bbox"] =  [[]]
    return tmp

def my_index(l, x, default=False):
    if x in l:
        return l.index(x)
    else:
        return default
def makeannotations(datas,tags):
    tmps = []
    for i,data in enumerate(datas):
        for j,tag in enumerate(data["tag"]):
            tmp_index = my_index(tags,tag,-1)
            if tmp_index > -1:
                tmps.append(annotations(data,tmp_index))
    return tmps
    
def categories(tags):
    tmps = []
    #最初の1つ目のタグがsupercategoryとする
    for i,tag in enumerate(tags):
        tmp = cl.OrderedDict()
        tmp["id"] = i
        tmp["supercategory"] = tag
        tmp["name"] = tag
        tmps.append(tmp)
    return tmps
def MakeTag(datas):
    tags = []
    for i,data in enumerate(datas):
        tags = tags + data["tag"]
    c = cl.Counter(tags)
    values, counts = zip(*c.most_common())
    return values, counts

def Makecocodata(obj,savename,tagsavename):
    #タグを整理する
    print("tag")
    tags, counts = MakeTag(obj["image"])
    list_leng = int(len(tags)/10)
    print(counts[:list_leng])
    print(tags[:list_leng])
    counts = counts[:list_leng]
    tags = tags[:list_leng]

    with open(tagsavename, 'w',encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(tags)

    js = cl.OrderedDict()
    print("info")
    tmp = info()
    js["info"] = tmp

    print("licenses")
    tmp = makelicenses(obj["image"])
    js["licenses"] = tmp

    print("images")  
    tmp = makeimages(obj["image"])
    js["images"] = tmp
  
    print("annotations") 
    tmp = makeannotations(obj["image"],tags)
    js["annotations"] = tmp
   
    print("categories")     
    tmp = categories(tags)
    js["categories"] = tmp
   
    
    with open(savename,'w',encoding = "utf8") as fw:
        json.dump(js,fw,indent=2, ensure_ascii=False)

def main():
    tmages_ = cl.OrderedDict()
    image_list = []
    count = 1
    #フォルダを作成
    try:
        os.makedirs("tag")
    except FileExistsError:
        pass
    try:
        os.makedirs("coco")
    except FileExistsError:
        pass
    for j,I in enumerate( range(10876227,6876227,-1)):
    
        tmp = cl.OrderedDict()
        URL = "https://seiga.nicovideo.jp/seiga/im" + str(I)
        print(URL)
        html = urlopen(URL).read()
        soup = BeautifulSoup(html, "html.parser")

        lg_ttl_illust = soup.find_all('div',class_='lg_ttl_illust')
        if len(lg_ttl_illust) > 0:
            tmp["id"] = "im" + str(I)
            tmp["url"] = URL

            lg_txt_illust = soup.find_all('div',class_='lg_txt_illust')
            lg_txt_date = soup.find_all('div', class_='lg_txt_date')

            tmp["title"] = lg_ttl_illust[0].text
            tmp["contributor"] = lg_txt_illust[0].text
            tmp["comment"] = lg_txt_illust[1].text
            tmp["time"] = lg_txt_date[0].text


            
            tags = soup.find_all('a', class_='tag')
            tag_list = []
            for i in tags:
                tag_list.append(i.text)
            tmp["tag"] = tag_list
            image_list.append(tmp)

        

        time.sleep(1)
        #定期的に保存
        if j%1000000 == 999999:
            tmages_tmp = cl.OrderedDict()
            tmages_tmp["image"] = image_list
            Makecocodata(tmages_tmp,'coco/cocodata_'+ str(count) +'.json','tag/' + 'tagdata_' + str(count) +'.csv')
            count = count + 1
            image_list = []

    tmages_["image"] = image_list
    Makecocodata(tmages_tmp,'coco/cocodata_'+ str(count) +'.json','tag/' + 'tagdata_' + str(count) +'.csv')

if __name__ == '__main__':
    main()
