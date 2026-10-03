import gzip
import json
import logging
import os
import shutil
import tempfile

from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
DB_FILE = DATA_DIR / 'AllPrintings.sqlite'
META_FILE = DATA_DIR / 'Meta.json'

DB_URL = 'https://mtgjson.com/api/v5/AllPrintings.sqlite.gz'
META_URL = 'https://mtgjson.com/api/v5/Meta.json'
TIMEOUT = 15

log = logging.getLogger(__name__)

def fetch_remote_meta() -> dict:
    response = requests.get(META_URL, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def read_local_meta() -> dict | None:
    if not META_FILE.exists():
        return None

    try:
        return json.loads(META_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        log.warning('Local Meta.json is corrupt, ignoring it')
        return None


def download_db() -> None:
    #Temp file lives in DATA_DIR so the final replace is an atomic rename on the same filesystem
    fd, tmp_name = tempfile.mkstemp(dir=DATA_DIR, suffix='.sqlite.tmp')
    os.close(fd)
    db_temp = Path(tmp_name)

    try:
        with requests.get(DB_URL, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()

            #Decompress while streaming so we never write the .gz to disk
            with gzip.GzipFile(fileobj=response.raw) as src, db_temp.open('wb') as dst:
                shutil.copyfileobj(src, dst, 1 << 20)

        db_temp.replace(DB_FILE)
    finally:
        db_temp.unlink(missing_ok=True)


def check_db() -> None:

    #Create data directory if it doesn't already exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        remote_meta = fetch_remote_meta()
    except requests.RequestException as e:
        if DB_FILE.exists():
            log.warning('Could not reach MTGJSON (%s), using local DB', e)
            return
        raise

    remote_version = remote_meta['meta']['version']
    local_meta = read_local_meta()

    if not DB_FILE.exists():
        log.info('No local DB found')
    elif local_meta is None:
        log.info('Missing Meta.json, cannot confirm DB version')
    elif local_meta['meta']['version'] != remote_version:
        log.info('DB is out of date (%s -> %s)', local_meta['meta']['version'], remote_version)
    else:
        log.info('DB is up to date (%s)', remote_version)
        return

    log.info('Downloading DB %s', remote_version)
    download_db()

    #Only record the new version once the DB has actually been swapped in
    META_FILE.write_text(json.dumps(remote_meta), encoding='utf-8')
    log.info('DB updated to %s', remote_version)