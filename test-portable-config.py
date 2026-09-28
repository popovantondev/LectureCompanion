import json,tempfile
from pathlib import Path
from portable_config import load_config,PORTABLE
with tempfile.TemporaryDirectory(prefix='lecture-portable-test-') as temporary:
    root=Path(temporary);bundle=root/'Folder with spaces';bundle.mkdir();data=root/'old-profile';data.mkdir()
    (data/'local.json').write_text(json.dumps({'node':'old/node.exe','model_root':'old-models'}))
    (bundle/'portable.json').write_text(json.dumps(PORTABLE))
    config=load_config(bundle,data)
    for key,relative in PORTABLE.items():assert Path(config[key])==(bundle/relative).resolve()
    assert config['node']!=str(data/'old/node.exe'),'Portable must override machine-specific paths'
    (bundle/'portable.json').unlink()
    for key in ('node','npu_python','model_root'):
        path=bundle/PORTABLE[key]
        if key=='model_root':path.mkdir(parents=True)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text('')
    assert load_config(bundle,data)['model_root']==str((bundle/'Modelle').resolve())
print('PASS: relative portable paths, spaces, automatic layout, no old-account configuration dependency.')

