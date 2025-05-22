from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = 'absolute-keel-460616-g2-381e10284818.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)

FOLDER_ID = '1WX54Z6xGPIymu4DFvPgTLX8_0zsWD3V3'  # Your shared folder ID

def upload_to_drive(file_path, file_name, folder_id=FOLDER_ID):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='audio/mpeg')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Make file public
    drive_service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    # Return sharable download link
    return f"https://drive.google.com/uc?id={file['id']}&export=download"

