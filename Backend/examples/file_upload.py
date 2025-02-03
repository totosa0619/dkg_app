import base64
import re
import requests

root = "/Users/noname/Desktop/invest-moldova/files"
fpath = "/Users/noname/Desktop/invest-moldova/invest-in-moldova-feb-18.json"
res_fname = "invest-in-moldova-v2-feb-18.json"
rxp = "(data:image.+\")(?!$)"
server = "https://tools.dkv.global"
token = "tnk_1"
# server = "http://localhost:8000"
# token = "tkn_2"

data = {}

with open(fpath, "r") as f:
    config = f.read()
    r = re.findall(rxp, config)
    for idx, img in enumerate(r):
        img_data = img[:-1].replace("data:image/", "")
        (ext, b64data) = img_data.split(";")
        b64data = b64data.replace("base64,", "")
        fname = f"{root}/file_{idx}.{ext}"
        data[img] = fname
        with open(fname, "wb+") as img_file:
            img_file.write(base64.b64decode(b64data))

    for b64data, fname in data.items():
        files = {"files": open(fname, 'rb')}
        r = requests.post(f"{server}/api/files", files=files, headers={
            'Authorization': f'Token {token}',
        })
        furl = r.json()[0]["url"]
        config = config.replace(b64data, f"{furl}\"")

    with open(f'{root}/{res_fname}', 'w') as newf:
        newf.write(config)

# upload data
# replace in file
