import re
import json
import pickle
import sys
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def make_get_message_ids_request(query, page_token, gmail):
    params = {
        'userId': 'me',
        'q': query,
        'pageToken': page_token,
    }

    return gmail.users().messages().list(**params)


def make_get_message_by_id_request(id, gmail):
    params = {
        'userId': 'me',
        'id': id,
        'format': 'full',
    }

    return gmail.users().messages().get(**params)


def make_message(message):
    message_id = message['id']
    internal_date = message['internalDate']
    payload = message['payload']
    headers = payload['headers']

    if 'parts' in payload:
        body = payload['parts'][0]['body']['data']
    else:
        body = payload['body']['data']

    from_header = [header for header in headers if header['name'] == 'From'][0]
    from_header_value = re.sub('[<>]', '', from_header['value'])

    return {
        'id': message_id,
        'from': from_header_value,
        'internal_date': int(internal_date),
        'body': body,
    }


def main():
    # Taken from https://developers.google.com/gmail/api/quickstart/python

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    output_folder = sys.argv[1]
    query = sys.argv[2]
    next_page_token = None
    message_ids = []
    gmail = build('gmail', 'v1', credentials=creds)

    # Get message ids
    while True:
        get_message_ids_result = make_get_message_ids_request(query=query, page_token=next_page_token, gmail=gmail).execute()
        next_page_token = get_message_ids_result['nextPageToken'] if 'nextPageToken' in get_message_ids_result else None

        ids = [message['id'] for message in get_message_ids_result['messages']]

        message_ids = message_ids + ids

        if not next_page_token:
            break

    # Make directory for storing messages
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass

    # Get and store messages
    for message_id in message_ids:
        get_message_by_id_result = make_get_message_by_id_request(id=message_id, gmail=gmail).execute()
        message = make_message(get_message_by_id_result)
        message_id = message['id']

        with open(f'{output_folder}/{message_id}.json', 'w') as message_file:
            json.dump(message, message_file)

        print(message_id)


if __name__ == '__main__':
    main()
