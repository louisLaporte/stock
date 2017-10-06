#!/usr/bin/env python3
from __future__ import print_function
import httplib2
import os
import base64
import json
# needed for attachment
import smtplib
import mimetypes
import email
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from apiclient import discovery, errors
from oauth2client import client, tools
from oauth2client.file import Storage
import logging
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'secret/gmail.json'
APPLICATION_NAME = 'gmail_client'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'cred.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        logger.info('Storing credentials to {}'.format(credential_path))
    return credentials


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        logger.info('Message snippet: {}'.format(message['snippet']))

        return message
    except errors.HttpError as error:
        logger.error('An error occurred: {}'.format(error))


def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()

        logger.info('Message snippet: {}'.format(message['snippet']))

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str.decode('utf-8'))

        return mime_msg
    except errors.HttpError as error:
        logger.error('An error occurred: {}'.format(error))
        return


def TrashMessage(service, user_id, msg_id):
    """Delete a Message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message to delete.
    """
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
        print('Message with id: %s deleted successfully.' % msg_id)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        logger.info('Message Id: {}'.format(message['id']))
        return message
    except errors.HttpError as error:
        logger.error('An error occurred: {}'.format(error))


def create_message(sender, to, subject, message_text, attached_file=None):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message.attach(MIMEText(message_text, 'html'))
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if attached_file:
        my_mimetype, encoding = mimetypes.guess_type(attached_file)
        if my_mimetype is None or encoding is not None:
            my_mimetype = 'application/octet-stream'
        main_type, sub_type = my_mimetype.split('/', 1)
        if main_type == 'text':
            with open(attached_file, 'r') as f:
                attachement = MIMEText(f.read(), _subtype=sub_type)
        elif main_type == 'image':
            with open(attached_file, 'rb') as f:
                attachement = MIMEImage(f.read(), _subtype=sub_type)
        elif main_type == 'audio':
            with open(attached_file, 'rb') as f:
                attachement = MIMEAudio(f.read(), _subtype=sub_type)
        elif main_type == 'application' and sub_type == 'pdf':
            with open(attached_file, 'rb') as f:
                attachement = MIMEApplication(f.read(), _subtype=sub_type)
        else:
            attachement = MIMEBase(main_type, sub_type)
            with open(attached_file, 'rb') as f:
                attachement.set_payload(f.read())
        encoders.encode_base64(attachement)
        filename = os.path.basename(attached_file)
        attachement.add_header('Content-Disposition',
                               'attachment', filename=filename)
        message.attach(attachement)

    b = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': b.decode()}


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    body = """
            <body>
                <p>New message</p>
                <p>from gmail API</p>
            </body>"""

    with open('secret/mail_list.json', 'r') as f:
        contacts = json.load(f)

    for contact in contacts["to"]:
        print("Send message to contact", contact)
        message = create_message(contacts["from"],
                                 contact,
                                 "Stock API",
                                 body)

        send_message(service, 'me', message)


if __name__ == '__main__':
    main()
