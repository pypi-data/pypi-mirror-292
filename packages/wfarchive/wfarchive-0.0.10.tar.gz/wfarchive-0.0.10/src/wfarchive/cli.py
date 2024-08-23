from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from sys import argv, exit
from . import __about__
from .core import Archive, dlarchive

parser = ArgumentParser(allow_abbrev=False)
HELP_EXIST_OK = 'allow overwriting the destination path for all export options'
HELP_EXPORT_LOOSE_FILES = 'extract files from the archive and save them to `%(metavar)s`'
HELP_EXPORT_ARCHIVE = 'export the archive to `%(metavar)s`'
HELP_EXPORT_SIGNED_ARCHIVE = 'export the signed version of the archive to `%(metavar)s`'
DESC_NOTE = 'Note: If the target path argument for an export option is omitted, a default path will be automatically generated based on the provided positional arguments.'


def main():
    parser.add_argument('--version', '-v', action='version', version=f'wfarchive {__about__.__version__}')
    subparsers = parser.add_subparsers(required=True)

    parser_load = subparsers.add_parser('load', aliases=['l'], help=f'load an existing archive')
    parser_load.set_defaults(func=load)
    subparsers_load = parser_load.add_subparsers(required=True)

    parser_load_cloud = subparsers_load.add_parser('cloud', aliases=['c'], help='load an existing archive from cloud storage', description=DESC_NOTE)
    parser_load_cloud.set_defaults(cloud=True)
    parser_load_cloud.add_argument('wflow_id')
    parser_load_cloud.add_argument('--exist-ok', '-f', action='store_true', help=HELP_EXIST_OK)
    parser_load_cloud.add_argument('--export-loose-files', '-l', metavar='target_directory', nargs='?', action='append', help=HELP_EXPORT_LOOSE_FILES)
    parser_load_cloud.add_argument('--export-archive', '-a', metavar='target_file', nargs='?', action='append', help=HELP_EXPORT_ARCHIVE)
    parser_load_cloud.add_argument('--export-signed-archive', '-s', metavar='target_file', nargs='?', action='append', help=HELP_EXPORT_SIGNED_ARCHIVE)

    parser_load_local = subparsers_load.add_parser('local', aliases=['l'], help='load an existing archive from the local file system', description=DESC_NOTE)
    parser_load_local.set_defaults(cloud=False)
    parser_load_local.add_argument('archive_file')
    parser_load_local.add_argument('--exist-ok', '-f', action='store_true', help=HELP_EXIST_OK)
    parser_load_local.add_argument('--export-loose-files', '-l', metavar='target_directory', nargs='?', action='append', help=HELP_EXPORT_LOOSE_FILES)

    parser_new = subparsers.add_parser('new', aliases='n', help=f'create a new archive', description=DESC_NOTE)
    parser_new.set_defaults(func=new)
    parser_new.add_argument('source_file_or_directory')
    parser_new.add_argument('--exist-ok', '-f', action='store_true', help=HELP_EXIST_OK)
    parser_new.add_argument('--export-archive', '-a', metavar='target_file', nargs='?', action='append', help=HELP_EXPORT_ARCHIVE)
    parser_new.add_argument('--export-signed-archive', '-s', metavar='target_file', nargs='?', action='append', help=HELP_EXPORT_SIGNED_ARCHIVE)

    if len(argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        args.func(args)


def type_name(obj) -> str:
    return type.__getattribute__(type(obj), '__name__')


@contextmanager
def exc_handler():
    try:
        yield
    except Exception as e:
        exit(f'{parser.prog}: {type_name(e)}: {e}')


@exc_handler()
def load(args: Namespace):
    if args.cloud:
        archive = dlarchive(args.wflow_id)
    else:
        archive = Archive.load_from_path(args.archive_file)
    if args.export_archive:
        archive.export_archive(args.export_archive[-1], exist_ok=args.exist_ok)
    if args.export_signed_archive:
        archive.export_signed_archive(args.export_signed_archive[-1], exist_ok=args.exist_ok)
    if args.export_loose_files:
        archive.export_loose_files(args.export_loose_files[-1], exist_ok=args.exist_ok)


@exc_handler()
def new(args: Namespace):
    archive = Archive.new(args.source_file_or_directory)
    if args.export_archive:
        archive.export_archive(args.export_archive[-1], exist_ok=args.exist_ok)
    if args.export_signed_archive:
        archive.export_signed_archive(args.export_signed_archive[-1], exist_ok=args.exist_ok)
