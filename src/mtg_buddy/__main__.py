import db
import logging

logging_file = '/var/log/mtg-buddy.log'

def main():
    logging.basicConfig(filename=logging_file, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)    
    
    logging.info("Validating DB")
    db.check_db()
    logging.info("Validation succeded")


if __name__ == "__main__":
    main()