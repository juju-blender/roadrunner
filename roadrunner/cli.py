import argparse
from roadrunner import core, log


def setup_options(argv=None):
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-c', '--config', dest="cfgpath", metavar="FILE",
                        help="Configuration file")
    parser.add_argument('--loglevel', dest='loglevel', metavar='LEVEL',
                        default='INFO', help="Set logging level")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help='dry-run')

    return parser.parse_args(argv)


def main():
    opts = setup_options()
    log.setup_logging(level=opts.loglevel)
    def_set = core.DefinitionSet(opts.cfgpath)
    def_set.dry_run = opts.dry_run
    def_set.run()
