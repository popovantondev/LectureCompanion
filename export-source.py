"""Export only reviewed source files. No git init/push and no private data copy."""
import argparse,json,re,zipfile,hashlib
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).parent
    manifest=json.loads((root/'release-manifest.json').read_text(encoding='utf-8'))
    if args.output.exists():raise ValueError('Output exists; use a new name')
    files=[]
    for relative in manifest['sourceFiles']:
        path=(root/relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():raise ValueError('Invalid/missing source: '+relative)
        if path.suffix in ('.py','.pyw','.js','.ps1','.json','.md','.html'):
            content=path.read_text(encoding='utf-8-sig')
            # A real Windows account path, not generic LOCALAPPDATA documentation.
            if re.search(r'[A-Z]:[\\/]+Users[\\/]+(?!Public|Example|<)',content,re.I):raise ValueError('Personal path in '+relative)
        files.append((relative,path))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'x',zipfile.ZIP_DEFLATED) as archive:
        for relative,path in files:archive.write(path,'LectureCompanion-2.4-Source/'+relative)
    digest=hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix('.zip.sha256').write_text(digest+'  '+args.output.name+'\n',encoding='utf-8')
    print('Source archive:',args.output,'files:',len(files))

if __name__=='__main__':main()

