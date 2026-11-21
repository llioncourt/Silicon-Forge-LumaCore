#!/usr/bin/env python3
"""Offline synthetic test; this is NOT a genuine Photon Workshop print file."""
import json
from pathlib import Path
import tempfile
import zipfile
from sf_pwsz import W, H, iter_rle, encode_runs, inspect_rle, validate_archive, patch, selftest

base_layer, changed_layer=selftest()
with tempfile.TemporaryDirectory() as dirname:
    base=Path(dirname)
    original=base/'cupom_mock.pwsz'
    output=base/'cupom_mock_SF.pwsz'
    config={
      'machine_type':{'name':'Anycubic Photon Mono M7 Pro','res_x':W,'res_y':H,'print_xsize':223.64,'print_ysize':126.48},
      'machine_extern':{
        'active_resins':['Standard Resin'],
        'user_resins':[{'property':{'name':'Standard Resin','type':'Standard Resin','film_name':'ACF'},
                        'slicepara':{'exposure_time':1.8,'zthick':.05,'bott_time':25,'bott_layers':5},
                        'slice_extpara':{'transition_layercount':5}}]
      }
    }
    ctl={'count':80,'paras':[{'layer_index':i,'layer_thickness':.05,'exposure_time':25 if i<5 else 1.8} for i in range(80)]}
    with zipfile.ZipFile(original,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('anycubic_photon_resins.pwsp',json.dumps(config))
        z.writestr('layers_controller.conf',json.dumps(ctl))
        z.writestr('scene.slice','MOCK FILE - MUST NOT PRINT')
        z.writestr('print_info.json','{"cost":0.0,"currency":"USD","print_time":1,"volume":1.0}')
        for i in range(80):
            z.writestr(f'layer_images/layer_{i}.pw0Img',base_layer)
    inspect = validate_archive(original)
    inspect[0].close()
    patch(original,output)
    assert original.read_bytes()!=output.read_bytes()
    with zipfile.ZipFile(original) as before, zipfile.ZipFile(output) as after:
        assert before.read('layers_controller.conf')==after.read('layers_controller.conf')
        assert before.read('anycubic_photon_resins.pwsp')==after.read('anycubic_photon_resins.pwsp')
        assert before.read('layer_images/layer_0.pw0Img')==after.read('layer_images/layer_0.pw0Img')
        assert before.read('layer_images/layer_79.pw0Img')==after.read('layer_images/layer_79.pw0Img')
        actual=after.read('layer_images/layer_21.pw0Img')
        assert inspect_rle(base_layer)==inspect_rle(actual)
        assert {shade for _,_,shade in iter_rle(actual)}=={0,13,14,15}
    print('PASSOU: teste com PWSZ sintetico; nenhuma validacao firmware')
