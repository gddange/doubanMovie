#coding:utf-8
import requests,random,time
from bs4 import BeautifulSoup
import re,time
import http.cookiejar as CJ
import multiprocessing
from PIL import Image
#from douban import get_captcha

BID_LIST_LEN = 100
BID_LEN=11

#用来存储每一部movie的信息
def readtxt():
	movies = []
#moviesurl = []
	with open('tvseries.txt','r+') as f:
		for line in f:
			line = line.strip('\n')
			movie = line.split(',')
			movie=movie[:-1]
			moviedes = {}
			for subinfo in movie:
				splitsubinfo = subinfo.split('::')
				try:
					k,v = splitsubinfo
					if k=='star':
						moviedes['star'] = v
					if k=='rate':
						moviedes['rate'] = v
					if k=='title':
						moviedes['title'] = v
					if k=='url':
						moviedes['url']=v
				except:
					pass
			if len(moviedes) !=0:
				movies.append(moviedes)
			#break
		f.close()
		return movies

def read_firstdata(fileName):
	movies  = []
	with open(fileName,'r')as tf:
		for line in tf.readlines():
			movie = {}
			lines = line.strip().split('\t')
			movie['title'] = lines[1]
			movie['rate'] =lines[3]
			movie['star'] = lines[4]
			movie['url'] = lines[-1]
			movies.append(movie)
	return movies

#简单方式get fino
def get_infotext(info):
	movieinfo = {}
	infotext = info.text
	infolist = infotext.split('\n')
	for detail in infolist:
		textlist = detail.split(':')
		if len(textlist) != 0:
			if textlist[0] == '导演':
				movieinfo['director'] = textlist[1]
			if textlist[0] == '编剧':
				movieinfo['scenarist'] = textlist[1]
			if textlist[0] == '主演':
				movieinfo['actors'] = textlist[1]
			if textlist[0].__contains__('类型'):
				movieinfo['classification'] = textlist[1]
			if textlist[0].__contains__('制片国家'):
				movieinfo['country'] = textlist[1]
			if textlist[0] == '语言':
				movieinfo['laguage'] = textlist[1]
			if textlist[0] == '又名':
				movieinfo['multiName'] = textlist[1]
			if textlist[0] == '片长':
				movieinfo['time'] = textlist[1]
			if textlist[0] == 'IMDb链接':
				movieinfo['imdb'] = textlist[1]
	return movieinfo

def writetxt(movie,num):
	with open('data/movie'+str(num)+'.txt','a+')as f:
		for k,v in movie.items():
				f.write(k+":"+v+',')
		f.write('\n')
		f.flush()
		f.close()

#设置代理
def check_ip():
	url = 'https://movie.douban.com/subject/3445559/'
	fp = open('data/host.txt','r')
	ips = fp.readlines()
	fp.close()
	proxys = list()
	valid = []
	ips = set(ips)
	for p in ips:
		ip = p.strip('\n').split('\t')
		proxy = 'http://' + ip[0] + ':' + ip[1]
		proxies = {'https:':proxy}
		proxys.append(proxies)
	for pro in proxys:
		try:
			s = requests.get(url,headers={ "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"},proxies = pro)
			#print(s)
			valid.append(pro)
		except Exception as e:
			print(e)
	return valid

#print(len(moviesurl))
def getmovieinfo(moviedes,valid_proxies,bids,num):
	user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
	headers = {
	    'User-Agent':user_agent
	    }
	proxies = random.choice(valid_proxies),
	movies = []
	i = 0
	if len(moviedes)==0:
		return None
	for movie in moviedes:
		try:
			#print(random.choice(valid_proxies))
			response = requests.get(movie['url'],headers = headers,proxies = random.choice(valid_proxies))
			html = BeautifulSoup(response.text.encode('utf-8','ignore').decode('utf-8','ignore'),'lxml')
			print(response.status_code)
			print('正在解析第%s部电视剧...'%str(i))
			if(response.status_code=='403'):
				print(response.url)
				break
			print(movie['url'])
			info = html.find('div',{'class':'subjectwrap'}).select('div#info')[0]
			#print(info)
			i +=1
			movieinfo = get_infotext(info)  
			movieinfo['title'] = movie['title']
			movieinfo['rate'] = movie['rate']
			movieinfo['star'] = movie['star']
			year = html.find('span',{'class':'year'}).text
			year = get_num(year)
			rating_sum = html.find('a',{'class':'rating_people'}).text
			movieinfo['rating_sum'] = get_num(rating_sum)
			movieinfo['year'] = year
			comment= html.find('div',{'id':'comments-section'}).find('div',{'class':'mod-hd'}).find('h2').find('a').text
			movieinfo['commentnum'] = get_num(comment)
			longcoment = html.find('section',{'class':'reviews'}).find('header').find('h2').find('a').text
			movieinfo['longnum'] = get_num(longcoment)
			movies.append(movieinfo)
			writetxt(movieinfo,num)
		except Exception as e:
			print(e)
		time.sleep(random.uniform(2.5,4))                                                                                     #设置延时
	return movies

def get_num(text):
	pattern = re.compile(r'[0-9]+')
	commentnum = re.search(pattern,text)
	return commentnum.group()

def get_a(text):
	result = []
	for a in text.find_all('a'):
		result.append(a.text)
	return result

def get_info(info):
	#最后需要转换成为dataframe进行分析，中间用空格隔开，各属性之间用，隔开
	location = info.find('span',{'class':'actor'})
	actors = get_a(location)
	direcandbian = location.find_previous_siblings()
	for element in direcandbian:
		pl = element.find('span',{'class':'pl'})
		if pl:
			if pl.text == '编剧':
				scenarist = get_a(element)
			if pl.text=='导演':
				director = get_a(element)
	next_siblings = location.find_next_siblings()
	return ' '.join(scenarist),' '.join(director),' '.join(actors)

if __name__ == '__main__':
	print('开始爬取数据...')
	cookies = []
	movies = read_firstdata('doubanmovie.txt')
	valid_proxy = check_ip()
	p1 = multiprocessing.Process(target=getmovieinfo,args=(movies[:5000],valid_proxy[:25],cookies,113))   
	p2 = multiprocessing.Process(target=getmovieinfo,args=(movies[5000:10000],valid_proxy[25:50],cookies,114))
	p3 = multiprocessing.Process(target=getmovieinfo,args=(movies[10000:15000],valid_proxy[50:75],cookies,115))
	p4 = multiprocessing.Process(target=getmovieinfo,args=(movies[15000:],valid_proxy[75:100],cookies,116))
	p2.deamon=p3.deamon=p4.deamon=p1.deamon=True
	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p1.join()
	p2.join()
	p3.join()
	p4.join()
	print("爬取结束.")


