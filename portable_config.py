"""Resolve a portable bundle before machine-specific paths. Never copy user profiles."""
import json,os
from pathlib import Path

PORTABLE={
 'node':'Laufzeit/node/node.exe','npu_python':'Laufzeit/python/python.exe',
 'ollama':'Laufzeit/ollama/ollama.exe','model_root':'Modelle','ollama_models':'Modelle/ollama'
}

def resolve_paths(config,base):
    resolved=dict(config)
    for key in PORTABLE:
        value=config.get(key)
        if not value:continue
        path=Path(os.path.expandvars(value))
        resolved[key]=str((base/path).resolve()) if not path.is_absolute() else str(path)
    return resolved

def load_config(bundle,data):
    portable=bundle/'portable.json'
    if portable.is_file():
        return resolve_paths(json.loads(portable.read_text(encoding='utf-8-sig')),bundle)
    # A complete standard layout needs no personal config file at all.
    if all((bundle/PORTABLE[k]).exists() for k in ('node','npu_python','model_root')):
        return resolve_paths(PORTABLE,bundle)
    for file in (data/'local.json',bundle/'local.json'):
        if file.is_file():return resolve_paths(json.loads(file.read_text(encoding='utf-8-sig')),file.parent)
    raise FileNotFoundError('local.json')
