# -*- coding: utf-8 -*-
from imio.helpers.emailer import create_html_email
from imio.helpers.emailer import send_email
from imio.scan_logger import CLIENTS_DIC
from imio.scan_logger import log
from imio.scan_logger import LOG_DIR
from plone import api

import os


def create_log_dirs(client_id):
    """Create log directories."""
    client_dir = os.path.join(LOG_DIR, "code", client_id)
    os.makedirs(client_dir, exist_ok=True)
    client_name = get_client_name(client_id, sep="_")
    if client_name:
        dest = os.path.join(LOG_DIR, "name", client_name)
        if not os.path.exists(dest):
            os.symlink(client_dir, dest)
    return client_dir


def get_client_name(code, sep=" "):
    """Get client name from code."""
    return CLIENTS_DIC.get(code, "").replace("|", sep)


def send_notification(title, lines):
    """Send email if required."""
    emails = api.portal.get_registry_record("imio.scan_logger.interfaces.ISettings.notification_emails")
    if not emails:
        return
    emails = [email.strip() for email in emails.split(",")]
    msg = create_html_email("\n".join(["<p>{}</p>".format(line) for line in lines]))
    mfrom = api.portal.get_registry_record("plone.email_from_address")
    ret, error = send_email(msg, title, mfrom, emails)
    # try:
    # api.portal.send_email(mfrom, emails[0], title, "\n".join(lines))
    # except ValueError as error:
    if not ret:
        log.error(f"Cannot send email: {error}")
