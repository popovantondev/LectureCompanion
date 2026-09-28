"""Finalize a tested Portable folder without its test/user state or device caches."""
import argparse,hashlib,json,zipfile
from pathlib import Path

PRIVATE={'Daten','data','__pycache__','.git','.cache'}
def allowed(relative):
    return not any(part in PRIVATE or part.startswith('cache-') for part in relative.parts) and relative.suffix not in ('.log','.pyc','.jsonl')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--folder',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=args.folder.resolve()
    if args.output.exists():raise ValueError('Use a new archive filename')
    for file in ('LectureCompanion.exe','portable.json','START_HIER.html','Laufzeit/python/python.exe','Laufzeit/node/node.exe','Laufzeit/ollama/ollama.exe'):
        if not (root/file).is_file():raise ValueError('Incomplete portable package: '+file)
    with zipfile.ZipFile(args.output,'x',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
        for file in sorted(root.rglob('*')):
            if not file.is_file():continue
            if not file.resolve().is_relative_to(root):raise ValueError('External link in release')
            relative=file.relative_to(root)
            if allowed(relative):archive.write(file,str(Path(root.name)/relative))
    digest=hashlib.sha256()
    with args.output.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
    args.output.with_suffix('.zip.sha256').write_text(digest.hexdigest()+'  '+args.output.name+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output) as archive:
        assert all(allowed(Path(info.filename).relative_to(root.name)) for info in archive.infolist())
        entries=len(archive.infolist());expanded=sum(i.file_size for i in archive.infolist())
    print(json.dumps({'archive':str(args.output),'entries':entries,'bytes':args.output.stat().st_size,'expandedBytes':expanded,'sha256':digest.hexdigest()}),flush=True)

if __name__=='__main__':main()
