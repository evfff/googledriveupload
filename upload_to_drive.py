# pip install google-api-python-client
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import os
import glob
import datetime
import io

# Define the scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Permissions needed to upload and manage files in Google Drive
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Path to the service account credentials file

PARENT_FOLDER_ID = "12uXxBYCP5AVTWlevr3MvsmwHdBwVsuGe"  # ID of the folder in Google Drive where backups will be uploaded

# Directories where backup files are stored
BOT_DB_BACKUP_DIR = '/opt/backup/bot_db/'  # Directory containing bot_db backup files
SITE_DB_BACKUP_DIR = '/opt/backup/site_db/'  # Directory containing site_db backup files

# Parameter to specify the age of files to delete from Google Drive (in days)
FILE_AGE_DAYS = 2  # Number of days to determine the age of files to delete

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB chunks for upload

def authenticate():
    """Authenticate and build the Google Drive service."""
    # Load credentials from the service account file
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # Build the Google Drive service
    return build('drive', 'v3', credentials=creds)

def get_latest_backup_file(directory):
    """Find the latest backup file in the given directory."""
    # Get a list of all .tar.gz files in the specified directory
    files = glob.glob(os.path.join(directory, '*.tar.gz'))
    if not files:
        print(f"No backup files found in {directory}.")
        return None
    # Find the most recently created file
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def chunked_upload(service, file_path, upload_name):
    """Upload a file to Google Drive in chunks."""
    # Metadata for the file
    file_metadata = {
        'name': upload_name,
        'parents': [PARENT_FOLDER_ID]
    }

    # Open the file in binary read mode
    with open(file_path, 'rb') as file:
        # Initiate a MediaIoBaseUpload with chunking enabled
        media = MediaIoBaseUpload(file, mimetype='application/gzip', chunksize=CHUNK_SIZE, resumable=True)

        # Create the file on Google Drive and start chunked upload
        request = service.files().create(body=file_metadata, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}% of {upload_name}")

    print(f"Upload of {upload_name} complete.")

def upload_backup_with_prefix(directory, prefix):
    """Upload the latest backup file with a specific prefix."""
    latest_backup = get_latest_backup_file(directory)
    
    if latest_backup:
        # Get the base file name
        base_name = os.path.basename(latest_backup)
        
        # Create the upload file name with the prefix
        upload_name = f"{prefix}_{base_name}"
        
        # Upload the file to Google Drive in chunks
        service = authenticate()
        chunked_upload(service, latest_backup, upload_name)

def delete_old_backups(directory_prefix):
    """Delete backup files from Google Drive that are older than the specified age for a specific directory."""
    service = authenticate()  # Authenticate and get the Google Drive service

    # Calculate the cutoff date based on the current date minus FILE_AGE_DAYS
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=FILE_AGE_DAYS)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')  # Format the date as a string for the query

    # Query to find files older than the cutoff date with the correct prefix
    query = f"'{PARENT_FOLDER_ID}' in parents and name contains '{directory_prefix}_' and modifiedTime < '{cutoff_date_str}T00:00:00'"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields="nextPageToken, files(id, name, modifiedTime)",
        pageSize=1000  # Adjust as needed
    ).execute()  # Execute the query
    items = results.get('files', [])  # Get the list of files matching the query

    if not items:
        print(f"No backup files older than {FILE_AGE_DAYS} days found for {directory_prefix}.")
        return

    for item in items:
        # Delete the file from Google Drive
        service.files().delete(fileId=item['id']).execute()
        print(f"Deleted file: {item['name']} (ID: {item['id']})")

def main():
    """Main function to handle backup operations."""
    # Upload the latest bot_db backup with prefix
   # upload_backup_with_prefix(BOT_DB_BACKUP_DIR, "bot_db")

    # Upload the latest site_db backup with prefix
    upload_backup_with_prefix(SITE_DB_BACKUP_DIR, "site_db")

    # Delete old backup files from Google Drive for both bot_db and site_db
    delete_old_backups("bot_db")
    delete_old_backups("site_db")

if __name__ == '__main__':
    main()
