# Karaoke Song Manager

[日本語 (Japanese)](docs/README_ja.md) | [中文 (Chinese)](docs/README_zh.md)

A local web application that helps you manage and curate karaoke songs from YouTube videos, complete with a self-contained portable Python environment.

## Features
- Fully portable: Runs on Windows without installing Python globally.
- Clean Architecture: Backend hidden in `core/` to prevent accidental deletion.
- Background Server: Starts silently via VBScript without flashing command prompt windows.
- Notion-like UI: Manage songs, view counts, tags, and DL status in a beautiful SPA interface.
- Inline Tag Customization: Directly rename tags in the dropdown menus using the 3-dot menu.
- Spreadsheet-like Experience: Supports cell drag-and-drop fill, and bulk operations.

## Initial Setup
1. Edit `config.json` and insert your YouTube Data API v3 key (`YOUTUBE_API_KEY`).
2. Double-click **`setup.bat`**. This will automatically download and set up a lightweight, isolated Python environment in the `bin/` directory and install all required libraries. (You only need to do this once).

## How to Run
Double-click **`run.vbs`**.
- It will silently start the server in the background and open the app in your default browser at `http://127.0.0.1:5000`.
- To safely shut down the server, go to the "設定とバックアップ" (Settings & Backup) tab in the app and click the "サーバーを終了する" (Shutdown Server) button.

## Uninstallation
Simply delete the entire application folder. It does not modify system registries or global environment variables.
