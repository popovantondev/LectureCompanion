"""Fast, model-free checks; native UI is opt-in and Windows only."""
import argparse,ast,json,os,shutil,subprocess,sys
from pathlib import Path
from html.parser import HTMLParser

class GuideImages(HTMLParser):
    def __init__(self):super().__init__();self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img':self.sources.append(dict(attrs).get('src',''))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--node',default=shutil.which('node'));parser.add_argument('--ui',action='store_true')
    args=parser.parse_args();root=Path(__file__).parent
    if not args.node:raise RuntimeError('Node.js required for developer tests (--node PATH)')
    manifest=json.loads((root/'release-manifest.json').read_text(encoding='utf-8'))
    assert manifest['version']==json.loads((root/'version.json').read_text())['version']=='2.4'
    for name in manifest['appDocuments']:
        if name.endswith('.html'):
            page=GuideImages();page.feed((root/name).read_text(encoding='utf-8'))
            for source in page.sources:
                if source.startswith(('https://','http://','data:')):continue
                assert (root/name).parent.joinpath(source).is_file(),'Missing guide image: '+name
    for name in manifest['sourceFiles']:
        assert (root/name).is_file(),'Missing release source: '+name
        assert (root/name).resolve().is_relative_to(root.resolve())
        assert Path(name).name not in ('local.json','state.json','device-benchmark.json','ui-settings.json')
        if name.endswith(('.py','.pyw')):ast.parse((root/name).read_text(encoding='utf-8-sig'),filename=name)
        elif name.endswith('.js'):subprocess.run([args.node,'--check',name],cwd=root,check=True,timeout=20)
    catalog=json.loads((root/'locales.json').read_text(encoding='utf-8'))
    assert all(all(row.get(lang) for lang in ('de','en','ru')) for row in catalog.values())
    for name in ['test-server-routes.js','test-lecture-language.js','test-live.js','test-freshness.js','test-vision-queue.js','test-response-modes.js','test-languages.js','test-vision-languages.js']:
        subprocess.run([args.node,name],cwd=root,check=True,timeout=30)
    for name in ['test-device-selection.py','test-portable-config.py']:
        subprocess.run([sys.executable,'-B',name],cwd=root,check=True,timeout=30)
    if args.ui:
        if os.name!='nt':raise RuntimeError('Native UI tests require Windows')
        for name in ['test-ui-deck.py','test-loading-sound.py']:
            subprocess.run([sys.executable,'-B',name],cwd=root,check=True,timeout=180)
    print('PASS: release manifest, syntax, localization and all selected model-free tests.')

if __name__=='__main__':main()
