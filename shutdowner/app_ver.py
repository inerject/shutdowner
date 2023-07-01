import sys
import logging
from pathlib import Path
import re


class AppVer:
    def __init__(self, path, newline=None):
        path = Path(path)
        if path.is_dir():
            self.path = path.resolve() / '_version.py'
        elif path.is_file():
            self.path = path.resolve()
        else:
            path = path.resolve()
            path.parent.resolve(strict=True)
            self.path = path

        self.newline = newline

    def __repr__(self):
        return self.get()

    def get(self) -> str:
        try:
            with open(self.path) as f:
                version_file_text = f.read()

            ver_pattern = r'^__version__ = ["\']([^"\']*)["\']'
            match = re.search(ver_pattern, version_file_text, re.MULTILINE)
            if match:
                self.repr = match.group(1)
            else:
                raise RuntimeError()

            v = self.repr.split('.')
            self.major, self.minor, self.patch = int(v[0]), int(v[1]), int(v[2])

        except Exception:
            self.repr = 'undefined'
            self.major, self.minor, self.patch = None, None, None

        return self.repr

    def set(self, major, minor, patch):
        with open(self.path, 'w', newline=self.newline) as f:
            f.write(f"__version__ = '{major}.{minor}.{patch}'\n")

    def reset(self):
        self.set(0, 1, 0)

    def inc_patch(self):
        self._check()
        self.patch += 1
        self.set(self.major, self.minor, self.patch)

    def inc_minor(self):
        self._check()
        self.minor += 1
        self.patch = 0
        self.set(self.major, self.minor, self.patch)

    def inc_major(self):
        self._check()
        self.major += 1
        self.minor = 0
        self.patch = 0
        self.set(self.major, self.minor, self.patch)

    def _check(self):
        if self.get() == 'undefined':
            raise ValueError('Version-file is undefined!')


if __name__ == '__main__':
    import argparse

    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        prog='version',
        description="""Managing version-file in format:
            "__version__ = '<M>.<m>.<p>'\\n".
            With no specified arguments [-p] [-m] [-M] [-r],
            it returns __version__ value.""",
    )

    parser.add_argument(
        'file', nargs='?', default='_version.py',
        help='Version-file path. "_version.py" by default.')
    parser.add_argument(
        '-p', '--patch', action='store_true',
        help='inc patch')
    parser.add_argument(
        '-m', '--minor', action='store_true',
        help='inc minor')
    parser.add_argument(
        '-M', '--major', action='store_true',
        help='inc major')
    parser.add_argument(
        '-r', '--reset', action='store_true',
        help='reset/create version-file (0.1.0)')
    parser.add_argument(
        '-n', '--newline', choices=['system', 'windows', 'unix'], default='system',
        help=""" Determines what character(s) are used to terminate line in version-file.
            Valid values are 'system' (by default, whatever the OS uses),
            'windows' (CRLF) and 'unix' (LF only)""")

    args = parser.parse_args()

    #
    newline_variants = {
        'system': None,
        'windows': '\r\n',
        'unix': '\n'
    }
    ver = AppVer(args.file, newline_variants[args.newline])

    opt_counter = 0

    if args.patch:
        opt_counter += 1
    if args.minor:
        opt_counter += 1
    if args.major:
        opt_counter += 1
    if args.reset:
        opt_counter += 1

    if opt_counter == 0:
        print(ver)
        sys.exit()
    elif opt_counter != 1:
        logging.error(f'Select strictly one option! Curr version: {ver}')
        sys.exit(1)

    #
    input_ver_repr = str(ver)

    if args.reset:
        ver.reset()
    if args.patch:
        ver.inc_patch()
    if args.minor:
        ver.inc_minor()
    if args.major:
        ver.inc_major()

    logging.info(f'{ver.path}: {input_ver_repr} -> {ver}')
