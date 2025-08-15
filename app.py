from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
import base64
import re
import json
import os
from io import BytesIO

app = Flask(__name__)

def parse_env(env_content):
    """Parses .env content and converts it to a dictionary supporting multiple formats.
    
    Supported formats:
    - KEY=value
    - KEY="value"
    - KEY='value'
    - KEY: value
    - KEY: "value"
    - KEY: 'value'
    - Comments with # (ignored)
    - Empty lines (ignored)
    - Empty values (KEY= or KEY:)
    """
    env_dict = {}
    errors = []
    
    # Split content into lines for better error reporting
    lines = env_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Strip whitespace
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Remove inline comments (but preserve # in quoted values)
        cleaned_line = _remove_inline_comments(line)
        if not cleaned_line.strip():
            continue
            
        # Try to parse the line
        try:
            key, value = _parse_env_line(cleaned_line)
            if key:
                # Validate Kubernetes secret key naming
                if not _is_valid_k8s_key(key):
                    errors.append(f"Line {line_num}: Invalid Kubernetes secret key '{key}'. Keys must contain only alphanumeric characters, '.', '-', and '_'")
                    continue
                    
                # Base64 encode the value
                encoded_value = base64.b64encode(value.encode('utf-8')).decode('ascii')
                env_dict[key] = encoded_value
        except ValueError as e:
            errors.append(f"Line {line_num}: {str(e)} - '{line}'")
            continue
    
    # If we have errors but also some successful parses, we can still proceed
    # Store errors for potential logging/debugging
    if errors:
        # For now, we'll just continue - could add error reporting later
        pass
        
    return env_dict


def _remove_inline_comments(line):
    """Remove inline comments while preserving # inside quoted strings."""
    in_single_quote = False
    in_double_quote = False
    escaped = False
    
    result = []
    
    for i, char in enumerate(line):
        if escaped:
            result.append(char)
            escaped = False
            continue
            
        if char == '\\':
            escaped = True
            result.append(char)
            continue
            
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '#' and not in_single_quote and not in_double_quote:
            # Found unquoted comment, truncate here
            break
            
        result.append(char)
    
    return ''.join(result)


def _parse_env_line(line):
    """Parse a single environment variable line.
    
    Returns tuple of (key, value) or raises ValueError if invalid.
    """
    # Patterns to try in order of preference
    patterns = [
        # KEY="value" or KEY='value'
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\']([^"\']*)["\']\s*$',
        # KEY=value (unquoted)
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s#].*?)\s*$',
        # KEY= (empty value)
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*$',
        # KEY: "value" or KEY: 'value'
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*["\']([^"\']*)["\']\s*$',
        # KEY: value (unquoted)
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^\s#].*?)\s*$',
        # KEY: (empty value)
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else ""
            return key, value
    
    # If no pattern matches, it's an invalid line
    raise ValueError(f"Invalid environment variable format")


def _is_valid_k8s_key(key):
    """Validate that the key conforms to Kubernetes secret key requirements.
    
    Keys must:
    - Start with alphanumeric or underscore
    - Contain only alphanumeric, '.', '-', and '_'
    - Not be empty
    """
    if not key:
        return False
    
    # Kubernetes allows alphanumeric, '.', '-', and '_'
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, key))

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
