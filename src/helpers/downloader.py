import requests
from pathlib import Path


def download_to_loacl(url:str, out_path:Path, parent_mkdir:bool=True):
    if not isinstance(out_path, Path):
        raise ValueError('Somthing went wrong')
    if parent_mkdir:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url)
        response.raise_for_status()

        out_path.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        print('Failed to download')
        return False