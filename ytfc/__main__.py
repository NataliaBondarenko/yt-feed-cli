"""
Author: https://github.com/NataliaBondarenko
MIT License
2024

This CLI parses RSS feeds and outputs a list of YouTube videos, shorts, and live streams.

Get the list of available options.
    ytfc -h
    
Features

Get the feed for a specific channel or playlist by its ID.
Output: feed info, entries - title, URL.
  Using `--ids`:
    ytfc -i UCBR8-60-B28hp2BmDPdntcQ UULPBR8-60-B28hp2BmDPdntcQ 
  Using `--ids` with @username:
    ytfc -i @youtube 
  Using `--read` (IDs from file):
    ytfc -r <local path to text file>
    Identifiers stored in the file must be separated by newlines.
  Combined `--ids` and `--read` options:
    ytfc -i @youtube -r <local path to text file>
    
Limit the number of entries in the output.
The number of entries in the RSS feed is up to 15.
  Using `--number`:
    ytfc -i UULPBR8-60-B28hp2BmDPdntcQ -n 2

Display details about feed entries.
Output: feed info, entries - title, URL, published, views, likes, description.
  Using `--verbose`:
    ytfc -i UULPBR8-60-B28hp2BmDPdntcQ -v

Save the result to a file (txt or html).
Creates a text file in the given location with the given name.
  Using `--save`:
    ytfc -i @youtube -s <local path>/output.txt
    ytfc -i @youtube -s <local path>/output.html

Skip printing results when saving to a file.
If errors occur, error messages will still be printed.
  Using `--no-print`:
    ytfc -i @youtube -s <local path>/output.txt -np
    ytfc -i @youtube -s <local path>/output.html -np
"""
import argparse
import os.path

from ytfc.utils.decorators import python_exceptions
from ytfc.utils.cli_utils import check_ids
from ytfc.utils.output_utils import generate_output, redirect_output, save_text, save_html


supported_ids_message = '\nSupported identifiers\n\n' \
                        'For all identifiers below, ' \
                        'the allowed characters are A–Z, a–z, 0–9, underscores, and hyphens.\n' \
                        '- Identifiers beginning with PL must contain 16 or 32 characters after the prefix.\n' \
                        '- Identifiers beginning with RD must contain at least 11 characters after the prefix.\n' \
                        '- OLAK5uy_ must be followed by one of these letters: ' \
                        'k, l, m, n, and 32 characters after the letter.\n' \
                        '- UC, UU, UULF, UULV, UUSH, UULP, UUPV, UUPS, UUMO, UUMF, UUMV, UUMS, FL ' \
                        'must be followed by 22 characters after these prefixes.\n' \
                        '- The channel username must start with @ and be between 3 and 30 characters. ' \
                        'A dot character is also allowed. @username is not case-sensitive, ' \
                        'unlike the identifiers listed earlier.\n'

     
@python_exceptions
def main(*args):
    parser = argparse.ArgumentParser(
        prog='ytfc',
        description='This CLI parses RSS feeds and outputs a list of YouTube videos, shorts, and live streams.')

    ids_help = 'Channel or playlist IDs for a request.'
    parser.add_argument('-i', '--ids',
                        nargs='+', metavar='ID', help=ids_help)

    read_help = 'File path to a text file containing a list of channel or playlist IDs.'
    parser.add_argument('-r', '--read',
                        type=str, metavar='FILE', help=read_help)

    number_help = 'Limit the number of entries in the output.'
    parser.add_argument('-n', '--number',
                        type=int, choices=range(1, 16), metavar='N', help=number_help)

    verbose_help = 'Display details about the feed and its entries.'
    parser.add_argument('-v', '--verbose',
                        action='store_true', help=verbose_help)
    
    save_help = 'File path to save the results. Creates a txt or html file with the given name.'
    parser.add_argument('-s', '--save',
                        type=str, metavar='FILE', help=save_help)

    no_print_help = 'Skip printing results when saving to a file.'
    parser.add_argument('-np', '--no-print',
                        action='store_true', help=no_print_help)
    
    args = parser.parse_args()
    
    if not args.ids and not args.read:
        parser.exit(status=0,
                    message=f'\n{parser.prog} 1.0.0{__doc__}{supported_ids_message}')
        
    if args.read:
        if not os.path.exists(args.read):
            parser.exit(status=1,
                        message=f'The path {args.read} does not exist. Check that the path is entered correctly.\n')
        if not os.path.isfile(args.read):
            parser.exit(status=1,
                        message=f'The path {args.read} is not a file path. Check that the path is entered correctly.\n')
            
    if args.save:
        if os.path.exists(args.save):
            parser.exit(status=1, message=f'The file {args.save} already exists. Choose a different file name.\n')
        dir_path = os.path.dirname(args.save)
        if dir_path and not os.path.exists(dir_path):
            parser.exit(status=1,
                        message=f'The directory path {dir_path} does not exist. Check that the path is entered correctly.\n')
        extension = os.path.splitext(args.save)[1][1:]
        if extension not in ['txt', 'html']:
            parser.exit(status=1, message=f'Saving to {args.save}. The file extension must be txt or html.\n')
            
    # both --read and --ids can be used
    invalid_ids, yt_ids = check_ids(args.ids, args.read)
    if invalid_ids:
        parser.exit(status=1,
                    message=f'\nUnsupported id(s): {", ".join(invalid_ids)}.\n'
                    f'{supported_ids_message}')

    print(f'\nID(s): {", ".join(yt_ids)}\n\n')
    
    # saving starts with the first string returned by generators
    if args.save:
        if args.no_print:
            print('Please wait.\n')
            output = generate_output(yt_ids, args.verbose, args.number)
        else:
            output = redirect_output(yt_ids, args.verbose, args.number)
        if extension == 'txt':
            save_text(args.save, output, yt_ids)
        elif extension == 'html':
            save_html(args.save, output, yt_ids)
        print(f'Saving the results to {args.save}.\nDone.')
    else:
        for i in generate_output(yt_ids, args.verbose, args.number):
            print(i)
    parser.exit(status=0)

        
if __name__ == '__main__':
    main()
