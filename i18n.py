"""Local UI translations, shared with the Node service. Never translate answer data."""
import json,os
from pathlib import Path

CATALOG=json.loads(Path(__file__).with_name('locales.json').read_text(encoding='utf-8'))
LANGUAGES=('de','en','ru')
language='de'

def set_language(value):
    global language
    language=value if value in LANGUAGES else 'de'
    os.environ['LECTURE_LANGUAGE']=language

def tr(text,lang=None):
    if not isinstance(text,str):return text
    selected=lang or language
    if text in CATALOG:return CATALOG[text].get(selected,text)
    for key in sorted(CATALOG,key=len,reverse=True):
        if len(key)>8 and text.startswith(key):return CATALOG[key].get(selected,key)+text[len(key):]
    return text
