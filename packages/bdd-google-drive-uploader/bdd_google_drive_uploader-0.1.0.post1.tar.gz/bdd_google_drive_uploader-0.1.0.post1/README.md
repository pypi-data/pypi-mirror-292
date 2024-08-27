
# Google Drive Uploader

Google Drive Uploader 是一個簡單的工具，用於將文件上傳到 Google Drive，。這個工具提供了一個簡單的 Python API，可以方便地集成到您的自動化腳本和應用程序中。

## PyPI url
https://pypi.org/project/bdd-google-drive-uploader/

## 功能

- 身份驗證管理
- 列出和搜索 Google Drive 上的共用雲端硬碟
- 根據資料夾路徑查找特定資料夾的 ID
- 將檔案上傳到指定的 Google Drive 資料夾

## 安裝

您可以通過 Python 的包管理工具 Poetry 來安裝 Google Drive Uploader：

```bash
poetry add google-drive-uploader
```

或者，如果您使用的是 pip，請先確保您的環境中安裝了 Poetry，然後運行以下命令：

```bash
pip install google-drive-uploader
```

## 快速入門

以下是一個如何使用 Google Drive Uploader 的簡單範例：

```python
from google_drive_uploader import GoogleDriveUploader

# 初始化 uploader
uploader = GoogleDriveUploader()

# 上傳檔案到指定的 Google Drive 資料夾
drive_name = "YourDriveName"
folder_path = "path/to/your/folder"
file_path = "path/to/your/file.txt"
uploader.upload_to_drive(drive_name, folder_path, file_path)
```

請確保您已經在本地配置了 `credentials.json` 文件，並且您的 Google API 應用程序有足夠的權限來訪問 Google Drive。

## 配置

您可以在初始化 `GoogleDriveUploader` 時提供 `credentials_json` 和 `credentials_pickle` 來自訂您的身份驗證憑證存放路徑：

```python
uploader = GoogleDriveUploader(credentials_json="path/to/your/credentials.json")
```
如此一來，首次實作`GoogleDriveUploader`就可以依照產生的網址進行認證，認證完成後，就可以獲得可復用的 `token.pkl`。