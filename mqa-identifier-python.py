from pathlib import Path

import click

from mqa_identifier_python.mqa_identifier import MqaIdentifier


@click.command(name="mqa-identifier-python", short_help="Identifies MQA FLAC files from a folder or from a file",
               context_settings=dict(help_option_names=["-?", "-h", "--help"]
                                     ))
@click.argument("paths", nargs=-1, type=click.Path())
def main(paths):
    # get all flac paths from arguments
    flac_paths = []

    for path in paths:
        path = Path(path)
        if Path.is_dir(path):
            # search for flac files recursively
            flac_paths += sorted(Path(path).glob('**/*.flac'))
        elif str(path).endswith('.flac') and path.is_file():
            flac_paths.append(path)

    if len(flac_paths) == 0:
        print('No FLAC files could be found!')
        return

    print(f'Found {len(flac_paths)} FLAC files to check')
    print('#\tEncoding\t\t\t\tName')
    for i, file_path in enumerate(flac_paths):
        # let's identify the MQA file
        mqa = MqaIdentifier(file_path)
        file_name = file_path.parts[-1]
        # python is dumb
        nt = '\t\t'

        # check if file is MQA
        if mqa.is_mqa:
            # beauty print MQA stuff
            print(f'{i + 1}\tMQA{" Studio" if mqa.is_mqa_studio else ""} {mqa.get_original_sample_rate()}kHz'
                  f'{"" if mqa.is_mqa_studio else nt}\t\t{file_name}')
        else:
            # too lazy to do it better
            print(f'{i + 1}\tNOT MQA\t\t\t\t\t{file_name}')


if __name__ == '__main__':
    main()
