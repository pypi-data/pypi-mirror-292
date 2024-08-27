# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2024 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttJamaican - test utilities
"""

import os
import shutil
import tempfile
import warnings
from unittest import TestCase


class FileConfigTestCase(TestCase):
    """
    Common base class for test suites which write temporary files, for
    sake of testing the config constructor etc.

    This inherits from :class:`python:unittest.TestCase` and adds the
    following features:

    Creates a temporary folder on setup, and removes it on teardown.
    Adds the :meth:`write_file()` method to help with creating
    temporary files.

    .. attribute:: tempdir

       Path to the temporary folder created during setup.
    """

    def setUp(self):
        """ """
        self.setup_files()

    def setup_files(self):
        """
        Setup logic specific to the ``FileConfigTestCase``.

        This creates the temporary folder.
        """
        self.tempdir = tempfile.mkdtemp()

    def setup_file_config(self): # pragma: no cover
        """ """
        warnings.warn("FileConfigTestCase.setup_file_config() is deprecated; "
                      "please use setup_files() instead",
                      DeprecationWarning, stacklevel=2)
        self.setup_files()

    def tearDown(self):
        """ """
        self.teardown_files()

    def teardown_files(self):
        """
        Teardown logic specific to the ``FileConfigTestCase``.

        This removes the temporary folder.
        """
        shutil.rmtree(self.tempdir)

    def teardown_file_config(self): # pragma: no cover
        """ """
        warnings.warn("FileConfigTestCase.teardown_file_config() is deprecated; "
                      "please use teardown_files() instead",
                      DeprecationWarning, stacklevel=2)
        self.teardown_files()

    def write_file(self, filename, content):
        """
        Write a new file (in temporary folder) with the given filename
        and content, and return its full path.  For instance::

           myconf = self.write_file('my.conf', '<file contents>')
        """
        path = os.path.join(self.tempdir, filename)
        with open(path, 'wt') as f:
            f.write(content)
        return path

    def mkdir(self, dirname):
        """
        Make a new temporary folder and return its path.

        Note that this will be created *underneath* :attr:`tempdir`.
        """
        return tempfile.mkdtemp(dir=self.tempdir)
