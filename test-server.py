from flask import Flask, request, jsonify
import agent

app = Flask(__name__)

@app.route('/', methods=['POST'])
def test():
    j = request.get_json(force=True)
    worker = agent.worker.Worker([], 10)
    headers = worker.generate_header()
    downloader_type = j.get('options', {}).get('downloader', 'basic')

    downloader_config = {
        'basic': agent.basic_downloader.basic_downloader,
        'render': agent.render_downloader.render_downloader,
    }
    downloader = downloader_config[downloader_type]

    answer = downloader(j, headers, 10)
    return jsonify(**answer)


app.run(debug=True, host="0.0.0.0", threaded=True)
