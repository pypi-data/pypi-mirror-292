from pathlib import Path

name = 'karaoke'
help_text = 'GUI for negromate karaoke'


def options(parser, config, **kwargs):
    parser.add_argument(
        '-s', '--song_folder', type=Path,
        default=config['global']['song_folder'],
        help="Folder with the song database, defaults to {}".format(
            config['global']['song_folder']))


def run(args, **kwargs):
    from ..karaoke import main
    main(args.song_folder.expanduser())
