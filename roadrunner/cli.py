import argparse


def setup_options(argv=None):
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-c', '--config', dest="cfgpath", metavar="FILE",
                        help="Configuration file")
    parser.add_argument('--loglevel', dest='loglevel', metavar='LEVEL',
                        help="Set logging level")

    return parser.parse_args(argv)


def main():
    opts = setup_options()
    setup_logging(level=opts.loglevel)
