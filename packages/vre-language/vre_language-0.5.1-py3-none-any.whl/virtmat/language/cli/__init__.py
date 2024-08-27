"""the main entry point for the virtmat language supporting tools"""
import argparse
from . import run_session
from . import run_model


def texts():
    """main function selecting one of the main modes - session or script"""
    parser = argparse.ArgumentParser(prog='texts')
    subparsers = parser.add_subparsers(help='Select the main mode', required=True,
                                       dest='session or script')
    help_i = 'Start an interactive session in workflow evaluation mode'
    parser_i = subparsers.add_parser(name='session',
                                     description='Start an interactive session',
                                     help=help_i)
    run_session.add_arguments(parser_i)
    parser_i.set_defaults(func=run_session.main)
    help_b = 'Run a script in instant, deferred or workflow evaluation mode'
    parser_b = subparsers.add_parser(name='script',
                                     description='Run a script',
                                     help=help_b)
    run_model.add_arguments(parser_b)
    parser_b.set_defaults(func=run_model.main)
    clargs = parser.parse_args()
    clargs.func(clargs)


if __name__ == '__main__':
    texts()
