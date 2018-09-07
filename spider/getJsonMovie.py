#coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import time
import json

def get_data(url,movies,movie_file,**kw):
	user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
	headers={'User-Agent':user_agent}
	page_start = 0
	while(True):
		get_url = url + str(page_start)
		if kw.get('genres',None):
			get_url = get_url+ '&genres='+kw['genres']
		if kw.get('countries',None):
			get_url = get_url + '&countries=' + kw['countries']
		html = requests.get(get_url,user_agent)
		print(html.json())
		movie_json = html.json()['data']
		if len(movie_json)==0:
			break
		else:
			for movie in movie_json:
				#movies.append(movie)
				print(movie)
				for k,v in movie.items():
					try:
						movie_file.write(k+'::')
						if isinstance(v,int):
							movie_file.write(str(v)+',')
						if v=='' or v == None:
							movie.file.write(',')
						if k=='casts':
							movie_file.write(' '.join(v)+',')
						else:
							movie_file.write(''.join(v)+',')
					except:
						pass
				movie_file.write('\n')
				movie_file.flush()
		page_start = page_start+20

url= r'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=电视剧&start='
#geners = ['中国大陆','美国','香港','台湾','日本','韩国','英国','法国','德国','意大利','西班牙','印度','泰国','俄罗斯','伊朗','加拿大','澳大利亚','爱尔兰','瑞典','巴西','丹麦']
genes = ['剧情','喜剧','动作','爱情','科幻','悬疑','惊悚','恐怖','犯罪','同性','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠','情色']
movies = []

def get_fromlist():
	movie_file = open('data.txt','a+')
	for item in genes:
		print('爬虫开始...')
		get_data(url,movies,movie_file,countries='美国',genres=item)
	movie_file.close()
	print('爬虫结束...')

if __name__ == '__main__':
	get_fromlist()



