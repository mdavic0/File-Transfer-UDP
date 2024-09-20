from lib.server import Server
from lib.arguments_parser import parse_arguments_server
from lib.log import prepare_logger
import logging
import sys

def main():
    try:
        arguments = parse_arguments_server()

        prepare_logger(arguments.loglevel)

        logging.info(
            "Starting server at IP: {} Port: {}. Storage directory: {}".format(arguments.host, arguments.port, arguments.storage))

        server = Server(arguments) #arguments.host, arguments.port, arguments.storage)
        server.start()
        
    except KeyboardInterrupt:
        logging.info("Server stopped")
        sys.exit(0)

if __name__ == '__main__':
    main()
