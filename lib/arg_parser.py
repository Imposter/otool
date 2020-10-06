# Copyright (c) 2020 Mivade. All rights reserved.
# Available at: https://gist.github.com/mivade/384c2c41c3a29c637cb6c603d4197f9f
import argparse

parser = argparse.ArgumentParser()
sub_parser = parser.add_subparsers(dest="command")

def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    return (list(name_or_flags), kwargs)

def subcommand(command=None, description=None, args=None):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py command -d
    """
    args = args or list()
    def decorator(func):
        name = command or func.__name__
        desc = description or func.__doc__
        parser = sub_parser.add_parser(name, description=desc)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

    