#-*- coding:utf-8 -*-
import os
import base64
import json
import requests
import datetime
import platform
from pyquery import PyQuery as pq
from multiprocessing.dummy import Pool as TheadPool




def get_id_by_name(name):
    """根据输入的名称获取漫画ID"""
    params = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Host': 'ac.qq.com',
        'Referer': 'http://ac.qq.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
                      Chrome/57.0.2987.133 Safari/537.36'
    }
    aim_url = 'http://ac.qq.com/Comic/searchList/search/'+name
    r = requests.get(aim_url, params=params)
    q = pq(r.text)
    total_count = q.find('.all_total_num').eq(0).text()
    if total_count != None and total_count !="":
        index = input("共找到{0}部漫画,请输入你想要下载的漫画的序号".format(total_count))
        return 'http://ac.qq.com'+q.find('.mod_book_list').find('.mod_book_cover').eq(int(index)-1).attr("href")
    else :
        return '没有找到与您输入相关的漫画'




def get_list_count(url):
    """根据URL获取章节数目"""
    q = pq(requests.get(url).text)
    a_count = q.find("#chapter").find(".works-chapter-list").eq(0).find("a").length
    return a_count

def get_list(url):
    """根据URL获取章节列表"""
    q = pq(requests.get(url).text)
    a_count = q.find("#chapter").find(".works-chapter-list").eq(0).find("a").length
    list_out = [];
    for i in range(a_count):
        list_out.append('http://ac.qq.com'+q.find("#chapter").find(".works-chapter-list").eq(0).find("a").eq(i).attr("href"))
    return list_out;

def get_detail_list(url):
    """根据详细URL获取章节详细页面并解析"""
    q = pq(requests.get(url).text)
    datail_list = json.loads( \
        base64.b64decode( \
           q.find('.pop-up-msg').next().next().text().split('\'')[1][1::] \
            ).decode())['picture']
    pic_list = []
    for i in datail_list:
        pic_list.append(i['url'])
    return pic_list

def download_pic(url):
    """根据URL下载图片"""
    try:
        if url is not None and url != "":
            r = requests.get(url)
            with open(url.split('_')[-1].split('.')[0]+'.jpg', "wb") as file:
                file.write(r.content)
    except Exception:
        exit()

        

def create_dir_by_name(dir_name):
    """根据名称创建文件夹或将目录移动该文件夹下"""
    cur_dir = os.getcwd()
    if platform.system() == 'Linux':
        aim_dir = cur_dir+'/'+name_input
    elif platform.system() == 'Windows':
        aim_dir = cur_dir+'\\\\'+name_input
    if os.path.exists(aim_dir) is False:
        os.mkdir(aim_dir)
    os.chdir(aim_dir)

def download_all(input_url):
    """根据URL下载漫画文件方法"""
    total_count = get_list_count(input_url)
    list_out = get_list(input_url)
    input_text = input("共找到{0}话".format(total_count)+ \
    "\r\n请输入你想要下载的章节\r\n如果你想要下载下载全部,请直接回车:")
    pic_list_all = []
    if input_text == "": 
        page_index = 1
        for i in list_out:
            print('正在抓取第{0}话的下载地址'.format(page_index))
            pic_list = get_detail_list(i)
            page_index += 1
            pic_list_all.extend(pic_list)
    else:
        try:
            download_detail_index = int(input_text)
            if total_count < download_detail_index \
                or download_detail_index == 0:
                print('你个逗比, ╤_╤')
            else:
                aim_url = list_out[download_detail_index-1]
                pic_list = get_detail_list(aim_url)
                pic_list_all.extend(pic_list)
        except TypeError:
            print('呵呵')
    return pic_list_all

if  __name__ == "__main__":
    name_input = input("请输入你想要下载的漫画名称:")
    input_url = get_id_by_name(name_input)
    if input_url.find('没有') == -1:
        pool = TheadPool(13)
        create_dir_by_name(name_input)
        begin_time = datetime.datetime.now()
        pic_list_download = download_all(input_url)
        print('开始下载喽........O(∩_∩)O~~\r\n开始时间:'+str(begin_time))
        pool.map(download_pic, pic_list_download)
        pool.close()
        pool.join()
        end_time = datetime.datetime.now()
        print(end_time)
        time_lost = (end_time - begin_time).seconds
        print('下载完成喽.......O(∩_∩)O~~\r\n共耗时:{0}秒'.format(time_lost))
    else:
        print(input_url)

