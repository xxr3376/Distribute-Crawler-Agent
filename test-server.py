from flask import Flask, request, jsonify
import agent

app = Flask(__name__)

@app.route('/', methods=['POST'])
def test():
    j = request.get_json(force=True)

    worker = agent.worker.Worker([], 10)
    headers = worker.generate_header()
    options = j.get('options', {})
    downloader_type = options.get('downloader', 'basic')
    if options.get('login', False):
        resource = options['resource']
        print resource
        name = options['source']
        cookies = agent.resource_manager.decode_cookies(resource)
        agent.resource_manager.__resource__ = {}
        agent.resource_manager.__resource__[name] = {
            "name": name,
            "error": False,
            "pool": [{
                "id": -1,
                "quota": 1000,
                "cookies": cookies,
            }]
        }
    downloader_config = {
        'basic': agent.basic_downloader.basic_downloader,
        'render': agent.render_downloader.render_downloader,
    }
    downloader = downloader_config[downloader_type]

    answer = downloader(j, headers, 10)
    return jsonify(**answer)

app.run(debug=True, host="0.0.0.0")
