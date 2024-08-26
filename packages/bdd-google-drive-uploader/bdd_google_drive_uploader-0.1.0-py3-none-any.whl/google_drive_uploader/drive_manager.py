# google_drive_uploader/drive_manager.py
from googleapiclient.discovery import build


class DriveManager:
    def __init__(self, creds):
        self.drive_service = build("drive", "v3", credentials=creds)

    def list_shared_drives(self, query=None):
        """列出所有共用雲端硬碟，並根據查詢篩選結果"""
        results = self.drive_service.drives().list(pageSize=10).execute()
        shared_drives = results.get("drives", [])

        if not shared_drives:
            print("No shared drives found.")
            return None

        for drive in shared_drives:
            if not query or query == drive["name"]:
                print(f"{drive['name']} (ID: {drive['id']})")
                return drive["id"]
        return None

    def find_folder_by_path(self, drive_id, folder_path):
        """根據資料夾路徑在共用雲端硬碟中找到最終目標資料夾的 ID"""
        folder_names = folder_path.split("/")
        parent_folder_id = drive_id
        for folder_name in folder_names:
            query = (
                f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' "
                f"and trashed=false and name='{folder_name}'"
            )
            results = (
                self.drive_service.files()
                .list(
                    q=query,
                    spaces="drive",
                    corpora="drive",
                    driveId=drive_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="nextPageToken, files(id, name)",
                )
                .execute()
            )

            folders = results.get("files", [])
            if not folders:
                print(
                    f"No subfolder named '{folder_name}' found in folder ID {parent_folder_id}."
                )
                return None
            else:
                folder = folders[0]
                print(f"Subfolder '{folder['name']}' found with ID: {folder['id']}")
                parent_folder_id = folder["id"]

        return parent_folder_id
