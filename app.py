from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
import base64
import json
import os
from io import BytesIO

app = Flask(__name__)

def parse_env(env_content):
    """Parses .env content and converts it to a dictionary, supporting both '=' and ':' separators"""
    env_dict = {}
    for line in env_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):  # Ignore empty lines and comments
            continue
        
        # Support both '=' and ':' as separators
        if "=" in line:
            key, value = line.split("=", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            continue  # Skip lines without a valid separator
        
        key, value = key.strip(), value.strip().strip('"')
        env_dict[key] = base64.b64encode(value.encode()).decode()
    return env_dict

@app.route('/', methods=['GET', 'POST'])
def index():
    json_output = None
    file_download = None
    secret_name = ""
    namespace = ""
    
    if request.method == 'POST':
        env_content = request.form.get('env_content', '')
        secret_name = request.form.get('secret_name', 'my-secret')
        namespace = request.form.get('namespace', 'default')
        
        env_dict = parse_env(env_content)
        secret_json = {
            "kind": "Secret",
            "apiVersion": "v1",
            "metadata": {
                "name": secret_name,
                "namespace": namespace
            },
            "type": "Opaque",
            "data": env_dict
        }
        
        json_output = json.dumps(secret_json, indent=4)
        file_download = BytesIO(json_output.encode())
        file_download.seek(0)
        
    return render_template('index.html', json_output=json_output, secret_name=secret_name, namespace=namespace)

@app.route('/download', methods=['POST'])
def download():
    env_content = request.form.get('env_content', '')
    secret_name = secure_filename(request.form.get('secret_name', 'my-secret'))
    namespace = request.form.get('namespace', 'default')
    
    env_dict = parse_env(env_content)
    secret_json = {
        "kind": "Secret",
        "apiVersion": "v1",
        "metadata": {
            "name": secret_name,
            "namespace": namespace
        },
        "type": "Opaque",
        "data": env_dict
    }
    
    json_output = json.dumps(secret_json, indent=4)
    file_download = BytesIO(json_output.encode())
    file_download.seek(0)
    
    safe_filename = secure_filename(f"{secret_name}.json")
    return send_file(file_download, mimetype='application/json', as_attachment=True, download_name=safe_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
