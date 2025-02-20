from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
import base64
import re
import json
import os
from io import BytesIO

app = Flask(__name__)

def parse_env(env_content):
    """Parses .env content and converts it to a dictionary using regex, ensuring correct key-value extraction."""
    env_dict = {}
    
    # Regex pattern to extract key-value pairs
    pattern = re.compile(r'([^:\s]+):\s*"([^"]+)"')

    for match in pattern.finditer(env_content):
        key = match.group(1).strip()  # Extract key
        value = match.group(2).strip()  # Extract value inside quotes

        # Ensure Base64 encoding for all extracted values
        encoded_value = base64.b64encode(value.encode()).decode()
        env_dict[key] = encoded_value

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
    secret_name = secure_filename(request.form.get('secret_name', 'my-secret'))  # Sanitize the secret name
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

    # Ensure the filename is safe
    safe_filename = secure_filename(f"{secret_name}.json")
    return send_file(file_download, mimetype='application/json', as_attachment=True, download_name=safe_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
