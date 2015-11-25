syncthing_conflict_resolver.py
==============================

What is it?
-----------

A simple Python 3 script to resolve conflicting files which may appear using [Syncthing](https://syncthing.net/).

    usage: syncthing_conflict_resolver.py [-h] [-n] [-r] [-i] [-l LOG] DIRECTORY

    Gets rid of Syncthing's "*sync-conflict-YYYYMMDD-HHMMSS*" files. It checks the
    modification date of the conflicting files, determines the newest version and
    renames it to the original file name, while deleting the other versions. Be
    careful without any optional arguments!

    positional arguments:
      DIRECTORY          directory to check for sync conflicts

    optional arguments:
      -h, --help         show this help message and exit
      -n, --dry-run      dry run, do not do anything
      -r, --recursive    recurse into subdirectories
      -i, --interactive  prompt for the actions for every sync conflict
      -l LOG, --log LOG  log level. Can be CRITICAL, ERROR, WARNING, INFO, or
                         DEBUG (default: INFO)

**Warning**: If you do not use optional arguments, older versions of conflicting files will be silently deleted. Use `--dry-run` or `--interactive` if you want to check what will be deleted first.

Requirements
------------

This script does not require any external dependencies.

Changelog
---------

Currently, there is no changelog; the best option at the moment is to read the commit messages.

License
-------

GNU GPL

Acknowledgements
----------------

### Authors

- Christoph Haunschmidt