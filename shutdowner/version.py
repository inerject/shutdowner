import sys
import logging
from pathlib import Path

import jinja2


class Version:
    def __init__(self, path):
        path = Path(path)
        if path.is_dir():
            self.path = path.resolve() / 'VERSION'
        elif path.is_file():
            self.path = path.resolve()
        else:
            path = path.resolve()
            path.parent.resolve(strict=True)
            self.path = path

    def __repr__(self):
        return self.get()

    def get(self) -> str:
        try:
            with open(self.path) as f:
                self.repr = f.readline().rstrip()

            v = self.repr.split('.')
            self.major, self.minor, self.patch = int(v[0]), int(v[1]), int(v[2])

        except Exception:
            self.repr = 'undefined'
            self.major, self.minor, self.patch = None, None, None

        return self.repr

    def set(self, major, minor, patch):
        with open(self.path, 'w') as f:
            f.write(f'{major}.{minor}.{patch}\n')

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

    def generate_app_ver_py(
        self,
        result_path,
        tmpl_path=(Path(__file__).parent / 'templates/app_ver.py.tmpl'),
    ):
        result_path = Path(result_path).resolve()
        logging.info(f'Generating {result_path}...')

        app_ver_py_config = {
            'app_ver': self.get(),
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
        }

        tmpl_path = Path(tmpl_path)
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(tmpl_path.parent),
            keep_trailing_newline=True,
        )
        template = env.get_template(tmpl_path.name)
        with open(result_path, 'w') as f:
            f.write(template.render(app_ver_py_config))

        logging.info(f'{result_path} successfully generated!')

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
        description='Managing app version in "major.minor.patch" format.',
    )

    parser.add_argument(
        'file', nargs='?', default='VERSION',
        help='Version-file path. "VERSION" by default.')
    parser.add_argument(
        '-g', '--gen-py', default="app_ver.py",
        help="""Generated py-file path. "app_ver.py" by default.
            Pass "skip" for skipping py-file generation.""")
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

    args = parser.parse_args()

    #
    ver = Version(args.file)

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
        parser.print_help()
        sys.exit(1)
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

    logging.info(f'{input_ver_repr} -> {ver}')

    if args.gen_py != 'skip':
        ver.generate_app_ver_py(args.gen_py)
