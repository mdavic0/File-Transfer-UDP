from lib.client import Client
from lib.arguments_parser import parse_arguments_download
from lib.log import prepare_logger
import logging
import sys
from lib.exceptions import *

def main():
    try:
        arguments = parse_arguments_download()

        prepare_logger(arguments.loglevel)
        
        logging.info(
            "Starting client at server IP: {} Port: {}. Destination file path: {}. File name: {}".format(
                arguments.host, arguments.port, arguments.dst, arguments.name
            )
        )

        client = Client(arguments) #.host, arguments.port, arguments.dst, arguments.name)

        try:
            client.download()
        except KeyboardInterrupt:
            logging.info("Client stopped")
            sys.exit(0)
        except ConnectionFailedError:
            logging.error("Couldn't establish connection to server")
            sys.exit(0)
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
