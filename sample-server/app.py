from flask import Flask, jsonify, request
import uuid
import random


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
  queries = random.sample(queries, 3)

  data = {
      'status': 'OK',
      'id': uuid.uuid1().hex,
      'queries': queries,
      }
  return jsonify(data)

@app.route('/upload', methods=['POST'])
def upload():
  sum_md5 = request.form['md5']
  sum_sha1 = request.form['sha1']
  f = request.files['file']
  query_id = request.form['id']

  return 'OK'

app.run(port=8008, debug=True)
