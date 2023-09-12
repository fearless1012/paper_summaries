from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pandas as pd
import PyPDF2
import gdown
import requests

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_files_in_folder(parent_id, service):
    query = f"'{parent_id}' in parents and trashed=false"
    response = service.files().list(q=query, fields='files(name,id,mimeType,webViewLink,createdTime,modifiedTime)').execute()
    files = response.get('files', [])
    dfs = [pd.DataFrame(files)]
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            dfs.append(get_files_in_folder(file['id'], service))
        elif file['mimeType'] == 'application/pdf':
            request = service.files().get_media(fileId=file['id']).execute()
            with open('./temp_dir/' + file['name'], 'wb') as f:
                f.write(request)
    return pd.concat(dfs, ignore_index=True)


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # try:
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    files_data = []
    files = pd.DataFrame(files_data)

    if not items:
        print('No files found.')
        return
    print('Files:')
    for item in items:
        df = get_files_in_folder(item['id'], service)
        files = pd.concat([files, df], ignore_index=True)
        print(len(files))

    files = files.drop(files.query("mimeType != 'application/pdf'").index)
    files.reset_index(drop=True, inplace = True)

    files.to_csv("Phishing_Papers.csv")

    # if not os.path.exists("./temp_dir"):
    #     os.makedirs("./temp_dir")


    # for ind in files.index:
    #     print(files['id'][ind])
    #     file_id = files['id'][ind]
    #     file_name = files['name'][ind]
    #     request = service.files().get_media(fileId=file_id)
    #     with open('./temp_dir/' + file_name, 'wb') as f:
    #         f.write(request.execute())

    # print(u'{0} ({1})'.format(item['name'], ))
    # except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
    # print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()