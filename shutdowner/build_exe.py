from pathlib import Path
import shutil
import logging
import subprocess

import PyInstaller.__main__
import jinja2

from _version import __version__


def clean_dist(dist):
    dist_path = Path(dist).resolve()
    logging.info(f'Cleaning "{dist_path}" directory...')

    if not dist_path.exists():
        dist_path.mkdir(parents=True)
        logging.info(
            f'"{dist_path}" directory doesn\'t exist!'
            ' The new one has been created.')
        return

    if not dist_path.is_dir():
        raise FileNotFoundError(
            f'Directory expected, but "{dist_path}" is not!')

    for path in dist_path.iterdir():
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

    logging.info(f'"{dist_path}" directory has been cleaned!\n')


def build_exe(
    target, app_name, icon, dist, build,
    pyinst_extra_flags: list = None,
    resource_dirs: list = None,
):
    logging.info(f'Building exe with PyInstaller...')

    args = [
        str(Path(target).resolve()),
        '--name', app_name,
        '--icon', str(Path(icon).resolve()),
        '--distpath', str(Path(dist).resolve()),
        '--workpath', str(Path(build).resolve()),
    ]

    if pyinst_extra_flags:
        args.extend([f'--{it}' for it in pyinst_extra_flags])

    if resource_dirs:
        for directory in resource_dirs:
            directory_path = Path(directory).resolve()
            if not directory_path.is_dir():
                raise FileNotFoundError(
                    f'Directory expected, but "{directory_path}" is not!')
            args.extend(['--add-data', f'{directory_path};{directory_path.name}'])

    PyInstaller.__main__.run(args)


def generate_iss(app_name, icon, dist, app_ver, app_guid):
    iss_path = Path(f'{app_name}.iss').resolve()
    logging.info(f'Generating "{iss_path}" file...')

    iss_config = {
        'app_name': app_name,
        'app_ico': str(Path(icon).resolve()),
        'dist': str(Path(dist).resolve()),
        'app_ver': app_ver,
        'app_guid': app_guid,
    }

    tmpl_path = Path(__file__).parent / 'templates/iss.tmpl'
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
    with open(iss_path, 'w') as f:
        f.write(template.render(iss_config))

    logging.info(f'"{iss_path}" file successfully generated!')


def build_setup(app_name):
    """ Inno Setup 6 required (+record in sys PATH).
        https://jrsoftware.org/isdl.php#stable
    """
    logging.info(f'Building setup with Inno Setup...')
    subprocess.run(['iscc', f'{app_name}.iss'], shell=True)


def generate_ico_from_image(image_path):
    from PIL import Image

    ico = Image.open(image_path)
    ico.save(Path(image_path).with_suffix('.ico'), format='ICO')


if __name__ == '__main__':
    import argparse

    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        prog='build-exe',
        description="""Automate bundle a Python application and all its
            dependencies into a single package with PyInstaller
            (https://pyinstaller.org/en/stable). And then (for Windows), put it all into
            a setup file with Inno Setup (https://jrsoftware.org/isdl.php#stable).""",
    )

    default_pyinst_extra_flags = [
        'windowed',
        'clean',
    ]

    parser.add_argument(
        '-t', '--target', required=True, help='target python script')
    parser.add_argument(
        '-a', '--app-name', required=True, help='application name')
    parser.add_argument(
        '-i', '--icon', required=True, help='application icon')
    parser.add_argument(
        '--dist', default='dist',
        help='Distribution directory path. "dist" byte default.')
    parser.add_argument(
        '--build', default='build',
        help='Where PyInstaller put all the temporary work files. "build" by default.')
    parser.add_argument(
        '--pyinst-extra-flags', nargs='*', default=default_pyinst_extra_flags,
        help=f"""Extra FLAG-arguments (without "--" prefix) for PyInstaller.
            Example: ... --pyinst-extra windowed clean ..." will pass "--windowed"
            and "--clean" flags to PyInstaller during application bundling.
            "{' '.join(default_pyinst_extra_flags)}" by default.""")
    parser.add_argument(
        '--resource-dirs', nargs='*',
        help="Directories with additional files to be added to the executable.")
    parser.add_argument(
        '--no-clean-dist', action='store_true',
        help='cancel cleaning dist directory before building')
    parser.add_argument(
        '-v', '--app-ver', help='application version')
    parser.add_argument(
        '--app-guid', required=True, help='application GUID')

    args = parser.parse_args()

    #
    if not args.no_clean_dist:
        clean_dist(args.dist)

    build_exe(
        args.target, args.app_name, args.icon, args.dist, args.build,
        args.pyinst_extra_flags, args.resource_dirs)

    if not args.app_ver:
        args.app_ver = __version__
    generate_iss(args.app_name, args.icon, args.dist, args.app_ver, args.app_guid)
    build_setup(args.app_name)
