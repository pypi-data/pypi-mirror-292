# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory

import csv
import logging
import os


_ = MessageFactory("imio.scan_logger")
log = logging.getLogger("imio.scan_logger")


if os.environ.get("ZOPE_HOME", ""):
    BLDT_DIR = "/".join(os.getenv("INSTANCE_HOME", "").split("/")[:-2])
else:  # test env
    BLDT_DIR = os.getenv("PWD", "")

LOG_DIR = os.path.join(BLDT_DIR, "var", "scan_logs")
for sub in ("code", "name"):
    os.makedirs(os.path.join(LOG_DIR, sub), exist_ok=True)
CLIENTS_CSV = os.path.join(LOG_DIR, "clients.csv")
CLIENTS_DIC = {}

if os.path.exists(CLIENTS_CSV):
    with open(CLIENTS_CSV, "r") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            for i, cc in enumerate(row["TypeCode"].split("-")):
                CLIENTS_DIC[f"{cc}{row['Code']}"] = "{}|{}".format(row["Type"].split("-")[i], row["Name"])
