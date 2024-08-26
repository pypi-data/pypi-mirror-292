#!/usr/bin/env python
from __future__ import annotations

import argparse
import linecache
import logging.config
import os.path
import sys
import unittest
import uuid
from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union
from urllib.parse import urlparse
from urllib.parse import urlunsplit

import yaml
from tqdm import tqdm

# Import Rucio dependencies
os.environ["RUCIO_HOME"] = os.path.expanduser("~/rucio")
from rucio.rse import rsemanager as rsemgr
from rucio.common.utils import generate_uuid
from rucio.client.ruleclient import RuleClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.didclient import DIDClient
from rucio.client.client import Client

sys.path.append("/usr/lib64/python3.6/site-packages/")
from gfal2 import Gfal2Context

# import Classes
from transfer_agents.commons import setupLogging
from transfer_agents.metadata import MetaData
from transfer_agents.es_query import EsData


class RucioData:
    def __init__(
        self,
        default_path: str = "../config/sample.yaml",
        es_body: str = "../config/es_body.json",
        csv_file: str = None,
    ):

        DEFAULT_CONFIG_FILE = "../config/sample.yaml"

        if default_path != DEFAULT_CONFIG_FILE:
            if os.path.exists(default_path):
                with open(default_path) as f:
                    self.config = yaml.safe_load(f)
                    f.close()
                    if "Rucio" not in self.config:
                        raise ValueError("'Rucio' not found in the configuration file")
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

        # Set up logger
        setupLogging(default_path)
        self.logger = logging.getLogger("rucio_functions")

        # Gfal context
        self.gfal = Gfal2Context()
        # Rucio Configuration
        self.didc = DIDClient()
        self.repc = ReplicaClient()
        self.rulesClient = RuleClient()
        self.client = Client()
        self.csv_file = csv_file
        # Get file list
        self.metadata = MetaData(default_path=default_path, csv_file=csv_file)
        self.es = EsData(default_path=default_path, es_body=es_body)

    @property
    def templatesection(self):
        return self.config["Rucio"]["options"]

    @property
    def rucio_account(self):
        return self.templatesection["account"]

    @property
    def rucio_scope(self):
        return self.templatesection["scope"]

    @property
    def rucio_destrse(self):
        return [self.templatesection["destrse"]]

    @property
    def rucio_sourcerse(self):
        return self.templatesection["sourcerse"]

    @property
    def rucio_working_folder(self):
        return self.templatesection["working_folder"]

    def rucio_replication_parameters(self):
        rses_lfn2pfn = []
        for destrse in self.rucio_destrse:
            rses_lfn2pfn.append(
                rsemgr.get_rse_info(
                    destrse,
                )["lfn2pfn_algorithm"],
            )

        if self.rucio_scope not in self.client.list_scopes_for_account(
            account=self.rucio_account,
        ):
            self.logger.info("scope %s needs to be created" % (self.rucio_scope))

            self.logger.info("creating it...")
            try:
                self.client.add_scope(self.rucio_account, self.rucio_scope)
            except Exception as e:
                self.logger.info(e)

        self.logger.info(
            "- Hello your setting are account=%s, scope=%s, origin RSE =%s and destination RSE =%s"
            % (
                self.rucio_account,
                self.rucio_scope,
                self.rucio_sourcerse,
                self.rucio_destrse,
            ),
        )
        self.logger.info(
            "- You will be replicating files to the following RSEs =%s using the following lfn2pfn_algorithm =%s, respectively"
            % (self.rucio_destrse, list(rses_lfn2pfn)),
        )

    ############################

    # Custom functions

    ############################
    def rucio_metadata(self, did, key, value):
        self.didc.set_metadata(
            scope=self.rucio_scope,
            name=did,
            key=key,
            value=value,
            recursive=False,
        )
        return True

    def rucio_list_rules(self):
        return list(self.client.list_account_rules(account=self.rucio_account))

    def rucio_main_rule_exists(self, rule_name, single_rse):
        if list(
            self.rulesClient.list_replication_rules(
                {
                    "scope": self.rucio_scope,
                    "name": rule_name,
                    "rse_expression": single_rse,
                },
            ),
        ):
            return list(
                self.rulesClient.list_replication_rules(
                    {
                        "scope": self.rucio_scope,
                        "name": rule_name,
                        "rse_expression": single_rse,
                    },
                ),
            )[0]["id"]
        else:
            return False

    ##################################################

    def combine_with_duplicate(self, root, rel_path):
        rs = root.split("/")
        rps = rel_path.split("/")
        popped = False
        for v in rs:
            if v == rps[0]:
                rps.pop(0)
                popped = True
            elif popped:
                break

        return "/".join(rs + rps)

    def rucio_rse_url(self):
        """
        Return the base path of the rucio url
        """
        rse_settings = rsemgr.get_rse_info(self.rucio_sourcerse)
        protocol = rse_settings["protocols"][0]

        schema = protocol["scheme"]
        prefix = protocol["prefix"]
        port = protocol["port"]
        rucioserver = protocol["hostname"]

        rse_url = []
        if None not in (schema, str(rucioserver + ":" + str(port)), prefix):
            rse_url.extend(
                [
                    schema,
                    rucioserver + ":" + str(port),
                    prefix,
                    "",
                    "",
                ],
            )
            if self.rucio_working_folder is not None:
                # Check if our test folder exists
                self.logger.info(urlunsplit(rse_url))
                path = os.path.join(urlunsplit(rse_url), self.rucio_working_folder)
                # self.gfal.mkdir_rec(path, 775)
                return path
            else:
                return urlunsplit(rse_url)
        else:
            return "Wrong url parameters"

    def rse_url(self, rse, path=None):
        """
        Return the base path of the rucio url
        """
        rse_settings = rsemgr.get_rse_info(rse)
        protocol = rse_settings["protocols"][0]

        schema = protocol["scheme"]
        prefix = protocol["prefix"]
        port = protocol["port"]
        rucioserver = protocol["hostname"]

        rse_url = []
        if None not in (schema, str(rucioserver + ":" + str(port)), prefix):
            rse_url.extend(
                [
                    schema,
                    rucioserver + ":" + str(port),
                    prefix,
                    "",
                    "",
                ],
            )
            if path is not None:
                # Check if our test folder exists
                path = os.path.join(urlunsplit(rse_url), path)
                # self.gfal.mkdir_rec(path, 775)
                return path
            else:
                return urlunsplit(rse_url)
        else:
            return "Wrong url parameters"

    def rucio_rse_path_file(self, path):
        """
        Return the base path of the rucio url
        """
        rse_settings = rsemgr.get_rse_info(self.rucio_sourcerse)
        protocol = rse_settings["protocols"][0]

        schema = protocol["scheme"]
        prefix = protocol["prefix"]
        port = protocol["port"]
        rucioserver = protocol["hostname"]

        if path is not None:
            prefix = self.combine_with_duplicate(prefix, path)

        rse_url = []
        if None not in (schema, str(rucioserver + ":" + str(port)), prefix):
            rse_url.extend(
                [
                    schema,
                    rucioserver + ":" + str(port),
                    prefix,
                    "",
                    "",
                ],
            )
            return urlunsplit(rse_url)
        else:
            return "Wrong url parameters"

    def rucio_check_replica(self, did, single_rse=None):
        """
        Check if a replica of the given file at the site already exists.
        """
        if not did:
            return False

        replicas = list(
            self.client.list_replicas(
                [{"scope": self.rucio_scope, "name": did}],
                rse_expression=single_rse,
            ),
        )

        for replica in replicas:
            if isinstance(replica, dict) and single_rse in replica["rses"]:
                path = replica["rses"][single_rse][0]
                return path
        return False

    ############################

    # Prepare DIDs for Rucio

    ############################
    def rucio_file_stat(
        self,
        name: str,
        sourcefile: str,
        checksum: str | None = None,
        size: int | None = None,
    ) -> dict[str, str | int]:
        """
        Get the size and checksum for every file in the run from defined path
        """
        """
        generate the registration of the file in a RSE :
        :param rse: the RSE name.
        :param scope: The scope of the file.
        :param name: The name of the file.
        :param bytes: The size in bytes.
        :param adler32: adler32 checksum.
        :param pfn: PFN of the file for non deterministic RSE  
        :param dsn: is the dataset name.
        """
        # Obtener el checksum y tamaño si están presentes, de lo contrario, usar los valores predeterminados
        if checksum is not None:
            adler32_checksum: str = checksum
        else:
            adler32_checksum: str = self.gfal.checksum(sourcefile, "adler32")

        if size is not None:
            file_size: int = size
        else:
            file_size: int = self.gfal.stat(sourcefile).st_size

        # Crear el diccionario replica con los valores obtenidos
        replica: dict[str, str | int] = {
            "scope": self.rucio_scope,
            "name": name,
            "adler32": adler32_checksum,
            "bytes": file_size,
            "pfn": sourcefile,
            "meta": {"guid": str(generate_uuid())},
        }
        return replica

    ############################

    # Create Groups of DIDs

    ############################
    def rucio_create_dataset(self, name_dataset, rse=None):
        self.logger.info(
            "- - Checking if a provided dataset exists: %s for a scope %s"
            % (name_dataset, self.rucio_scope),
        )

        try:
            dataset = self.client.add_dataset(
                scope=self.rucio_scope,
                name=name_dataset,
            )
            if self.client.get_did(self.rucio_scope, name_dataset):
                self.logger.info(
                    "- - - Dataset %s  succesfully created " % (name_dataset),
                )
        except Exception as e:
            self.logger.warning(e)

    def rucio_create_container(self, name_container):
        """
        registration of the dataset into a container :
        :param name_container: the container's name
        :param info_dataset : contains,
            the scope: The scope of the file.
            the name: The dataset name.
        """
        self.logger.info(
            "- - Checking if a provided container exists: %s for a scope %s"
            % (name_container, self.rucio_scope),
        )

        try:
            dataset = self.client.add_container(
                scope=self.rucio_scope,
                name=name_container,
            )
            if self.client.get_did(self.rucio_scope, name_container):
                self.logger.info(
                    "- - - DID %s  succesfully created " % (name_container),
                )
        except Exception as e:
            self.logger.warning(e)

    ############################

    # General funciotn for registering a did into a GROUP of DID (CONTAINER/DATASET)

    ############################
    def rucio_attach_did(self, file_name, dataset_name):
        """
        Attaching a DID to a Collection
        """

        self.logger.info(f"- - - Attaching {file_name} to {dataset_name}")
        try:
            self.client.attach_dids(
                scope=self.rucio_scope,
                name=dataset_name,
                dids=[{"scope": self.rucio_scope, "name": file_name}],
            )
            self.logger.info(
                "- - - {} succesfully attached to {}".format(
                    file_name,
                    dataset_name,
                ),
            )

        except Exception as e:
            self.logger.warning(e)
            self.logger.warning(
                "{} already attached to {}".format(
                    file_name,
                    dataset_name,
                ),
            )

    ############################

    # Prepare Collections for Rucio

    ############################
    def rucio_collections(self, did, collections):

        for collection in collections:
            if "dataset_1" in collection:
                # Create the dataset and containers for the file
                self.rucio_create_dataset(collections[collection])

            else:
                self.rucio_create_container(collections[collection])

            # Attach the dataset and containers for the file
            self.rucio_attach_did(did, collections[collection])
            did = collections[collection]

    ############################

    # Create Rule for DIDs

    ############################
    def rucio_add_rule(
        self,
        single_rse,
        rule_name,
        purge=True,
        priority=3,
        asynchronous=False,
        source_replica_expression=None,
    ):
        """
        Create a replication rule for one dataset at a destination RSE
        """
        type_1 = self.client.get_did(scope=self.rucio_scope, name=rule_name)
        self.logger.debug(
            f"- - - - Creating replica rule for {type_1['type']} {rule_name} at rse: {single_rse}",
        )
        rule_id = self.rucio_main_rule_exists(rule_name, single_rse)

        if rule_id:
            self.logger.info(f"- - - - Rule {rule_id} already exists at {single_rse}")
            return rule_id

        for i in range(2):
            self.logger.info(
                f"Attempt {i+1}: Checking if rule exists for {rule_name} at {single_rse}",
            )
            if self.rucio_main_rule_exists(rule_name, single_rse):
                self.logger.debug(
                    f"Rule already exists for {rule_name} at {single_rse}",
                )
                return

            try:
                rule = self.rulesClient.add_replication_rule(
                    [{"scope": self.rucio_scope, "name": rule_name}],
                    copies=1,
                    rse_expression=single_rse,
                    grouping="ALL",
                    account=self.rucio_account,
                    purge_replicas=purge,
                    priority=priority,
                    asynchronous=asynchronous,
                    source_replica_expression=source_replica_expression,
                )
                self.logger.debug(
                    f"Rule successfully replicated at {single_rse} with id {rule[0]}",
                )
                return rule[0]
            except Exception as e:
                self.logger.info(
                    f"Failed to create rule {rule_name} at {single_rse}: {e}",
                )
                if i == 1:
                    raise Exception("Failed to create rule after multiple attempts")

    ############################

    # Create Rules for not registered DIDs

    ############################
    def outdated_register_replica(self, filemds, destRSE, orgRSE, priority=3):
        """
        Register file replica.
        """
        carrier_dataset = "outdated_replication_dataset" + "-" + str(uuid.uuid4())

        self.logger.info(carrier_dataset)
        self.rucio_create_dataset(carrier_dataset)

        # Create a completly new create the RULE:
        for filemd in filemds:
            self.rucio_attach_did(filemd, carrier_dataset)

        self.logger.info(carrier_dataset)
        outdated_rules = {destRSE: None, orgRSE: None}

        for item_rse in outdated_rules:
            tries = 50
            success = False
            for i in range(0, tries):
                try:
                    rule = self.rucio_add_rule(
                        item_rse,
                        rule_name=carrier_dataset,
                        priority=priority,
                        asynchronous=True,
                    )

                    if (
                        self.rucio_main_rule_exists(carrier_dataset, item_rse)
                        is not None
                    ):
                        outdated_rules[item_rse] = self.rucio_main_rule_exists(
                            carrier_dataset,
                            item_rse,
                        )
                        self.logger.info(
                            "- - This is the rule {} placed at {} ".format(
                                str(outdated_rules[item_rse]),
                                str(item_rse),
                            ),
                        )
                        success = True
                    else:
                        raise Exception(
                            "No rule found for dataset '{}' at RSE '{}'".format(
                                carrier_dataset,
                                item_rse,
                            ),
                        )
                except Exception as e:
                    self.logger.error("Error adding rule: %s" % str(e))
                    self.logger.info("Attempt %d/%d failed" % (i + 1, tries))
                    continue
                break
            if not success:
                return False

        self.logger.info(outdated_rules)
        try:
            # Create a relation rule between origin and destiny RSE, so that the source data can be deleted
            print("primer intento", outdated_rules[orgRSE], outdated_rules[destRSE])
            rule = self.client.update_replication_rule(
                rule_id=outdated_rules[orgRSE],
                options={
                    "lifetime": 10,
                    "child_rule_id": outdated_rules[destRSE],
                    "purge_replicas": True,
                    "priority": priority,
                },
            )

            # Create a relation rule between the destiny rule RSE with itself, to delete the dummy rule, while keeping the destiny files
            print("segundo intento", outdated_rules[destRSE], outdated_rules[destRSE])
            rule = self.client.update_replication_rule(
                rule_id=outdated_rules[destRSE],
                options={
                    "lifetime": 10,
                    "child_rule_id": outdated_rules[destRSE],
                    "purge_replicas": False,
                    "priority": priority,
                },
            )
        except Exception as e:
            self.logger.error("Error updating replication rule: %s" % str(e))
            return False

        return True

        #####################################################3

    def replication_files_rucio(self):
        # Create a list with the properties for writing a text file
        for destRSE in self.rucio_destrse:

            if self.csv_file is None:
                listOfFiles = self.metadata.datatypelist_files()
            else:
                listOfFiles = self.metadata.datatypelist_files_transfer()

            self.logger.info(
                "- Replicating these number of files: {:-<50}".format(
                    "%s" % len(listOfFiles),
                ),
            )
            replication_batch_size = 10

            for i in tqdm(range(0, len(listOfFiles), replication_batch_size)):
                # Create an array for those files that has not been replicated depending on fts priority
                list_priority = {1: [], 2: [], 3: [], 4: [], 5: []}

                for n in range(i, min(i + replication_batch_size, len(listOfFiles))):
                    file = listOfFiles[n]["name"]
                    dest_name = (
                        listOfFiles[n]["destpfn"][1:]
                        if listOfFiles[n]["destpfn"].startswith("/")
                        else listOfFiles[n]["destpfn"]
                    )
                    sourcepfn = (
                        listOfFiles[n]["sourcepfn"][1:]
                        if listOfFiles[n]["sourcepfn"].startswith("/")
                        else listOfFiles[n]["sourcepfn"]
                    )
                    sourcepfn = os.path.join(self.rucio_rse_url(), sourcepfn)

                    # sourcepfn = os.path.join(self.rucio_rse_url(), file.lstrip('/'))
                    destpfn = self.rse_url(
                        destRSE,
                        os.path.join(self.rucio_scope, dest_name),
                    )
                    checksum = listOfFiles[n].get("checksum", None)
                    size = listOfFiles[n].get("size", None)
                    self.logger.info(
                        "- Replicating source file: {:-<50}".format("%s" % sourcepfn),
                    )
                    self.logger.info(
                        "- Replicating destination file: {:-<50}".format(
                            "%s" % (destpfn),
                        ),
                    )

                    # 1) Get the file stat and check existance
                    try:
                        org_check = self.rucio_check_replica(
                            dest_name,
                            single_rse=self.rucio_sourcerse,
                        )
                    except:
                        # File has been deleted or does not exists
                        org_check = False
                    self.logger.info(
                        "- Existance of file at source : {:-<50} ".format(
                            "%s" % org_check,
                        ),
                    )

                    # Else, if the files is not registered
                    if org_check is False:
                        self.logger.info(
                            "{} {} not added".format(
                                file,
                                self.rucio_sourcerse,
                            ),
                        )

                        try:

                            Data = self.rucio_file_stat(
                                dest_name,
                                sourcepfn,
                                size=size,
                                checksum=checksum,
                            )
                            self.logger.info(
                                "- Registring file  : {:-<50} ".format(
                                    "%s" % listOfFiles[n]["name"],
                                ),
                            )

                            add = self.client.add_replicas(
                                rse=self.rucio_sourcerse,
                                files=[Data],
                                ignore_availability=True,
                            )

                            self.logger.info(Data)
                            self.logger.info(
                                "- File registered succesfully: {:-<50}".format(
                                    "%s" % (add),
                                ),
                            )
                            self.logger.info(
                                "- File registered at RSE: {:-<50}".format(
                                    "%s" % (self.rucio_sourcerse),
                                ),
                            )
                            update = self.client.update_replicas_states(
                                self.rucio_sourcerse,
                                [
                                    {
                                        "scope": self.rucio_scope,
                                        "name": dest_name,
                                        "state": "A",
                                    },
                                ],
                            )
                            self.logger.info(
                                "- File state updated at RSE: {:-<50}".format(
                                    "%s" % (update),
                                ),
                            )
                            self.logger.info(
                                self.client.get_did(
                                    scope=self.rucio_scope,
                                    name=dest_name,
                                ),
                            )
                        except Exception as e:
                            exc_type, exc_obj, tb = sys.exc_info()
                            f = tb.tb_frame
                            lineno = tb.tb_lineno
                            filename = f.f_code.co_filename
                            linecache.checkcache(filename)
                            line = linecache.getline(filename, lineno, f.f_globals)
                            self.logger.warning(
                                f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}',
                            )

                        try:
                            # 2) Add metadata from experiments
                            if listOfFiles[n]["metadata"]:
                                for key in listOfFiles[n]["metadata"]:
                                    self.logger.info(
                                        "adding key = %s metadata with value = %s"
                                        % (
                                            key,
                                            listOfFiles[n]["metadata"][str(key)],
                                        ),
                                    )
                                    self.rucio_metadata(
                                        dest_name,
                                        key,
                                        listOfFiles[n]["metadata"][
                                            str(
                                                key,
                                            )
                                        ],
                                    )

                            self.rucio_metadata(
                                dest_name,
                                "replication_time",
                                datetime.today().strftime("%Y%m%d-%H_%M_%S"),
                            )
                        except Exception as e:
                            exc_type, exc_obj, tb = sys.exc_info()
                            f = tb.tb_frame
                            lineno = tb.tb_lineno
                            filename = f.f_code.co_filename
                            linecache.checkcache(filename)
                            line = linecache.getline(filename, lineno, f.f_globals)
                            self.logger.warning(
                                f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}',
                            )

                        # 3) Create rucio's collections [datasets, & or containers]:
                        try:
                            print(listOfFiles[n]["organization"])
                            self.rucio_collections(
                                dest_name,
                                listOfFiles[n]["organization"],
                            )
                        except Exception as e:
                            self.logger.error(e)

                    # If it is registered, skip add replica
                    else:  # needs to be changed to False
                        self.logger.info(
                            "- - The FILE %s already have a replica at RSE %s : %s"
                            % (dest_name, self.rucio_sourcerse, org_check),
                        )
                    # 4) Check existance at destRSE
                    try:
                        dest_check = self.rucio_check_replica(
                            did=dest_name,
                            single_rse=destRSE,
                        )
                    except:
                        # File has been deleted or does not exists
                        dest_check = True

                    # dest_check = False
                    if dest_check is False:

                        self.logger.info(
                            "- - The FILE %s does not have a replica at RSE %s : %s"
                            % (dest_name, destRSE, dest_check),
                        )
                        try:
                            self.rucio_add_rule(
                                destRSE,
                                listOfFiles[n]["collection"],
                                priority=listOfFiles[n]["priority"],
                                asynchronous=False,
                            )
                            self.logger.info(
                                "- - - - Getting parameters for rse %s" % destRSE,
                            )
                            self.logger.info(
                                "Succesfully created main rule for %s"
                                % listOfFiles[n]["collection"],
                            )
                        except Exception as e:
                            self.logger.error(e)
                            self.logger.error(
                                "Failed to create main rule for %s"
                                % (listOfFiles[n]["collection"]),
                            )
                        # 6) Create the json array

                        # Finally, add them to a general list
                        for priority in list_priority:
                            if priority == int(listOfFiles[n]["priority"]):
                                self.logger.info(
                                    "- FILE %s with priority %s is going to be replicated to RSE %s"
                                    % (dest_name, str(priority), destRSE),
                                )
                                list_priority[priority].append(dest_name)

                    # If it is registered, skip add replica
                    else:  # needs to be changed to False
                        self.logger.info(
                            "- The FILE %s already have a replica at RSE %s : %s"
                            % (dest_name, destRSE, dest_check),
                        )

                # Now, create Dummy rules between the ORIGIN and DESTINATION RSEs
                for item in list_priority.items():

                    if len(item[1]) > 0:
                        self.outdated_register_replica(
                            item[1],
                            destRSE,
                            self.rucio_sourcerse,
                            priority=item[0],
                        )
                        self.logger.info(
                            "Your are going to replicate {} files with priority {} from {} to {}".format(
                                str(len(item[1])),
                                str(item[0]),
                                destRSE,
                                self.rucio_sourcerse,
                            ),
                        )
                    else:
                        self.logger.info(
                            "There are no files to be replicated to destination {} with priority {}".format(
                                destRSE,
                                str(item[0]),
                            ),
                        )
