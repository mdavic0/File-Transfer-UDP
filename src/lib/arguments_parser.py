from argparse import ArgumentParser
import logging


def add_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO)
    group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING)

    parser.add_argument(
        "-H",
        "--host",
        type=str,
        required=True,
        help="service IP address")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="service port")


def parse_arguments_upload():
    parser = ArgumentParser(prog="Upload", description="Upload file")

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-sw",
        "--stopwait",
        action="store_const",
        dest="protocol",
        const=0)
    group.add_argument(
        "-sr",
        "--selectiverepeat",
        action="store_const",
        dest="protocol",
        const=1)

    add_arguments(parser)
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        required=True,
        help="source file path")
    parser.add_argument(
        "-d",
        "--dst",
        type=str,
        required=False,
        help="destination file path",
        default="")
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="file name")

    parser.add_argument(
        "-m",
        "--mininet",
        action="store_const",
        dest="mininet",
        const=1,
        default=0,
        help="running all hosts in mininet")
    return parser.parse_args()


def parse_arguments_download():
    parser = ArgumentParser(prog="Download", description="Download file")
    add_arguments(parser)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-sw",
        "--stopwait",
        action="store_const",
        dest="protocol",
        const=0)
    group.add_argument(
        "-sr",
        "--selectiverepeat",
        action="store_const",
        dest="protocol",
        const=1)

    parser.add_argument(
        "-d",
        "--dst",
        type=str,
        required=True,
        help="destination file path")
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        required=False,
        help="source file path",
        default="")
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="file name")

    parser.add_argument(
        "-m",
        "--mininet",
        action="store_const",
        dest="mininet",
        const=1,
        default=0,
        help="running all hosts in mininet")
    return parser.parse_args()


def parse_arguments_server():
    parser = ArgumentParser(prog="Server", description="Server")
    add_arguments(parser)
    parser.add_argument(
        "-s",
        "--storage",
        type=str,
        required=True,
        help="storage dir path")
    return parser.parse_args()
