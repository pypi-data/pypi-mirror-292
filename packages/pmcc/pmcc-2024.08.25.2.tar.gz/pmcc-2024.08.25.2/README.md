# README #

### What is this repository for? ###

* creates timestamped snapshots of given file(s) in place, without any repository setup
* displays diffs between current state or a given snapshot and the previous one

### How do I get set up? ###

* PyPi - https://pypi.python.org/pypi/pmcc
* Install - pip install pmcc
* Configuration - n/a
* Dependencies - argparse

### Usage

* check / diff - pmcc file.ext [ --di ]
* commit - pmcc file.ext --ci
* log - pmcc file.ext --log
* diff between a given version and previous version - pmcc file.ext --di -cNN # NN = revision number
* revert to the given revision - pmcc file.ext --re -cNN
* invoke an editor after verifying that the file is checked in - pmcc file.ext { --vi | --emacs | --edit }

### How it works

* snapshots are stored as copies of the file preffixed with a dot and suffixed with a unix timestamp
    * e.g. file.ext -> .file.ext.TTTTTTTTTT
* the last action specified on command line overrides all previous ones 
    * so that one can append a quick --di, --ci or --log without having to edit the whole command line

### Who do I talk to? ###

* https://bitbucket.org/dkopen
