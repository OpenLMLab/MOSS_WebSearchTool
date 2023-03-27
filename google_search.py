#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line example for Custom Search.

Command-line application that does a search.
"""

__author__ = "xtzhang"
import re
import unicodedata as ucd
import warnings
warnings.filterwarnings('ignore')

import heapq
import time
import pprint

from googleapiclient.discovery import build
import re
import requests
#from HTMLParser import HTMLParser
from html.parser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc 
import spacy
# 必须导入pytextrank，虽然表面上没用上，
import pytextrank
import nltk
import fasttext
from bs4 import BeautifulSoup
#import fasttext.util
import json
import heapq
import re
import time
from urllib import parse

import requests
from bs4 import BeautifulSoup


from textrank_utils import top_sentence
from score_utils import score, score_2, score_3


class prey(object):
    def __init__(self, value, sentence):
        self.value =  value
        self.sentence = sentence
    # 重写 < 符号用于sorted
    def __lt__(self, other):
        return self.value < other.value
    def __gt__(self, other):
        return self.value > other.value
    def __le__(self, other):
        return self.value <= other.value
    def __eq__(self, other):
        return self.value == other.value
    def __ne__(self, other):
        return self.value != other.value
    def __ge__(self, other):
        return self.value >= other.value

def containenglish(str0):
    import re
    return bool(re.search('[a-z]', str0))


def clean_html(html: str) -> str:
    """Remove HTML markup from the given string."""
    # Remove inline JavaScript/CSS, HTML comments, and HTML tags
    cleaned_html = re.sub(
        r"(?is)<(script|style).*?>.*?(</\1>)|<!--(.*?)-->[\n]?|<(?s).*?>", "", html.strip()
    )

    # Deal with whitespace and HTML entities
    cleaned_html = re.sub(
        r"&nbsp;|  |\t|&.*?;[0-9]*&.*?;|&.*?;", "", cleaned_html
    )

    # Normalize the text
    # cleaned_html = ucd.normalize('NFKC', cleaned_html).replace(' ', '')

    return cleaned_html.strip()

def select(new):
    if len(new) < 10:
        oral = new
    elif len(new) // 10 < 10:
        oral = new[:20]
    elif len(new) // 10 > 50:
        oral = new[:50]
    else:
        oral = new[:len(new) // 10] 
    return oral

def get_web_response(url):
    print("[ENGINE] get web response")
    try:
        response = requests.get(url=url, timeout=5)
        response.encoding = 'utf-8'
        return response
    except requests.exceptions.RequestException:
        print("requests post fail")
        return None

def extract_description(soup):
    description = soup.find(attrs={"name": "description"})
    if description:
        content = description.get('content')
        if content:
            return content
    return None

def summ_web(q, url, ft_en, ft_zh, is_eng, nlp_en, nlp_zh, measure_en, measure_zh, snippet,title):
    print(q)
    print(url)
    #start_time = time.time()
    url = parse.unquote(url)
    
    response = get_web_response(url)
    if response is None:
        return {"title":title, "url": url, "summ": snippet, "note": "fail to get ... use snippet", "type": "snippet"}

    soup = BeautifulSoup(response.text, "html.parser")
    description = extract_description(soup)

    if description:
        if all(key_word in description for key_word in q.split()):
            return {"title":title, "url": url, "summ": description, "note": "use description as summ", "type": "description"}

    text = clean_html(response.text)
    sentences = re.split("\n|。|\.", text)

    ft = ft_en if is_eng else ft_zh
    measure = measure_en if is_eng else measure_zh
    nlp = nlp_en if is_eng else nlp_zh

    scored_sentences = []
    for sentence in sentences:
        if 3 <= len(sentence) <= 200:
            scored_sentence = {
                'ft': -1 * score(q, sentence, ft) if ft else None,
                'score_2': -1 * score_2(q, sentence),
                'measure': -1 * score_3(q, sentence, measure=measure) if measure else None,
                'sentence': sentence
            }
            scored_sentences.append(scored_sentence)

    top_sentences = heapq.nsmallest(5, scored_sentences, key=lambda x: x['ft'] or float('inf')) + \
                    heapq.nsmallest(10, scored_sentences, key=lambda x: x['score_2']) + \
                    heapq.nsmallest(5, scored_sentences, key=lambda x: x['measure'] or float('inf'))

    stop_word = "." if is_eng else "。"
    combined_text = stop_word.join([sentence['sentence'] for sentence in top_sentences])

    if len(combined_text) < 3:
        return {"title":title, "url": url, "summ": snippet, "note": "bad web, fail to summ, use snippet,", "type": "snippet"}

    try:
        summary = top_sentence(text=combined_text, limit=3, nlp=nlp)
        summary = "".join(summary)
    except Exception as e:
        return {"title":title, "url": url, "summ": snippet, "note": "unknown summ error , use snippet", "type": "snippet"}

    if any(key_word in summary for key_word in q.split()):
        return {"title":title, "url": url, "summ": summary, "note": "good summ and use it", "type": "my_summ"}

    return {"title":title, "url": url, "summ": snippet, "note": "poor summ , use snippet", "type": "snippet"}

"""
def summ_web(q, url, ft_en, ft_zh, is_eng, nlp_en, nlp_zh, measure_en, measure_zh, snippet ):
    print(q)
    print(url)
    start_time = time.time()
    from urllib import parse
    url = parse.unquote(url)
    try:
        watcher = time.time()
        response = requests.get(url=url, timeout=5)
        print("[summ_web] get cost:", time.time() - watcher)
    except:
        print("[summ_web] cost:", time.time() - start_time)
        return {"url":url, "summ":snippet, \
            "note":"fail to get ... use snippet" , "type":"snippet" }

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text)
    
    description = soup.find(attrs={"name": "description"})

    if description:
        flag = False
        try :
            description['content']
            flag = True
        except:
            pass
        if flag:
            #print(description['content'])
            description = description['content']

    all_in = True
    if description:
        try:
            for key_word in q.split():
                if description.find(key_word) >= 0:
                    pass
                else:
                    all_in = False
            if all_in:
                print("use description as summary")
                print("[summ_web] cost:", time.time() - start_time)
                return {"url":url, "summ":description, \
                    "note":"use description as summ", "type":"description"} 
        except :
            print("warning: catch error, skip description")
            return {"url":url, "summ":description, \
                    "note":"warning: catch error, skip description", "type":"snippet"} 

    text = clean_html(response.text)
   
    sentences = re.split("\n|。|\.", text)
    print("[summ_web] candidates number:", len(sentences))
    #print(sentences)
    new, new_2, new_3 = [], [], []

    t2 = time.time()

    ft = ft_en if is_eng else ft_zh
    measure = measure_en if is_eng else measure_zh
    for sentence in sentences:
        if len(sentence) > 200 or len(sentence) < 3:
            continue

        if ft:
            v = -1 * score(q, sentence, ft)
            p = prey(v, sentence)
            if abs(v) != 0:
                heapq.heappush( new, p )
        
        v2 = -1 * score_2(q, sentence)
        p2 = prey(v2, sentence)
        if abs(v2) != 0:
            heapq.heappush( new_2, p2 )
        
        if measure:
            v3 = -1 * score_3(q, sentence, measure=measure)
            p3 = prey(v3, sentence)
            if abs(v3) != 0:
                heapq.heappush( new_3, p3 )
        
    print( "[summ_web] socre heap cost: ", time.time() - t2 ) 

    stop_word = "." if is_eng else "。"

    oral = select(new)[:5]
    oral_2 = select(new_2)[:10] 
    oral_3 = select(new_3)[:5]
    
    all_orals = oral+oral_2+oral_3
    # for i in all_orals:
    #     print(i.value, i.sentence)
        
    res = stop_word.join([ i.sentence for i in all_orals ])

    nlp =  nlp_en if is_eng else nlp_zh
 
    if len(res) < 3:
        print("[summ_web] too short" )
        return {"url":url, "summ":snippet , \
            "note":"bad web, fail to summ, use snippet,", "type":"snippet"} 
    else:
        t3 = time.time()
        try:
            summ = top_sentence(text=res, limit=3, nlp=nlp)
            print( "textrank cost: ", time.time() - t3 )
        except:
            return {"url":url, "summ":snippet , \
        "note":"unknown summ error , use snippet", "type":"snippet"} 
    #print(summ)
    
    summ = "".join(summ)
    print("[summ_web] cost:", time.time() - start_time)
    #if not summ:
    #    return 
    for key_word in q.split():
        if summ.find(key_word) >=0 :
            print("[summ_web] nice summ", )            
            return { "url":url, "summ": summ, \
                "note":"good summ and use it", "type":"my_summ" }

    return {"url":url, "summ":snippet , \
        "note":"poor summ , use snippet", "type":"snippet"} 

