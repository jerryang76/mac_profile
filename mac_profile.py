# coding=utf-8
import httplib,urllib,re, time, ssl , sys
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def help():
	print 'mac_profile <Destination IP> <port> <username> <password> <http,https>'
	print 'example:'
	print 'mac_profile 1.1.1.1 443 root password https'
	print 'mac_profile 1.1.1.1 80 root password http'
	sys.exit()


if len(sys.argv) < 6:
	help()
host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
Pass = sys.argv[4]
prot = sys.argv[5]

#連線前準備，GW位置
# host = '10.10.1.223'
# user = 'octtel'
# Pass = '12841302'
#排除網站阻擋
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
headers = { 'User-Agent' : user_agent}
#連線控制與URL


def http_get(prot,url):
	#列出來源頁面
	if prot == 'http':
		http_connect = httplib.HTTPConnection(host, port, timeout=10)	
	elif prot == 'https':
		http_connect = httplib.HTTPSConnection(host, port, timeout=10, context=ctx)	 	
	else:
		help()
	#print "<br>"
	#request(method, url, headers)
	#print (url,headers)
	http_connect.request('GET', url, '', headers)	
	#準備收取內容
	http_data = http_connect.getresponse()
	#Read page source html
	data = http_data.read()
	http_connect.close()
	#print data
	return data
	
	
def http_post(prot,url,params):
	#列出來源頁面
	if prot == 'http':
		http_connect = httplib.HTTPConnection(host, port, timeout=10)	
	elif prot == 'https':
		http_connect = httplib.HTTPSConnection(host, port, timeout=10, context=ctx)	 	
	else:
		help()
	#print "<br>"
	#request(method, url, body, headers)
	#print (host,url,params,headers)	
	# http_data = urllib.urlopen(url, params)
	http_connect.request('POST', url, params, headers)	
	# 準備收取內容
	http_data = http_connect.getresponse()
	# Read page source html
	data = http_data.read()
	http_connect.close()
	#print data	
	return data
	
url = params = mac = data = firmware_long = ''

# login
def login():
	login_url = '/goform/LoginForm'
	login_pass = 'username='+user+'&password='+Pass
	url = "/LoginForm.asp"
	useless1 = http_get(prot,url)
	url = login_url
	params = login_pass
	login_page = http_post(prot,url,params)
	print 'Login...'
	time.sleep(1)
	url = "/LoginFirstPageForm.asp"
	useless2 = http_get(prot,url)

# get status MAC, HW, Driver, Firmware
def status():
	url = '/goform/StatusLoad'
	params = 'FORM=SystemInformationForm'
	getinformation = http_post(prot,url,params)
	# print "-----------------------------------"
	# print getinformation
	# print "-----------------------------------"
	# str.find(str, beg=0, end=len(string))
	mac_head = getinformation.find('"WanMac":"')
	mac_tail = getinformation.find('"',mac_head+len('"WanMac":"'))
	mac = getinformation[mac_head+len('"WanMac":"'):mac_tail]
	print mac
	firmware_head = getinformation.find('Ver(')
	firmware_tail = getinformation.find('==',firmware_head+len('Ver('))
	firmware_long = getinformation[firmware_head+len('Ver('):firmware_tail]	
	print firmware_long
	firmware_tail = getinformation.find(' ',firmware_head+len('Ver('))
	firmware_short = getinformation[firmware_head+len('Ver('):firmware_tail]
	# print firmware_short
	return mac, firmware_long


# backup profile
def backup():
	url = '/goform/AjaxPost'
	params = 'ajax_action=CONFIG_BACKUP&backup_type=BACKUP_PROFILE'
	profile_url = http_post(prot,url,params)
	time.sleep(1)
	# print profile_url
	profile_url_head = profile_url.find('":"')
	profile_url_tail = profile_url.find('"',profile_url_head+len('":"'))
	profile_url = profile_url[profile_url_head+len('":"'):profile_url_tail]
	url = profile_url
	# url = '/tmp/backup.profile'
	config = http_get(prot,url)
	mac_profile = mac+'.profile'
	print 'Writing '+mac_profile
	# Writing backup.profile
	#https://docs.python.org/3/tutorial/inputoutput.html
	with open(mac_profile, mode='wb') as file:		
		file.write(config)
	file.closed
	print 'Done!'
	

login()
#帶進function的string值放在()裡面，帶出來的string放在return中，function中會用到的值也可以放在global中
mac,firmware_long = status()
#print firmware_long
backup()
