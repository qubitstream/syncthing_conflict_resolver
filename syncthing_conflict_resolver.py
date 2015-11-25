#!/usr/bin/env python3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################
#
# Resolve conflicts with Syncthing's *sync-conflict* files, keep only newest versions
#
# Be careful and use the --dry-run option to check out which files would get deleted!
#
# tested on Python 3.3+
#
# Christoph Haunschmidt 2015-11

__version__ = '2015-11-25.0'

import os.path
import argparse
import re
import logging
from collections import defaultdict


SYNC_CONFLICT_RE = re.compile(r'^(?P<root>.*)\.sync-conflict-\d{8}-\d{6}(?P<extension>\.[^\.]*){0,1}$')
DELETED_FILES = 0
RENAMED_FILES = 0


def check_conflicting_files(original_fn, conflict_file_set):
    """Checks conflicting files and keeps the newest"""
    global DELETED_FILES
    global RENAMED_FILES
    all_fns = {original_fn} | conflict_file_set
    if len(all_fns) < 2:
        logging.info('No sync conflict: {}'.format(original_fn))
        return

    mtime_dict = {os.stat(f).st_mtime: f for f in all_fns}
    newest_fn = mtime_dict[max(mtime_dict.keys())]

    to_delete_fns = all_fns - {newest_fn}

    if ARGS.interactive and not ARGS.dry_run:
        print(os.linesep + os.linesep.join(to_delete_fns))
        do_delete = input('Y for keeping {} and deleting the files above? '.format(newest_fn)).lower() == 'y'
    else:
        do_delete = True

    if not do_delete:
        return

    for to_delete_fn in to_delete_fns:
        if not ARGS.dry_run:
            try:
                os.remove(to_delete_fn)
                DELETED_FILES += 1
            except Exception as e:
                logging.error('Error deleting {}: {}'.format(to_delete_fn, e))
        else:
            logging.info('DRY RUN: would delete {}'.format(to_delete_fn))

    if original_fn != newest_fn:
        if not ARGS.dry_run:
            try:
                os.rename(newest_fn, original_fn)
                RENAMED_FILES += 1
            except Exception as e:
                logging.error('Error renaming {} to {}: {}'.format(newest_fn, original_fn, e))
        else:
            logging.info('DRY RUN: would rename {} to {}'.format(newest_fn, original_fn))


def check_dir(directory):
    """Checks a directory (and possible subdirs) for sync-conflict files"""
    conflicting_files = defaultdict(set)

    for root, dirs, files in os.walk(directory):
        try:
            for fn in files:
                m = SYNC_CONFLICT_RE.match(fn)
                if m:
                    conflicting_fn = m.group('root') + (m.group('extension') or '')
                    if conflicting_fn in files:
                        conflicting_files[os.path.join(root, conflicting_fn)].add(os.path.join(root, fn))
                        logging.debug('DIR {}: CONFLICT {} WITH {}'.format(root, conflicting_fn, fn))
                    else:
                        logging.warning('sync-conflict file without equivalent: {}'.format(
                            os.path.join(root, fn)
                        ))
        except Exception as e:
            logging.warning(e)
        if not ARGS.recursive:
            break

    for original_fn, conflicting_fns in conflicting_files.items():
        check_conflicting_files(original_fn, conflicting_fns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gets rid of Syncthing\'s "*sync-conflict-YYYYMMDD-HHMMSS*" files. '
        'It checks the modification date of the conflicting files, determines the newest version and renames it to '
        'the original file name, while deleting the other versions. Be careful without any optional arguments!',
        epilog='Written by Christoph Haunschmidt. Version: {}'.format(__version__))

    parser.add_argument('directory',
        metavar='DIRECTORY', help='directory to check for sync conflicts')

    parser.add_argument('-n', '--dry-run', action='store_true',
        default=False, help='dry run, do not do anything')

    parser.add_argument('-r', '--recursive', action='store_true',
        default=False, help='recurse into subdirectories')

    parser.add_argument('-i', '--interactive', action='store_true',
        default=False, help='prompt for the actions for every sync conflict')

    parser.add_argument('-l', '--log', action='store', default='INFO',
        help='log level. Can be CRITICAL, ERROR, WARNING, INFO, or DEBUG (default: %(default)s)')

    ARGS = parser.parse_args()

    numeric_level = getattr(logging, ARGS.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(ARGS.log))

    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=numeric_level,
        datefmt='%Y-%m-%d %H:%M')

    if os.path.isdir(ARGS.directory):
        check_dir(ARGS.directory)
        print('Done, {} files deleted, {} files renamed.'.format(DELETED_FILES, RENAMED_FILES))
    else:
        logging.critical('{} is not a directory.'.format(ARGS.directory))
