import PyInstaller.__main__


if __name__ == '__main__':
    args = [
        'shutdowner.py',
        '--distpath', '../dist',
        '--workpath', '../build',
        '--clean',
        '--windowed',
        '--icon', 'icons/shutdowner.png'
    ]

    for d in ['icons']:
        args.extend(['--add-data', f'{d};{d}'])

    PyInstaller.__main__.run(args)
