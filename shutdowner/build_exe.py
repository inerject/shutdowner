from pathlib import Path


def abs_path(relative_path):
    return (Path(__file__).parent / relative_path).resolve()


if __name__ == '__main__':
    import argparse
    import logging
    import pyappbundler
    from _version import __version__

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-e', '--only-exe', action='store_true',
        help='build only exe (without setup)')

    args = parser.parse_args()

    #
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
    )

    app_name = 'shutdowner'
    bundler_config = {
        'target': abs_path('shutdowner.py'),
        'icon': abs_path('icons/shutdowner.ico'),
        'app_guid': '{84CE7496-1B5B-4CE1-A5D2-9C126ACB1CA1}',
        'app_ver': __version__,
        'res_dirs': [abs_path('icons')],
        'pyinst_flags': ['windowed', 'clean'],
    }

    if args.only_exe:
        pyappbundler.exe(**bundler_config)
    else:
        pyappbundler.exe_and_setup(**bundler_config)
