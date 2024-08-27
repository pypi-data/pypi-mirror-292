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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#

import iocbio.db.db as iocdb


class DatabaseInterface(iocdb.DatabaseInterface):
    """Database interface and helper functions"""

    current_schema_version = "7"
    settings_compname = "iocbio"
    settings_appname = "sparks"

    @staticmethod
    def remove_login(username=None):
        """Remove all saved login information"""
        iocdb.DatabaseInterface.remove_login(
            DatabaseInterface.settings_compname, DatabaseInterface.settings_appname, username
        )

    @staticmethod
    def settings():
        return iocdb.DatabaseInterface.settings(DatabaseInterface.settings_compname, DatabaseInterface.settings_appname)

    def __init__(self):
        iocdb.DatabaseInterface.__init__(self, self.settings_compname, self.settings_appname)

    def schema(self):
        """Check the present schema version, create if missing and return the version of current schema"""

        version = self.schema_version()
        if version is None:
            self.schema_set_version(DatabaseInterface.settings_appname, DatabaseInterface.current_schema_version)
            version = self.schema_version()

        if version == "1":
            self.schema_update_1_2()
        elif version == "2":
            self.schema_update_2_3()
        elif version == "3":
            self.schema_update_3_4()
        elif version == "4":
            self.schema_update_4_5()
        elif version == "5":
            self.schema_update_5_6()
        elif version == "6":
            self.schema_update_6_7()
        elif version == "7":
            pass
        else:
            raise RuntimeError("This version (%s) of database schema is not supported" % version)

    def schema_update_1_2(self):
        from iocbio.sparks.constants import database_table_experiment

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        self.query("ALTER TABLE " + self.table(database_table_experiment) + " ADD transposed INTEGER DEFAULT 0")
        self.schema_set_version(DatabaseInterface.settings_appname, "2")

        self.schema()  # to check whether further updates are needed

    def schema_update_2_3(self):
        from iocbio.sparks.calc.spark import Spark

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Spark.database_schema_update_2_3(self)
        self.schema_set_version(DatabaseInterface.settings_appname, "3")

        self.schema()  # to check whether further updates are needed

    def schema_update_3_4(self):
        from iocbio.sparks.calc.spark import Spark
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_3_4(self)
        Spark.database_schema_update_3_4(self)
        self.schema_set_version(DatabaseInterface.settings_appname, "4")

        self.schema()  # to check whether further updates are needed

    def schema_update_4_5(self):
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_4_5(self)
        self.schema_set_version(DatabaseInterface.settings_appname, "5")

        self.schema()  # to check whether further updates are needed

    def schema_update_5_6(self):
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_5_6(self)
        self.schema_set_version(DatabaseInterface.settings_appname, "6")

        self.schema()  # to check whether further updates are needed

    def schema_update_6_7(self):
        from iocbio.sparks.handler.experiment import ExperimentHandler

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        ExperimentHandler.database_schema_update_6_7(self)
        self.schema_set_version(DatabaseInterface.settings_appname, "7")

        self.schema()  # to check whether further updates are needed
