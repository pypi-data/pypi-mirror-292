import plistlib
from . import templates, typing
from os import makedirs, scandir
from os.path import basename, exists, isfile, join, splitext
from platform import system
from requests import get
from subprocess import CompletedProcess, run
from typing import Literal, overload, Optional, Protocol, TypeVar

T = TypeVar('T', str, bytes)


class SupportsRead(Protocol[T]):
    def read(self) -> T:
        ...


class WFArchiveException(Exception):
    pass


class InvalidArchive(WFArchiveException):
    pass


class InvalidSchema(WFArchiveException):
    pass


class Archive:
    def __init__(self):
        self._archive_path: Optional[str] = None
        self._loose_files_path: Optional[str] = None
        self._alternative_name: Optional[str] = None
        self._schema: typing.Schema

    def _build_schema(self, path: str) -> typing.Schema:
        schema = {
            'T': 'D',
            'P': {}
        }
        with scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    schema['P'][entry.name] = self._build_schema(entry.path)
                else:
                    with open(entry.path, 'rb') as f:
                        schema['P'][entry.name] = {
                            'T': 'F',
                            'B': f.read()
                        }
        return schema

    def _load_schema(self, wflow: typing.Wflow):
        for action in wflow['WFWorkflowActions']:
            if action['WFWorkflowActionIdentifier'] == 'is.workflow.actions.wfarchive':
                action: typing.Wflow.WFArchiveAction
                break
        else:
            raise InvalidArchive(repr(self.archive_path))
        return action['WFWorkflowActionParameters']

    @classmethod
    def load_from_bytes(cls, s: bytes, name: Optional[str] = None):
        archive =  Archive()
        archive._schema = archive._load_schema(
            plistlib.loads(s, fmt=plistlib.FMT_BINARY))
        if name is not None:
            archive._alternative_name = name
        return archive

    @classmethod
    def load_from_fp(cls, fp: SupportsRead[bytes], name: Optional[str] = None):
        return cls.load_from_bytes(fp.read(), name)

    @classmethod
    def load_from_path(cls, path: str):
        with open(path, 'rb') as f:
            archive = cls.load_from_fp(f)
        archive._archive_path = path
        return archive

    @classmethod
    def new(cls, loose_files_path: str):
        archive = Archive()
        archive._loose_files_path = loose_files_path
        if isfile(loose_files_path):
            with open(loose_files_path, 'rb') as f:
                archive._schema = {
                    'T': 'D',
                    'P': {
                        basename(loose_files_path): {
                            'T': 'F',
                            'B': f.read()
                        }
                    }
                }
        else:
            archive._schema = archive._build_schema(loose_files_path)
        return archive

    @property
    def archive_path(self):
        return self._archive_path

    @property
    def loose_files_path(self):
        return self._loose_files_path

    @property
    def alternative_name(self):
        return self._alternative_name

    @property
    def schema(self):
        return self._schema

    def __bytes__(self):
        return plistlib.dumps(
            templates.wflow(self.schema),
            fmt=plistlib.FMT_BINARY
        )

    def _get_default_archive_path(self):
        if self.alternative_name is None:
            if self.loose_files_path is None:
                raise RuntimeError('cannot determine archive path')
            path = self.loose_files_path
        else:
            path = self.alternative_name
        path, _ = splitext(path)
        return f'{path}.wflow'

    def _get_default_loose_files_path(self):
        if self.alternative_name is None:
            if self.archive_path is None:
                raise RuntimeError('cannot determine loose files path')
            path = self.archive_path
        else:
            path = self.alternative_name
        path, _ = splitext(path)
        return path

    def export_archive(self, path: Optional[str] = None, *, exist_ok: bool = False):
        if self.archive_path is not None:
            raise RuntimeError('cannot call export_archive() or export_signed_archive() on an Archive object initialized by load_from_path()')
        if path is None:
            path = self._get_default_archive_path()
        if (not exist_ok) and exists(path):
            raise FileExistsError(repr(path))
        with open(path, 'wb') as f:
            f.write(bytes(self))

    @overload
    def export_signed_archive(self, path: Optional[str] = None, *, exist_ok: bool = False, capture_output: Literal[True]) -> CompletedProcess: ...

    @overload
    def export_signed_archive(self, path: Optional[str] = None, *, exist_ok: bool = False, capture_output: Literal[False] = False) -> None: ...

    def export_signed_archive(self, path: Optional[str], *, exist_ok: bool = False, capture_output: bool = False):
        if system() != 'Darwin':
            raise RuntimeError('export_signed_archive() can only be called on macOS')
        if path is None:
            path = self._get_default_archive_path()
        self.export_archive(path, exist_ok=exist_ok)
        process = run(['shortcuts', 'sign', '-i', path, '-o', path], capture_output=capture_output)
        return process if capture_output else None

    def export_loose_files(self, path: Optional[str] = None, *, exist_ok: bool = False):
        if self.loose_files_path is not None:
            raise RuntimeError('cannot call export_loose_files() on an Archive object initialized by new()')
        if path is None:
            if len(self.schema['P']) == 1:
                path = '.'
            else:
                path = self._get_default_loose_files_path()
        self._save_dir(self.schema, path, exist_ok)

    def _save_dir(self, schema: typing.Schema, path: str, exist_ok: bool):
        makedirs(path, exist_ok=True)
        for name, sch in schema['P'].items():
            sch_type = sch['T']
            joined_path = join(path, name)
            if sch_type == 'F':
                if (not exist_ok) and exists(joined_path):
                    raise FileExistsError(repr(joined_path))
                with open(joined_path, 'wb') as f:
                    f.write(sch['B'])
            elif sch_type == 'D':
                self._save_dir(sch, joined_path, exist_ok)
            else:
                raise InvalidSchema(f'undefined schema type: {sch_type!r}')


def dlarchive(wflow_id: str):
    record: typing.Record = get(templates.record_url % wflow_id).json()
    archive_bytes = get(record['fields']['shortcut']['value']['downloadURL']).content
    return Archive.load_from_bytes(archive_bytes, record['fields']['name']['value'])
