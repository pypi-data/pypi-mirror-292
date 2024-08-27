def add_example_parser(subparsers):

    parser = subparsers.add_parser('example', help='Example of a CLI tool.')
    parser.set_defaults(func=cli_example)

    parser.add_argument('input', help='Example of positional argument')
    parser.add_argument('-o', '--optional', help='Example of optional argument', default='default value')

def cli_example(args):

    print('Input:', args.input)
    print('Optional:', args.optional)
    print('This is an example CLI')
    return 0