def google_search_api(q):
    service = build("customsearch", "v1", developerKey="<key>")

    t1 = time.time()
    
    res = (
        service.cse().list(
            q=q,
            cx="15c042af751a24b91",
            cr="countryUS",
        ).execute()
    )
    
    print("url cost:", time.time() - t1)
    #url = None
    #for i in res["items"]:
    #    if i["formattedUrl"].split("\.")[-1] == "html":
    #        url = i["formattedUrl"]
    #        break
    urls = []
    for i, url in enumerate(res["items"]):
        urls.append( url["formattedUrl"] )
        if i >= 2:
            break
    print(urls)
    return urls
"""
    
def search_api(q, SERPER_KEY):
    import requests
    import json
    url = "https://google.serper.dev/search"

    if containenglish(q): 
        payload = json.dumps({"q": q,})
    else:
        payload = json.dumps({"q": q})#,"gl": "cn","hl": "zh-cn"})
    headers = {
        'X-API-KEY': SERPER_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)

    return response_dict

"""
def engine(q, ft_en, ft_zh, nlp_en, nlp_zh, measure_en, measure_zh,topk=3):
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    watcher = time.time()
    is_eng = True if containenglish(q) else False
    
    response = search_api(q)
    
    if "answerBox" in response.keys():
        if "link" in response["answerBox"]:
            url = response["answerBox"]["link"]
        else:
            url = response["organic"][0]["link"]
        summ = response["answerBox"]
        print("[EnGINE] answerBox")
        print("[ENGINE] query cost:", time.time() - watcher)
        return {"url":url, "summ":summ, \
            "note":"directly return answerBox, thx google !", "type":"answerBox"}

    def wash_black(urls, snippet, topk=3):
        black_list = [ "enoN, youtube.com, bilibili.com", "zhihu.com" ]
        res = []
        snippets= []
        count = 0
        for i, url in enumerate(urls):
            for domain in black_list:
                if url.find(domain) < 0 and url.split(".")[-1] != "pdf":
                    res.append(url)
                    snippets.append(snippet[i])
                    count += 1
                    if count >= topk:
                        return res, snippets
        return res, snippets

    urls, snippets = wash_black([ i["link"] for i in response["organic"] ],\
        [ i["snippet"] for i in response["organic"] ], topk=topk)
    res = {}
    
    for i, url in enumerate(urls):
        try:
            summ = summ_web(q, url, ft_en, ft_zh, is_eng, nlp_en, nlp_zh, measure_en, measure_zh, snippets[i])
        except:
            summ = {"url":url, "summ":snippets[i], \
            "note":"unbelievable error, use snippet !", "type":"snippet"}
        res[str(i)] = summ
    print("[ENGINE] query cost:", time.time() - watcher)
    return res
