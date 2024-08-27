# -*- coding: utf-8 -*-
from datetime import datetime
from imio.scan_logger import CLIENTS_DIC
from imio.scan_logger.utils import create_log_dirs
from imio.scan_logger.utils import get_client_name
from imio.scan_logger.utils import send_notification
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service

import os
import re


class MessageReceiver(Service):
    def reply(self):
        data = json_body(self.request)
        client_id = data.get("client_id", None)
        message = data.get("message", None)
        level = data.get("level", "")
        hostname = data.get("hostname", "")
        version = data.get("version", "")
        cl_infos = f"{client_id} ({hostname}, ver. {version})"
        try:
            if not client_id or not message:
                self.request.response.setStatus(400)
                return {"status": "error", "message": "client_id and message are required in json body"}
            if not re.match(r"^0\d{5}$", client_id):
                return {
                    "status": "error",
                    "message": "client_id must be 6 digits long, start with zero, and contain only digits.",
                }
            if client_id not in CLIENTS_DIC:
                send_notification(
                    f"{cl_infos}), unknown client id",
                    [f"Cannot find {client_id} in clients dic: len is {len(CLIENTS_DIC)}"],
                )

            client_dir = create_log_dirs(client_id)
            file_path = os.path.join(client_dir, f"{hostname}_messages.log")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Open the file in append mode and write the message with the timestamp
            with open(file_path, "a") as file:
                file.write(f"{current_time} {version} | {message}\n")

            if level == "ERROR":
                send_notification(
                    f"Message from {cl_infos} - {get_client_name(client_id)}",
                    message.split("\n"),
                )
        except Exception as err:
            send_notification(
                f"Problem with message from {cl_infos} - {get_client_name(client_id)}",
                message.split("\n") + str(err).split("\n"),
            )
        return {"status": "success", "message": "Log received"}
