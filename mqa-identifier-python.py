import click

from datetime import datetime
from pathlib import Path
from mutagen.flac import FLAC

from mqa_identifier_python.mqa_identifier import MqaIdentifier

ENCODER = 'MQAEncode v1.1, 2.4.0+0 (278f5dd), E24F1DE5-32F1-4930-8197-24954EB9D6F4'


@click.command(name="mqa-identifier-python", short_help="Identifies MQA FLAC files from a folder or from a file",
               context_settings=dict(help_option_names=["-?", "-h", "--help"]
                                     ))
@click.option("--fix-tags", type=bool, default=False, is_flag=True,
              help="Adds all the required tags for MQA such as MQAENCODE, ENCODER and ORIGINALSAMPLERATE.")
@click.argument("paths", nargs=-1, type=click.Path())
def main(paths: list, fix_tags: bool):
    if fix_tags:
        print('MQA tags will be added, overwriting existing MQA tags!')

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

            if fix_tags:
                # adding all needed MQA tags to file with mutagen
                tagger = FLAC(file_path)

                # generate the tags with current date, time
                encoder_time = datetime.now().strftime("%b %d %Y %H:%M:%S")
                tags = {
                    'ENCODER': f'{ENCODER}, {encoder_time}',
                    'MQAENCODER': f'{ENCODER}, {encoder_time}',
                    'ORIGINALSAMPLERATE': str(mqa.original_sample_rate)
                }

                # add tags as VORBIS commit to the FLAC file
                for k, v in tags.items():
                    tagger[k] = v

                # saving the tags
                tagger.save()

        else:
            # too lazy to do it better
            print(f'{i + 1}\tNOT MQA\t\t\t\t\t{file_name}')


if __name__ == '__main__':
    main()
