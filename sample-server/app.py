from flask import Flask, jsonify, request
import uuid
import random
import time
import hashlib

app = Flask(__name__)

@app.route('/manager/register', methods=['POST'])
def register():
    j = request.get_json(force=True)
    print j
    action = {
        'type': 'start_agent',
        'data': 'sdlkfjaslfksajflkasflkas',
    }
    return jsonify(status='OK', actions=[action])

@app.route('/manager/heartbeat', methods=['POST'])
def heartbeat():
    j = request.get_json(force=True)
    print j
    action = {
        'type': 'stop_agent',
        'data': 'sdlkfjaslfksajflkasflkas',
    }
    return jsonify(status='OK', actions=[action])

@app.route('/info')
def info():
  data = {
      'control_server': ['http://localhost:8008/control'],
      'upload_server': ['http://localhost:8008/upload'],
      'get_resource': ['http://localhost:8008/get_resource'],
      }
  return jsonify(data)

@app.route('/control')
def control():
  with open('/home/xxr/url.list') as f:
      queries = map(lambda x: {'url': x, 'need_login': True, 'resource': 'weibo'}, filter(lambda x: x, map(lambda x: x.strip(), f.readlines())))
  queries = random.sample(queries, 3)

  data = {
      'status': 'OK',
      'id': uuid.uuid1().hex,
      'queries': queries,
      }
  return jsonify(data)

@app.route('/upload', methods=['POST'])
def upload():
  sum_md5 = request.form['md5_checksum']
  sum_sha1 = request.form['sha1_checksum']
  f = request.files['file']

  query_id = request.form['id']

  filename = '/home/xxr/ddd/%s.gz' % uuid.uuid1().hex
  f.save(filename)
  f.seek(0)

  md5 = hashlib.md5()
  sha1 = hashlib.sha1()

  string = f.read()
  md5.update(string)
  sha1.update(string)
  if md5.hexdigest() != sum_md5 or sha1.hexdigest() != sum_sha1:
    print md5.hexdigest(), sum_md5
    print sha1.hexdigest(), sum_sha1
    print 'checksum is not right'
    raise Exception()
  print query_id, filename

  return 'OK'

@app.route('/get_resource')
def get_resource():
    cookies = 'SINAGLOBAL=1626578483264.8933.1405389915226; __utma=15428400.1879566305.1405475927.1405475927.1405475927.1; __utmz=15428400.1405475927.1.1.utmcsr=weibo.com|utmccn=(referral)|utmcmd=referral|utmcct=/u/5200297795/home; __gads=ID=c3e4428bd8078662:T=1405516288:S=ALNI_MbLjCDvMGInBrdQ-oTqqlxfB72Z3w; myuid=5242355424; wvr=5; SUS=SID-5243473869-1407380454-GZ-mtfck-d5e4d365a9aab95bc1e88a1bb0d0af49; SUE=es%3D5bbfafea5502a3651ce28d74083c60fd%26ev%3Dv1%26es2%3D08762bd1ab7e849dda101b2dec145db6%26rs0%3DDVttXZYUAlihdZtdR2n4swpJDVjhSND%252BblB0UwlZKtYcJycBh6I%252FRr78LOmj2QYPxHDHKy%252BsS3K2Wh3GkQsBbd4US9aQ6fN3EdMJKzEQeyFlyvBCVvneBDlWFpdqus4rqn6aZY%252BWKl7OdQeBmc06rnlh1uqC1FIqrVpyE2PVkjc%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1407380454%26et%3D1407466854%26d%3Dc909%26i%3Daf49%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D2%26st%3D0%26uid%3D5243473869%26name%3D1908639260%2540qq.com%26nick%3D%25E8%2596%2587%25E8%2596%2587%25E5%25AE%2589tesdt%26fmp%3D%26lcp%3D; SUB=_2AkMkvmTRa8NlrAZTnPsRy2jqaoRH-jyXbGgnAn7uJhIyGxgf7lA2qSWaodrfwllEMB7afIieSvi9UX3i8w..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhSKYxYTuRj6ERRgG4V1qSq5JpX5KMt; ALF=1438916453; SSOLoginState=1407380454; _s_tentry=login.sina.com.cn; UOR=news.ifeng.com,widget.weibo.com,login.sina.com.cn; Apache=5174189445096.999.1407380457421; ULV=1407380457426:2:1:1:5174189445096.999.1407380457421:1405389915287; SWB=usrmd1196'
    time.sleep(3)
    return jsonify(rid='123', resource=cookies, status='OK', quota=5)

app.run(port=8008, debug=True)
