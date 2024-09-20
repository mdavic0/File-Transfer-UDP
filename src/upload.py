import logging
import sys
import traceback
from lib.exceptions import *
from lib.client import Client
from lib.arguments_parser import parse_arguments_upload
from lib.log import prepare_logger

def main():
    try:
        arguments = parse_arguments_upload()

        prepare_logger(arguments.loglevel)

        logging.info(
            f"Starting client at server IP: {arguments.host} Port: {arguments.port}. Source file path: {arguments.src}. File name: {arguments.name}. Protocol: {arguments.protocol}"
        )

        client = Client(arguments) #.host, arguments.port, arguments.dst, arguments.name)

        try: 
            client.upload()
        except KeyboardInterrupt:
            logging.info("Client stopped")
            sys.exit(0)
        except ConnectionFailedError:
            logging.error("Couldn't establish connection to server")
            sys.exit(0)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
