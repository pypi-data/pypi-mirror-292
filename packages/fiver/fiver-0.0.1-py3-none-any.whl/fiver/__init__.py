import argparse

import questionary
from .utils import SubcommandHelpFormatter
from .version import print_version
from .server import server_app
from .client import client_app


def cli_entry_point():
    parser = argparse.ArgumentParser(description="fiver - Fiver command line interface",  usage="fiver command [arguments...]", formatter_class=SubcommandHelpFormatter)
    parser._positionals.title = "commands"
    parser.add_argument('-v', '--version', action='store_true', help='print the version')

    subparsers = parser.add_subparsers()
    connect = subparsers.add_parser('connect', help='connect to server', usage='fiver connect')
    connect.add_argument('connect', nargs='?', type=bool, default=True, help='connect to server')

    server = subparsers.add_parser('server', help='start server', usage='fiver server debug,start,status,stop')
    server.add_argument('server', nargs='?', type=str, choices=['debug', 'start', 'status', 'stop', ], default="status", help='server manager')
   
    args = parser.parse_args()
    if args.version:
        print_version()
    elif getattr(args, 'connect', None):
        address = questionary.text("Enter my ip server (Ex: 127.0.0.10:10000):").ask()
        client_app(address)
    elif getattr(args, 'server', None):
        server_app(args.server)
    else:
        parser.print_help()
