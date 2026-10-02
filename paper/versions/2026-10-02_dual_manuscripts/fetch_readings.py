"""Fetch primary papers for local reading; never reads experimental data."""
from pathlib import Path
import json
import urllib.request
import subprocess

ROOT = Path(__file__).resolve().parent
DEST = ROOT.parents[2] / 'temp' / 'dual_manuscript_readings'
SOURCES = {
    'dror2018': 'https://aclanthology.org/P18-1128.pdf',
    'lin2011': 'https://aclanthology.org/P11-1052.pdf',
    'lostmiddle2024': 'https://aclanthology.org/2024.tacl-1.9.pdf',
    'hotpot2018': 'https://aclanthology.org/D18-1259.pdf',
    'musique2022': 'https://aclanthology.org/2022.tacl-1.31.pdf',
}
DEST.mkdir(parents=True, exist_ok=True)
records = []
for name, url in SOURCES.items():
    path = DEST / (name + '.pdf')
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(path), str(DEST/(name+'.txt'))], check=True)
    records.append({'id': name, 'url': url, 'text_path': str(DEST / (name+'.txt')), 'reading_status': 'DOWNLOADED_NOT_YET_READ'})
    print('Downloaded and extracted: '+name, flush=True)
print(json.dumps(records, indent=2))
