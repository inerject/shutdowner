import sys
from pathlib import Path
import shutil

import PyInstaller.__main__


DIST_PATH = '../dist'
BUILD_PATH = '../build'
APP_ICON_PATH = 'icons/shutdowner.png'
RESOURCES_DIRS = ['icons']


def clean_dist():
    for path in Path(DIST_PATH).iterdir():
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as err:
            print(f'Error: {err}')
            sys.exit(1)


if __name__ == '__main__':
    clean_dist()

    args = [
        'shutdowner.py',
        '--distpath', DIST_PATH,
        '--workpath', BUILD_PATH,
        '--clean',
        '--windowed',
        '--icon', APP_ICON_PATH,
    ]

    for d in RESOURCES_DIRS:
        args.extend(['--add-data', f'{d};{d}'])

    PyInstaller.__main__.run(args)
