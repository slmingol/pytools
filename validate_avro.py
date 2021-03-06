#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-12-22 23:25:25 +0000 (Tue, 22 Dec 2015)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback
#  to help improve or steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Avro Validator Tool

Validates each file passed as an argument

Directories are recursed, checking all files ending in a .avro suffix.

Works like a standard unix filter program - if no files are passed as arguments or '-' is given then reads
from standard input

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import os
import re
import sys
import avro
from avro.datafile import DataFileReader
from avro.io import DatumReader
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import die, ERRORS, log_option, uniq_list_ordered
    from harisekhon import CLI
except ImportError as _:
    print('module import failed: %s' % _, file=sys.stderr)
    print("Did you remember to build the project by running 'make'?", file=sys.stderr)
    print("Alternatively perhaps you tried to copy this program out without it's adjacent libraries?", file=sys.stderr)
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.7.3'

class AvroValidatorTool(CLI):

    def __init__(self):
        # Python 2.x
        super(AvroValidatorTool, self).__init__()
        # Python 3.x
        # super().__init__()
        self.re_avro_suffix = re.compile(r'.*\.avro$', re.I)
        self.valid_avro_msg = '<unknown> => Avro OK'
        self.invalid_avro_msg = '<unknown> => Avro INVALID'

    def check_avro(self, filehandle):
        try:
            DataFileReader(filehandle, DatumReader())
            print(self.valid_avro_msg)
        except avro.datafile.DataFileException as _:
            if 'snappy' in str(_):
                die("%s => ERROR: %s - Is the python-snappy module installed? ('pip install python-snappy')" \
                    % (filehandle.name, _))
            die("%s => ERROR: %s" % (filehandle.name, _))
        except TypeError as _:
            if self.verbose > 2:
                print(_)
            die(self.invalid_avro_msg)

    def run(self):
        if not self.args:
            self.args.append('-')
        args = uniq_list_ordered(self.args)
        for arg in args:
            if arg == '-':
                continue
            if not os.path.exists(arg):
                print("'%s' not found" % arg)
                sys.exit(ERRORS['WARNING'])
            if os.path.isfile(arg):
                log_option('file', arg)
            elif os.path.isdir(arg):
                log_option('directory', arg)
            else:
                die("path '%s' could not be determined as either a file or directory" % arg)
        for arg in args:
            self.check_path(arg)

    def check_path(self, path):
        if path == '-' or os.path.isfile(path):
            self.check_file(path)
        elif os.path.isdir(path):
            for item in os.listdir(path):
                subpath = os.path.join(path, item)
                if os.path.isdir(subpath):
                    self.check_path(subpath)
                elif self.re_avro_suffix.match(item):
                    self.check_file(subpath)
        else:
            die("failed to determine if path '%s' is file or directory" % path)

    def check_file(self, filename):
        if filename == '-':
            filename = '<STDIN>'
        self.valid_avro_msg = '%s => Avro OK' % filename
        self.invalid_avro_msg = '%s => Avro INVALID' % filename
        if filename == '<STDIN>':
            self.check_avro(sys.stdin)
        else:
            try:
                with open(filename) as avrohandle:
                    self.check_avro(avrohandle)
            except IOError as _:
                die("ERROR: %s" % _)


if __name__ == '__main__':
    AvroValidatorTool().main()
