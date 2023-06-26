import sys
from pathlib import Path
import shutil
import logging
import subprocess

import PyInstaller.__main__
import jinja2


DIST_PATH = '../dist'
BUILD_PATH = '../build'
APP_PNG_PATH = 'icons/shutdowner.png'
APP_ICO_PATH = 'icons/shutdowner.ico'
RESOURCES_DIRS = ['icons']
ISS_SCRIPT_PATH = '../shutdowner.iss'
ISS_SCRIPT_TMPL_PATH = f'{ISS_SCRIPT_PATH}.tmpl'


def build_exe_with_pyinstaller():
    logging.info(f'========== Building exe with pyinstaller... ==========')

    clean_dist()

    args = [
        'shutdowner.py',
        '--distpath', DIST_PATH,
        '--workpath', BUILD_PATH,
        '--clean',
        '--windowed',
        '--icon', APP_PNG_PATH,
        # '--log-level', 'WARN',
    ]

    for d in RESOURCES_DIRS:
        args.extend(['--add-data', f'{d};{d}'])

    PyInstaller.__main__.run(args)


def clean_dist():
    logging.info(f'Clean "{Path(DIST_PATH)}" directory...')

    for path in Path(DIST_PATH).iterdir():
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    logging.info(f'"{Path(DIST_PATH)}" directory is cleaned!\n')


def prepare_iss_from_tmpl():
    logging.info(f'========== Prepare Inno Setup script (iss)... ==========')

    iss_config = {
        'app_name': 'shutdowner',
        'app_ver': '0.0.2',
        'app_guid': '{84CE7496-1B5B-4CE1-A5D2-9C126ACB1CA1}',
        'app_ico': Path(APP_ICO_PATH).resolve(),
    }

    tmpl_path = Path(ISS_SCRIPT_TMPL_PATH)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(tmpl_path.parent),
        keep_trailing_newline=True,
        block_start_string='{%%',
        block_end_string='%%}',
        variable_start_string='[{{',
        variable_end_string='}}]',
        comment_start_string='{##',
        comment_end_string='##}',
    )
    template = env.get_template(tmpl_path.name)
    with open(ISS_SCRIPT_PATH, 'w') as f:
        f.write(template.render(iss_config))

    logging.info(f'.iss file successfully generated!')


def build_setup_with_innosetup():
    """ Inno Setup 6 required (+record in sys PATH).
        https://jrsoftware.org/isdl.php#stable
    """
    logging.info(f'========== Building setup with Inno Setup... ==========')

    iss_script_abs_path = (Path(__file__).parent / ISS_SCRIPT_PATH).resolve()
    subprocess.run(['iscc', f'{iss_script_abs_path}'], shell=True)


def generate_ico_from_image(image_path):
    from PIL import Image

    ico = Image.open(image_path)
    ico.save(Path(image_path).with_suffix('.ico'), format='ICO')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
    )

    build_exe_with_pyinstaller()
    prepare_iss_from_tmpl()
    build_setup_with_innosetup()
