from mtg_buddy import db
import logging


log = logging.getLogger()

def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s: %(message)s',
        datefmt='%H:%M:%S',
    )

    log.info("Validating DB")
    db.check_db()
    log.info("Validation succeded")

if __name__ == "__main__":
    main()