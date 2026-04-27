import subprocess
import json
import os
import sys

def wasm_encrypt(request_data: dict, args1: str = "0") -> str:
    if getattr(sys, 'frozen', False):
        current_dir = sys._MEIPASS
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    encrypt_js_path = os.path.join(current_dir, 'encrypt.js')
    
    payload = json.dumps(request_data)
    
    result = subprocess.run(
        ['node', encrypt_js_path, payload, args1],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=current_dir
    )
    
    if result.returncode != 0:
        raise Exception(f"WASM Encryption failed: {result.stderr}")
        
    output = result.stdout
    if "ENCRYPTED:" in output:
        return output.split("ENCRYPTED:")[1].strip()
    else:
        raise Exception(f"WASM Encryption failed, unexpected output: {output}")
