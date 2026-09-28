"""Hardware-independent fallback scenarios; does not load or benchmark a real model."""
import json,tempfile,sys,types
from pathlib import Path
from unittest.mock import patch
import device_runtime as runtime

with tempfile.TemporaryDirectory(prefix='lecture-device-test-') as temporary:
    root=Path(temporary);model=root/'Qwen3-8B-int4-cw-ov';model.mkdir();(model/'openvino_model.xml').write_text('test')
    class Core:
        available_devices=['CPU','GPU.0']
        def get_property(self,d,k):return d+k
    loaded=[]
    def pipeline(model,device,config):loaded.append(device);return object()
    ov=types.SimpleNamespace(Core=Core,__version__='test')
    genai=types.SimpleNamespace(LLMPipeline=pipeline)
    def probe(device,root):return {'ok':True,'device':device,'seconds':4 if device=='CPU' else 2}
    with patch.dict(sys.modules,{'openvino':ov,'openvino_genai':genai}),patch.object(runtime,'data_dir',lambda:root),patch.object(runtime,'probe',side_effect=probe) as bench:
        _,device,info=runtime.select_pipeline(root)
        assert device=='GPU.0' and bench.call_count==2 and loaded==['GPU.0']
        runtime.select_pipeline(root);assert bench.call_count==2,'Do not repeat cached benchmark'
        Core.available_devices=['CPU'];_,device,_=runtime.select_pipeline(root);assert device=='CPU'
        assert runtime.options('CPU',root)['INFERENCE_NUM_THREADS']<=4
        Core.available_devices=['NPU','CPU'];_,device,_=runtime.select_pipeline(root);assert device=='NPU'
        def broken_npu(model,device,config):
            if device=='NPU':raise RuntimeError('driver failed')
            return object()
        genai.LLMPipeline=broken_npu;_,device,_=runtime.select_pipeline(root);assert device=='CPU'
        Core.available_devices=['CPU','GPU.0']
        with patch.object(runtime,'probe',return_value={'ok':False,'device':'CPU','error':'timeout'}):
            # Force a different fingerprint so a successful old result is not reused.
            (model/'changed.json').write_text('{}')
            try:runtime.select_pipeline(root);raise AssertionError('Failure must not be labelled success')
            except RuntimeError as e:assert 'benchmark failed' in str(e)
print('PASS: no-NPU CPU/GPU ranking, cache, hardware invalidation, CPU-only, NPU preference/driver fallback, failed benchmark.')
