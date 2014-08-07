from flask import Flask, jsonify, request
import uuid
import random
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
      }
  return jsonify(data)

@app.route('/control')
def control():
  with open('/home/xxr/url.list') as f:
    queries = map(lambda x: {'url': x}, filter(lambda x: x, map(lambda x: x.strip(), f.readlines())))
  queries = random.sample(queries, 30)

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

  filename = '/home/xxr/ddd/%s.tar.gz' % uuid.uuid1().hex
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

app.run(port=8008, debug=True)
