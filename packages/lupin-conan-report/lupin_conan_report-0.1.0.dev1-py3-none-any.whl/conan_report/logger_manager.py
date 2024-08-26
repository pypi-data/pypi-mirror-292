import logging


def configure_logger():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def die(message: str) -> None:
    logging.error(message)
    exit(1)
