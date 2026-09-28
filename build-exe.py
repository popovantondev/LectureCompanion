"""Build the small UI bundle. Does not bundle Node, Ollama, OpenVINO or model weights."""
import argparse
import json
import importlib.metadata
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).parent/'dist')
    args=parser.parse_args();source=Path(__file__).parent;work=args.output.parent/'build-exe-work'
    work.mkdir(parents=True,exist_ok=True)
    icon=work/'companion.ico'
    with Image.open(source/'assets'/'companion.png') as image:
        image.save(icon,format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    version_file=work/'windows-version.txt'
    version_file.write_text("VSVersionInfo(ffi=FixedFileInfo(filevers=(2,4,0,0),prodvers=(2,4,0,0),mask=0x3f,flags=0,OS=0x40004,fileType=1,subtype=0,date=(0,0)),kids=[StringFileInfo([StringTable('040904B0',[StringStruct('FileDescription','Lecture Companion Portable'),StringStruct('FileVersion','2.4'),StringStruct('ProductName','Lecture Companion'),StringStruct('ProductVersion','2.4'),StringStruct('OriginalFilename','LectureCompanion.exe')])]),VarFileInfo([VarStruct('Translation',[1033,1200])])])",encoding='utf-8')
    command=[sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--windowed','--name','LectureCompanion','--icon',str(icon),
        '--version-file',str(version_file),'--distpath',str(args.output),'--workpath',str(work/'pyinstaller'),'--specpath',str(work),
        '--exclude-module','numpy','--exclude-module','matplotlib','--exclude-module','torch','--exclude-module','scipy']
    manifest=json.loads((source/'release-manifest.json').read_text(encoding='utf-8'))
    for name in manifest['appDataFiles']+manifest['appDocuments']:
        file=source/name
        destination=str(Path(name).parent)
        command+=['--add-data',str(file)+';'+destination]
    command+=['--add-data',str(source/'assets')+';assets',str(source/'launch.py')]
    subprocess.run(command,cwd=source,check=True)
    target=args.output/'LectureCompanion'
    # A double-clickable synthetic demo, no terminal or model services required.
    shutil.copy2(target/'LectureCompanion.exe',target/'LectureCompanionDemo.exe')
    for name in manifest['appDocuments']+['portable.example.json','version.json']:
        destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source/name,destination)
    # Retain dependency notices in the frozen UI as well as the external runtimes.
    notices=target/'_internal'/'licenses';notices.mkdir(parents=True,exist_ok=True)
    for package in ('Pillow','pyinstaller'):
        distribution=importlib.metadata.distribution(package)
        for file in distribution.files or []:
            if 'license' in str(file).lower() or str(file).lower().endswith('copying.txt'):
                original=distribution.locate_file(file)
                if original.is_file():shutil.copy2(original,notices/(package+'-'+original.name))
    print('EXE:',target/'LectureCompanion.exe')
    print('Bundle MiB:',round(sum(p.stat().st_size for p in target.rglob('*') if p.is_file())/1024**2,1))

if __name__=='__main__':main()
