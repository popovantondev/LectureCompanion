"""Package an explicitly prepared, verified portable runtime and just the two models.
No download/install, no source-workspace copy, no overwrite, no personal config.
"""
import argparse,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from portable_config import PORTABLE

def within(path,root):
    if not path.resolve().is_relative_to(root.resolve()):raise ValueError('Path outside selected directory: '+str(path))
    return path

def main():
    parser=argparse.ArgumentParser()
    for arg in ('app','runtime','models','output'):parser.add_argument('--'+arg,type=Path,required=True)
    parser.add_argument('--no-zip',action='store_true')
    parser.add_argument('--ollama-models',type=Path)
    args=parser.parse_args()
    for folder in (args.app,args.runtime,args.models):
        if not folder.is_dir():raise ValueError('Missing directory: '+str(folder))
    if args.output.suffix.lower()!='.zip':raise ValueError('--output must end in .zip')
    target=args.output.with_suffix('')
    if target.exists() or args.output.exists():raise ValueError('Output already exists. Use a new output name.')
    for relative in ('node/node.exe','python/python.exe','ollama/ollama.exe'):
        if not (args.runtime/relative).is_file():raise ValueError('Missing portable runtime: '+relative)
    python=args.runtime/'python/python.exe'
    if (python.parent/'pyvenv.cfg').exists():raise ValueError('A venv is not portable. Provide a standalone Python directory.')
    script="import sys,openvino,openvino_genai,json; print(json.dumps([sys.prefix,openvino.__file__,openvino_genai.__file__]))"
    result=subprocess.run([str(python),'-I','-c',script],capture_output=True,text=True,timeout=40,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),check=True)
    for location in json.loads(result.stdout.strip().splitlines()[-1]):within(Path(location),python.parent)
    model=args.models/'Qwen3-8B-int4-cw-ov'
    if not (model/'openvino_model.xml').exists():raise ValueError('OpenVINO model missing')
    ollama_root=args.ollama_models or args.models/'ollama'
    manifest=ollama_root/'manifests/registry.ollama.ai/library/qwen3-vl/2b-instruct'
    description=json.loads(manifest.read_text(encoding='utf-8'))
    blobs=[]
    for item in [description['config'],*description['layers']]:
        digest=item['digest']
        import re
        if not re.fullmatch(r'sha256:[a-f0-9]{64}',digest):raise ValueError('Invalid model digest')
        blob=ollama_root/'blobs'/digest.replace(':','-')
        if not blob.is_file():raise ValueError('Incomplete Ollama model: '+str(blob))
        blobs.append(blob)
    # Refuse app-local private data before copying the already built release.
    private={'local.json','state.json','ui-settings.json','device-benchmark.json','history-before-10.json','pet-position.json'}
    if any(p.name in private or p.suffix in ('.log','.jsonl') for p in args.app.rglob('*')):raise ValueError('App folder contains private runtime data')
    for folder in (args.app,args.runtime,model):
        for p in folder.rglob('*'):within(p,folder)
    print('Copying app...',flush=True)
    shutil.copytree(args.app,target)
    print('Copying standalone runtimes...',flush=True)
    shutil.copytree(args.runtime,target/'Laufzeit',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    print('Copying text model...',flush=True)
    shutil.copytree(model,target/'Modelle'/model.name,ignore=shutil.ignore_patterns('.git','.cache','cache-*'))
    print('Copying vision model...',flush=True)
    for source in [manifest,*blobs]:
        dest=target/'Modelle'/'ollama'/source.relative_to(ollama_root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    (target/'portable.json').write_text(json.dumps(PORTABLE,indent=2),encoding='utf-8')
    if args.no_zip:
        print('Portable folder:',target,flush=True);return
    with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
        for file in target.rglob('*'):
            if file.is_file():archive.write(file,str(Path(target.name)/file.relative_to(target)))
    print('Portable archive:',args.output)
    print('Extract the whole folder to an internal SSD. Test on a clean second Windows PC before distribution.')

if __name__=='__main__':main()
