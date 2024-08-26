from __future__ import annotations

import pkg_resources


yamlconfig = pkg_resources.resource_filename(__name__, "sample.yaml")
jsonconfig = pkg_resources.resource_filename(__name__, "es_body.json")
transferfile = pkg_resources.resource_filename(__name__, "transfer.csv")