"""

def filter_urls(urls, snippets, titles, black_list=None, topk=3):
    if black_list is None:
        black_list = ["enoN, youtube.com, bilibili.com", "zhihu.com"]

    filtered_urls, filtered_snippets, filtered_titles = [], [], []
    count = 0
    for url, snippet, title in zip(urls, snippets, titles):
        if all(domain not in url for domain in black_list) and url.split(".")[-1] != "pdf":
            filtered_urls.append(url)
            filtered_snippets.append(snippet)
            filtered_titles.append(title)
            count += 1
            if count >= topk:
                break

    return filtered_urls, filtered_snippets, filtered_titles

def engine(q, SERPER_KEY,ft_en, ft_zh, nlp_en, nlp_zh, measure_en, measure_zh, topk=3):
    start_time = time.time()
    is_eng = containenglish(q)

    response = search_api(q, SERPER_KEY)

    if "answerBox" in response.keys():
        url = response["answerBox"].get("link", response["organic"][0]["link"])
        summ = response["answerBox"]
        print("[EnGINE] answerBox")
        print("[ENGINE] query cost:", time.time() - start_time)
        return {"url": url, "summ": summ, "note": "directly return answerBox, thx google !", "type": "answerBox"}

    raw_urls = [i["link"] for i in response["organic"]]
    raw_snippets = [i["snippet"] for i in response["organic"]]
    raw_titles = [i["title"] for i in response["organic"]]
    urls, snippets, titles = filter_urls(raw_urls, raw_snippets, raw_titles, topk=topk)

    results = {}
    for i, url in enumerate(urls):
        try:
            summ = summ_web(q, url, ft_en, ft_zh, is_eng, nlp_en, nlp_zh, measure_en, measure_zh, snippets[i], titles[i])
        except:
            summ = {"url": url, "summ": snippets[i], "note": "unbelievable error, use snippet !", "type": "snippet", "title":titles[i]}

        results[str(i)] = summ

    print("[ENGINE] query cost:", time.time() - start_time)
    return results   

if __name__ == "__main__":
    import time
    print("loading embeddings ...")
    ft_en = fasttext.load_model('cc.en.300.bin')
    ft_zh = fasttext.load_model('cc.zh.300.bin')
    nlp_en = spacy.load("en_core_web_sm")
    nlp_zh = spacy.load("zh_core_web_sm")
    from score_utils import score_measure
    measure_en = None#score_measure("en")
    measure_zh = None#score_measure("zh")
    print("embeddings loaded ...")

    start_time = time.time()
    #engine("复旦 排名")#yes
    #engine("张文宏")#yes
    #engine("relative molecular mass of carbon dioxide", measure_en, measure_zh)#yes
    #engine("爱因斯坦场方程 解的数目")#yes
    #engine("Stable Diffusion introduction", measure_en, measure_zh)#yes
    #engine("quick sort", measure_en, measure_zh)#yes
    #engine("document image rectification", ft_en, ft_zh, measure_en, measure_zh)#yes
    #engine("忽如一夜春风来，千树万树梨花开 季节", ft_en, ft_zh, measure_en, measure_zh)#no
    print(engine("奔驰c 比亚迪model y 比较", open("serper_key").readline(), ft_en, ft_zh, nlp_en, nlp_zh, measure_en, measure_zh))#yes
    print(time.time() - start_time)

