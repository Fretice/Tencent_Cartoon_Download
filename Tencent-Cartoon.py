#-*- coding:utf-8 -*-
import os
import base64
import json
import requests
import datetime
from pyquery import PyQuery as pq
from multiprocessing.dummy import Pool as ThreadPool


def get_list(url):
    """根据URL获取章节列表"""
    q = pq(requests.get(url).text)
    all_chapter = []
    chapter_tags = q.find("#chapter").find(".works-chapter-list").eq(0).find("a")
    for tag in chapter_tags:
        chapter_title = ''.join(tag.attrib["title"].split('：')[1:])
        chapter_url = 'http://ac.qq.com' + tag.attrib['href']
        all_chapter.append({'title':chapter_title,'url':chapter_url})
    name = q.find('h2').eq(0).text()
    name = filter_filename(name)
    return all_chapter,name

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

def download_chapter(chapter):
    cur_dir = os.getcwd()
    title = chapter['title']
    pic_list = chapter['pic_list']
    dir_path = os.path.join(cur_dir,IMG_DIR,filter_filename(title))
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except:
            print('目录已存在')
    print('正在下载 {0}'.format(title))
    for i in range(1,len(pic_list)):
        try:
            url = pic_list[i]
            file_path = os.path.join(dir_path,str(i) + '.jpg')
            img = requests.get(url).content
            with open(file_path,'wb') as f:
                f.write(img)
        except Exception as e:
            print('这张图片下载出错',title,pic_list[i])

def filter_filename(filename):
    '''windows文件名过滤非法字符串'''
    illegal_str = r'\/:*?"<>|'
    repalce_str = r' '
    map_str = filename.maketrans(illegal_str,repalce_str*len(illegal_str))
    return filename.translate(map_str)

def download_all(input_url):
    """根据URL下载漫画文件方法"""
    all_chapter,name = get_list(input_url)
    chapter_list = []
    input_text = input("共找到{0}话".format(len(all_chapter))+ \
    "\n请输入你想要下载的章节\n如果你想要下载下载全部,请直接回车:")
    if input_text == "":
        start_chapter = 1
        end_chapter = len(all_chapter)
    else:
        try:
            start_chapter = int(input_text.split('-')[0])
            end_chapter = int(input_text.split('-')[-1])
            if len(all_chapter) < end_chapter \
                or start_chapter == 0 \
                or start_chapter > end_chapter:
                print('你个逗比, ╤_╤')
        except TypeError:
            print('呵呵')
            exit()
    for chapter in all_chapter[start_chapter-1:end_chapter]:
        print('正在抓取下载地址 {0}'.format(chapter['title']))
        chapter['pic_list'] = get_detail_list(chapter['url'])
        chapter_list.append(chapter)
    return chapter_list,name

if  __name__ == "__main__":
    start_url = input("请输入你想要下载的漫画的url,\n类似 http://ac.qq.com/Comic/ComicInfo/id/505430\n:")
    # start_url = 'http://ac.qq.com/Comic/ComicInfo/id/505430'
    pool = ThreadPool(8)
    chapter_list,IMG_DIR = download_all(start_url)
    begin_time = datetime.datetime.now()
    print('开始下载喽........O(∩_∩)O~~\r\n开始时间:'+str(begin_time))
    pool.map(download_chapter, chapter_list)
    pool.close()
    pool.join()
    end_time = datetime.datetime.now()
    print(end_time)
    time_lost = (end_time - begin_time).seconds
    print('下载完成喽.......O(∩_∩)O~~\n共耗时:{0}秒'.format(time_lost))
