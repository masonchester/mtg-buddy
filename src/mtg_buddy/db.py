import pathlib as pt
import sqlite3 as sql
import requests as rq
import logging
import gzip
import tempfile
import hashlib


db_path = pt.Path.cwd() / 'data/'
db_file = db_path / 'AllPrintings.sqlite'

url = 'https://mtgjson.com/api/v5/AllPrintings.sqlite.gz'

logging_file = '/var/log/mtg-buddy.log'

logging.basicConfig(filename=logging_file, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

def check_db():

    if not pt.Path(db_path).exists(follow_symlinks=False):
        logging.info('Creating data dir')
        pt.Path.mkdir(db_path)
        logging.info('Data dir created successfully')

    if not pt.Path(db_file).exists(follow_symlinks=False):
        download_db()

    is_db_outdated()

def download_db():
    
    response = rq.get(url)
    
    if(response.status_code == 200):
        with open(db_file, "wb") as file:
            file.write(gzip.decompress(response.content))
        logging.info("DB file sucessfully downloaded")
    else:
        logging.info('Failed to download DB file. Status Code:', response.status_code)

def is_db_outdated():

    response = rq.get(url + '.sha256')
        
    if(response.status_code == 200):
        with tempfile.TemporaryFile() as temp:
            temp.write(response.content)

            logging.info("Sucessfully downloaded checksum")

            downloded_checksum = temp.read()

            with open(db_file, 'rb') as file:
                current_checksum = hashlib.file_digest(file, "sha256").hexdigest()

            if downloded_checksum != current_checksum:
                logging.info('DB is outdated redownloading')
                download_db()

        logging.info("DB is up to date")
    else:
        logging.info('Failed to download checksum file. Status Code:', response.status_code)
    