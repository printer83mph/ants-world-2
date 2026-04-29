import logging
import time

from app.config import settings
from app.simulator import Simulator


def main():
    if settings.debug:
        logging.basicConfig(level=logging.DEBUG)

    sim = Simulator(redis_url=settings.redis_url)
    dt = settings.fixed_dt

    while True:
        sim.tick(dt)
        time.sleep(dt)


if __name__ == "__main__":
    main()
