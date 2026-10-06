import asyncio
from mtg_buddy import db, agents, tool
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
    chat()

def chat():
    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user:
            continue
        if user.lower() in {'quit', 'exit'}:
            break

        results = asyncio.run(agents.run_agent(user))

        print(results)
if __name__ == "__main__":
    main()