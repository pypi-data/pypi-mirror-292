from argparse import ArgumentParser
from agox.cli import parsers

def main():

    main_parser = ArgumentParser()
    subparsers = main_parser.add_subparsers(help='sub-command help')

    for add_parser in parsers:
        add_parser(subparsers)

    args = main_parser.parse_args()
    args.func(args)


