#!/usr/bin/env python3
"""Local config launcher. Does not modify the original PNG folder."""
import json
from pathlib import Path
from argparse import Namespace
from sf_optical_masker import process_folder
root=Path(__file__).resolve().parent
cfg=json.loads((root/'config.json').read_text(encoding='utf8'))
for key in ('input_dir','output_dir'):
    p=Path(cfg[key]);cfg[key]=str((root/p).resolve()) if not p.is_absolute() else str(p)
Path(cfg['input_dir']).mkdir(exist_ok=True,parents=True)
Path(cfg['output_dir']).mkdir(exist_ok=True,parents=True)
print('SILICON FORGE EXPERIMENTAL GRAYSCALE | NOT READY FOR PRINTING',flush=True)
process_folder(Namespace(**cfg))
