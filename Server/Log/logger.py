import logging

# config log system
format = "%(asctime)s: %(message)s" 
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

def warn(msg):
    logging.warn(msg)

def info(msg):
    logging.info(msg)

def error(msg):
    logging.error(msg)