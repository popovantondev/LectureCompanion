"""Prepare a relocatable Windows runtime from explicitly selected local installs.

Copies a base Python distribution + isolated model packages, not a broken venv.
Ollama includes CPU and Vulkan; CUDA/ROCm packs are deliberately not required.
Never downloads, overwrites an existing output or copies personal model history.
"""
import argparse,json,os,shutil,subprocess
from pathlib import Path

IGNORE=shutil.ignore_patterns('__pycache__','*.pyc','.cache')

def copy_tree(source,target):
    for item in source.rglob('*'):
        if not item.resolve().is_relative_to(source.resolve()):raise ValueError('External link: '+str(item))
    shutil.copytree(source,target,ignore=IGNORE)

def main():
    parser=argparse.ArgumentParser()
    for arg in ('python-base','packages','node','ollama','output'):parser.add_argument('--'+arg,type=Path,required=True)
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.output.exists() and not args.resume:raise ValueError('Choose a new output directory; existing files are never overwritten')
    if (args.python_base/'pyvenv.cfg').exists():raise ValueError('--python-base must not be a virtual environment')
    for file in (args.python_base/'python.exe',args.node,args.ollama/'ollama.exe'):
        if not file.is_file():raise ValueError('Missing runtime: '+str(file))
    if not (args.packages/'openvino_genai').is_dir():raise ValueError('OpenVINO GenAI packages missing')
    dest=args.output/'python';dest.mkdir(parents=True,exist_ok=True)
    if not (args.resume and (dest/'python312._pth').is_file()):
        print('Preparing standalone Python...',flush=True)
        for name in ('python.exe','pythonw.exe','python3.dll','python312.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt'):
            shutil.copy2(args.python_base/name,dest/name)
        copy_tree(args.python_base/'DLLs',dest/'DLLs')
        (dest/'Lib').mkdir()
        for item in (args.python_base/'Lib').iterdir():
            if item.name in ('site-packages','__pycache__','test','ensurepip'):continue
            if item.is_dir():copy_tree(item,dest/'Lib'/item.name)
            else:shutil.copy2(item,dest/'Lib'/item.name)
        print('Copying OpenVINO and its dependencies...',flush=True)
        copy_tree(args.packages,dest/'Lib/site-packages')
        # Explicit local import paths disable registry/user-site/PYTHONPATH lookup.
        (dest/'python312._pth').write_text('.\nLib\nDLLs\nLib/site-packages\nimport site\n',encoding='utf-8')
    print('Copying Node and Ollama CPU/Vulkan...',flush=True)
    node=args.output/'node';node.mkdir(exist_ok=True);shutil.copy2(args.node,node/'node.exe')
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    shutil.copy2(Path(__file__).parent/'licenses/Node-24.19.0-LICENSE',node/'LICENSE.txt')
    ollama=args.output/'ollama';ollama.mkdir(exist_ok=True);shutil.copy2(args.ollama/'ollama.exe',ollama/'ollama.exe')
    shutil.copy2(Path(__file__).parent/'licenses/Ollama-0.33.3-LICENSE',ollama/'LICENSE.txt')
    lib=ollama/'lib/ollama';lib.mkdir(parents=True,exist_ok=True)
    for item in (args.ollama/'lib/ollama').iterdir():
        if item.is_file():shutil.copy2(item,lib/item.name)
        elif item.name=='vulkan' and not (lib/item.name).exists():copy_tree(item,lib/item.name)
    env=os.environ.copy()
    env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
    env['PATH']=str(dest)+os.pathsep+str(Path(os.environ.get('SystemRoot','C:/Windows'))/'System32')
    script="import sys,openvino,openvino_genai,json;print(json.dumps({'prefix':sys.prefix,'ov':openvino.__file__,'genai':openvino_genai.__file__,'devices':openvino.Core().available_devices}))"
    result=subprocess.run([str(dest/'python.exe'),'-I','-c',script],env=env,capture_output=True,text=True,timeout=90,check=True,creationflags=flags)
    info=json.loads(result.stdout.strip().splitlines()[-1])
    for key in ('prefix','ov','genai'):
        if not Path(info[key]).resolve().is_relative_to(dest.resolve()):raise RuntimeError('Runtime depends on another Python installation')
    (args.output/'runtime-verification.json').write_text(json.dumps({'python':'3.12','openvino':'2026.3.1','isolatedImports':True,'visionBackends':['CPU','Vulkan']},indent=2),encoding='utf-8')
    print('Standalone runtime verified; devices:',info['devices'],flush=True)
    print('Runtime MiB:',round(sum(p.stat().st_size for p in args.output.rglob('*') if p.is_file())/1024**2,1),flush=True)

if __name__=='__main__':main()
