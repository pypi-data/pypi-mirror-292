# import modules
from __future__ import annotations

import json
import linecache
import logging
import os
import re
import sys
import unittest
import uuid
from string import Template

import yaml

from transfer_agents.commons import setupLogging
from transfer_agents.db_functions import dbData
from transfer_agents.transfer_file import TransferFile

# import Classes


class MetaData:
    _config = None

    def __init__(
        self,
        default_path: str = "../config/sample.yaml",
        csv_file: str = None,
    ):

        DEFAULT_CONFIG_FILE = "../config/sample.yaml"

        if default_path != DEFAULT_CONFIG_FILE:
            if os.path.exists(default_path):
                with open(default_path) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
            else:
                print(
                    f"Configuration file '{default_path}' not found. Using default configuration file.",
                )
                with open(DEFAULT_CONFIG_FILE) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
        else:
            with open(DEFAULT_CONFIG_FILE) as f:
                self.config = yaml.safe_load(f)
                f.close()

        setupLogging(default_path)
        self.logger = logging.getLogger("metadata")

        # import functions from db_functions.py
        self.db = dbData(default_path)
        self.transfer_file = TransferFile(default_path, csv_file)

    # properties
    @property
    def root_elements(self):
        return (
            object_session(self)
            .query(MetaData)
            .filter_by(project=self, parent=None)
            .order_by(MetaData.name)
        )

    @property
    def templatesection(self):
        return self.config["Template"]

    @property
    def basedir(self):
        return self.templatesection["options"]["basedir"]

    @property
    def filename(self):
        return self.templatesection["options"]["filename"]

    @property
    def datasection(self):
        return self.config["Data Sections"]

    @property
    def dataconfig(self):
        return self.config["Data Sections"]

    @property
    def datatypelist(self):
        return [
            section
            for section in self.datasection.keys()
            if self.datasection[section]["options"]["basedir"]
            and self.datasection[section]["options"]["transfer"]
        ]

    def datatypelist_files(self):
        project_list = self.datatypelist
        self.logger.info(project_list)

        list_metadata = list()

        for project_name in project_list:
            self.logger.info("- Project: {:-<50}".format("%s " % project_name))
            query = Template(
                self.datasection[project_name]["options"]["query"],
            ).safe_substitute(
                dict(self.datasection[project_name]["regex"].items()),
            )
            self.logger.info("- Query: {:-<50}".format("%s " % query))
            list_files = self.db.execute_query(query)

            if self.datatype_transfer(project_name) == True:
                if len(list_files) == 0:
                    self.logger.info("- No files to transfer")
                else:
                    for file_name in list_files:
                        self.logger.info(file_name)
                        metadata = self.parse_datatype(project_name, file_name)
                        source_dir = self.datatype_sourcepfn(project_name, file_name)
                        dest_dir = self.datatype_destpfn(project_name, file_name)

                        self.logger.info("- Result: {:-<50}".format("%s " % metadata))
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s "
                                % Template(source_dir).safe_substitute(
                                    dict(metadata.items()),
                                ),
                            ),
                        )
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s "
                                % Template(dest_dir).safe_substitute(
                                    dict(metadata.items()),
                                ),
                            ),
                        )
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s " % self.parse_organization(project_name, metadata),
                            ),
                        )
                        self.logger.info("- Result: {:-<50}".format("%s " % dest_dir))
                        file_data = {}
                        file_data["name"] = file_name
                        file_data["sourcepfn"] = Template(source_dir).safe_substitute(
                            dict(metadata.items()),
                        )
                        if "output_path" in self.datasection[project_name]["options"]:
                            output_path = self.datasection[project_name]["options"][
                                "output_path"
                            ].format(file_name)
                            file_data["destpfn"] = list(
                                self.db.execute_query(output_path),
                            )[0]
                        else:
                            file_data["destpfn"] = Template(dest_dir).safe_substitute(
                                dict(metadata.items()),
                            )

                        file_data["collection"] = self.datatype_rule(project_name)
                        file_data["metadata"] = self.parse_metadata(
                            project_name,
                            metadata,
                        )
                        file_data["organization"] = self.parse_organization(
                            project_name,
                            metadata,
                        )
                        file_data["priority"] = self.datatype_priority(project_name)
                        # print(file_data)
                        list_metadata.append(file_data)
        return list_metadata

    def datatypelist_files_transfer(self):
        project_list = self.datatypelist
        self.logger.info(project_list)
        list_files = self.transfer_file.get_csv_data()
        list_metadata = list()
        metadata_dict = {}

        for project_name in project_list:
            self.logger.info("- Project: {:-<50}".format("%s " % project_name))
            if self.datatype_transfer(project_name) == True:
                if len(list_files) == 0:
                    self.logger.info("- No files to transfer")
                else:
                    matching_rows = list_files[
                        list_files[0].str.contains(project_name, case=False)
                    ]
                    # Agregar las filas coincidentes a la lista de metadatos

                    for index, row in matching_rows.iterrows():
                        file_name = row[0]
                        self.logger.info(file_name)
                        metadata = self.parse_datatype(project_name, file_name)
                        source_dir = self.datatype_sourcepfn(project_name, file_name)
                        dest_dir = self.datatype_destpfn(project_name, file_name)

                        file_data = {}
                        file_data = {}
                        name = str(uuid.uuid4())
                        self.logger.info("- Result: {:-<50}".format("%s " % metadata))
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s "
                                % Template(source_dir).safe_substitute(
                                    dict(metadata.items()),
                                ),
                            ),
                        )
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s "
                                % Template(dest_dir).safe_substitute(
                                    dict(metadata.items()),
                                ),
                            ),
                        )
                        self.logger.info(
                            "- Result: {:-<50}".format(
                                "%s " % self.parse_organization(project_name, metadata),
                            ),
                        )

                        file_data["name"] = file_name
                        file_data["sourcepfn"] = Template(source_dir).safe_substitute(
                            dict(metadata.items()),
                        )
                        file_data["destpfn"] = name
                        file_data["checksum"] = row[1]
                        file_data["size"] = row[2]
                        file_data["priority"] = self.datatype_priority(project_name)
                        file_data["destpfn"] = Template(dest_dir).safe_substitute(
                            dict(metadata.items()),
                        )
                        # file_data["destpfn"] = Template(dest_dir).safe_substitute(dict(metadata.items())) + '/' + name
                        file_data["collection"] = self.datatype_rule(project_name)
                        file_data["metadata"] = self.parse_metadata(
                            project_name,
                            metadata,
                        )
                        file_data["organization"] = self.parse_organization(
                            project_name,
                            metadata,
                        )

                        list_metadata.append(file_data)
        print(list_metadata)
        return list_metadata

    def filename_regex(self):
        template = Template(
            Template(self.filename).safe_substitute(
                dict(self.templatesection["reblocks"].items()),
            ),
        ).safe_substitute(
            dict(self.templatesection["regex"].items()),
        )
        self.logger.debug(template)
        return template

    def datatype_rule(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["rule_name"]

    def datatype_basedir(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["basedir"]

    def datatype_transfer(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["transfer"]

    def datatype_filename(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["filename"]

    def datatype_sourcedir(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["sourcedir"]

    def datatype_destdir(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["destdir"]

    def datatype_priority(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["priority"]

    def datatype_sourcepfn(self, data_type, file_name):
        return os.path.join(
            self.datatype_basedir(data_type),
            self.datatype_sourcedir(data_type),
            file_name,
        )

    def datatype_destpfn(self, data_type, file_name):
        if file_name.startswith("/"):
            file_name = file_name[1:]
        return os.path.join(self.datatype_destdir(data_type), file_name)

    def datatype_metadata(self, data_type):
        return dict(self.config["Data Sections"][data_type]["metadata"])

    def datatype_organization(self, data_type):
        return dict(self.config["Data Sections"][data_type]["organization"])

    def parse_organization(self, data_type, metadata):
        organization = self.datatype_organization(data_type)
        for x in organization.items():
            organization.update(
                {x[0]: Template(x[1]).safe_substitute(dict(metadata.items()))},
            )
        return organization

    def parse_metadata(self, data_type, metadata):
        template = self.datatype_metadata(data_type)

        for x in template.items():
            template.update(
                {x[0]: Template(x[1]).safe_substitute(dict(metadata.items()))},
            )
        return template

    def datatype_path(self, data_type):
        return os.path.join(
            self.datatype_basedir(data_type),
            self.datatype_sourcedir(data_type),
            self.datatype_filename(data_type),
        )

    def datatype_extra(self, data_type):
        return self.config["Data Sections"][data_type]["options"]["extra_metadata"]

    def datatype_extra_query(self, data_type):
        return self.config["Data Sections"][data_type]["extra_metadata"]["query_1"]

    def datatype_extra_query_2(self, data_type):
        return self.config["Data Sections"][data_type]["extra_metadata"]["query_2"]

    def datatype_regex(self, data_type):
        return self.config["Data Sections"][data_type]["regex"]

    def datatype_reblocks(self, data_type):
        return self.config["Data Sections"][data_type]["reblocks"]

    def parse_file_name(self, file_name):
        m = re.match(self.filename_regex(), file_name)
        try:
            return m.groupdict()
        except AttributeError:
            raise FilenameRegexMismatch(
                "Filename does not match regex ({} vs. {})".format(
                    self.name,
                    self.datatype.filename_regex(vars={}),
                ),
            )

    def datatype_parse(self, project_name):
        # self.logger.debug('this is project filename ', project_name)
        self.logger.debug(self.datatype_filename(project_name))
        self.logger.debug(self.datatype_reblocks(project_name))
        self.logger.debug(self.datatype_regex(project_name))
        template = Template(
            Template(self.datatype_filename(project_name)).safe_substitute(
                dict(self.datatype_reblocks(project_name).items()),
            ),
        ).safe_substitute(dict(self.datatype_regex(project_name).items()))
        self.logger.debug(template)
        return template

    def parse_datatype(self, project_name, file_name):
        self.logger.debug(
            "- Datatype: {:-<50}".format(f"{project_name} {file_name}"),
        )

        if self.datatype_extra(project_name) == True:
            query = self.datatype_extra_query(project_name)
            query = query % (file_name)
            # self.logger.debug('this is extra query ', query)
            self.logger.debug("- Extra query: {:-<50}".format("%s" % query))
            extra_metadata = list(
                self.db.execute_query(
                    self.datatype_extra_query(project_name) % (file_name),
                ),
            )[0]
            template = self.datatype_parse(project_name)
            self.logger.debug(template)
            self.logger.info(extra_metadata)
            m = re.match(template, os.path.join(extra_metadata, file_name))

        else:
            template = self.datatype_parse(project_name)
            m = re.match(template, file_name)

        self.logger.debug(m)
        try:
            metadata = m.groupdict()
            metadata.update(self.datatype_metadata(project_name))

            if self.datatype_extra(project_name) == True:
                extra_metadata_2 = json.loads(
                    list(
                        self.db.execute_query(
                            self.datatype_extra_query_2(project_name) % (file_name),
                        ),
                    )[0],
                )
                self.logger.debug(extra_metadata_2)
                metadata.update(extra_metadata_2)

            return metadata
        except AttributeError:
            # raise FilenameRegexMismatch('Filename does not match regex (%s vs. %s)' % (self.name, self.datatype.filename_regex(vars={})))
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            self.logger.warning(
                f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}',
            )
