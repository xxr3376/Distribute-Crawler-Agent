from flask import Flask, request, jsonify
import agent

app = Flask(__name__)

@app.route('/', methods=['POST'])
def test():
    j = request.get_json(force=True)
    worker = agent.worker.Worker([], 10)
    headers = worker.generate_header()
    answer = agent.downloader.basic_downloader(j, headers, 10)
    return jsonify(**answer)


app.run(debug=True, host="0.0.0.0")
