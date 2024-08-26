# google_drive_uploader/file_uploader.py
import mimetypes
import os

from googleapiclient.http import MediaFileUpload


class FileUploader:
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def upload_file(self, folder_id, file_path, mimetype=None):
        """將指定檔案上傳到指定的資料夾"""
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            return

        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(file_path)
            if mimetype is None:
                print(
                    "Warning: Could not determine the MIME type. Defaulting to 'application/octet-stream'."
                )
                mimetype = "application/octet-stream"

        file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)
        request = self.drive_service.files().create(
            body=file_metadata, media_body=media, fields="id", supportsAllDrives=True
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")

        print(
            f"File '{file_metadata['name']}' uploaded successfully with ID: {response['id']}"
        )
