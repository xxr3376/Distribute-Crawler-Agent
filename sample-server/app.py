from flask import Flask, jsonify, request
import uuid
import random
import hashlib
import zlib


app = Flask(__name__)

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
  queries = random.sample(queries, 1)

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

  filename = '/home/xxr/ddd/%s.json' % uuid.uuid1().hex
  md5 = hashlib.md5()
  sha1 = hashlib.sha1()

  string = f.read()
  md5.update(string)
  sha1.update(string)
  if md5.hexdigest() != sum_md5 or sha1.hexdigest() != sum_sha1:
    print 'checksum is not right'
    raise Exception()
  with open(filename, 'wb') as output:
    output.write(zlib.decompress(string))
  print query_id, filename

  return 'OK'

app.run(port=8008, debug=True)
