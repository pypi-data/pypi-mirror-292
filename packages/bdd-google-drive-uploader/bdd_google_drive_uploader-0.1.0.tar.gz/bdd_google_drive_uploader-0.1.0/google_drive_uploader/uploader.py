# google_drive_uploader/uploader.py
from google_drive_uploader.auth import AuthManager
from google_drive_uploader.drive_manager import DriveManager
from google_drive_uploader.file_uploader import FileUploader


class GoogleDriveUploader:
    def __init__(
        self, credentials_json="credentials.json", credentials_pickle="token.pickle"
    ):
        self.auth_manager = AuthManager(credentials_json, credentials_pickle)
        self.drive_manager = DriveManager(self.auth_manager.creds)
        self.file_uploader = FileUploader(self.drive_manager.drive_service)

    def upload_to_drive(self, drive_name, folder_path, file_path, mimetype=None):
        """整合方法：列出共用雲端硬碟、找到目標資料夾並上傳檔案"""
        drive_id = self.drive_manager.list_shared_drives(drive_name)
        if drive_id:
            target_folder_id = self.drive_manager.find_folder_by_path(
                drive_id, folder_path
            )
            if target_folder_id:
                print(f"Ready to upload to folder ID: {target_folder_id}")
                self.file_uploader.upload_file(target_folder_id, file_path, mimetype)
            else:
                print("Target folder not found or inaccessible.")
        else:
            print("Shared drive not found.")
