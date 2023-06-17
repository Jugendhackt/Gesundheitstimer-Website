import logging

# Logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "[%(asctime)s] [%(module)s/%(levelname)s]: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
log.addHandler(console_handler)
