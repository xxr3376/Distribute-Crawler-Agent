cookies_string = "SINAGLOBAL=1626578483264.8933.1405389915226; __utma=15428400.1879566305.1405475927.1405475927.1405475927.1; __utmz=15428400.1405475927.1.1.utmcsr=weibo.com|utmccn=(referral)|utmcmd=referral|utmcct=/u/5200297795/home; __gads=ID=c3e4428bd8078662:T=1405516288:S=ALNI_MbLjCDvMGInBrdQ-oTqqlxfB72Z3w; myuid=5242355424; wvr=5; SUS=SID-5243473869-1407380454-GZ-mtfck-d5e4d365a9aab95bc1e88a1bb0d0af49; SUE=es%3D5bbfafea5502a3651ce28d74083c60fd%26ev%3Dv1%26es2%3D08762bd1ab7e849dda101b2dec145db6%26rs0%3DDVttXZYUAlihdZtdR2n4swpJDVjhSND%252BblB0UwlZKtYcJycBh6I%252FRr78LOmj2QYPxHDHKy%252BsS3K2Wh3GkQsBbd4US9aQ6fN3EdMJKzEQeyFlyvBCVvneBDlWFpdqus4rqn6aZY%252BWKl7OdQeBmc06rnlh1uqC1FIqrVpyE2PVkjc%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1407380454%26et%3D1407466854%26d%3Dc909%26i%3Daf49%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D2%26st%3D0%26uid%3D5243473869%26name%3D1908639260%2540qq.com%26nick%3D%25E8%2596%2587%25E8%2596%2587%25E5%25AE%2589tesdt%26fmp%3D%26lcp%3D; SUB=_2AkMkvmTRa8NlrAZTnPsRy2jqaoRH-jyXbGgnAn7uJhIyGxgf7lA2qSWaodrfwllEMB7afIieSvi9UX3i8w..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhSKYxYTuRj6ERRgG4V1qSq5JpX5KMt; ALF=1438916453; SSOLoginState=1407380454; _s_tentry=login.sina.com.cn; UOR=news.ifeng.com,widget.weibo.com,login.sina.com.cn; Apache=5174189445096.999.1407380457421; ULV=1407380457426:2:1:1:5174189445096.999.1407380457421:1405389915287; SWB=usrmd1196"

import requests
UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
LAN = 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': LAN,
    'User-Agent': UA,
}


cookies = dict((x.strip().split('=', 1)) for x in cookies_string.split(';'))
print cookies
s = requests.session()
r = s.get('http://weibo.com', headers=headers, allow_redirects=True, cookies=cookies)

with open('/home/xxr/test.html', 'wb') as f:
    f.write(r.content)

print list(r.cookies)
print list(s.cookies)
