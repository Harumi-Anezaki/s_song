@echo off
setlocal
cd /d "%~dp0"

echo =========================================
echo Karaoke Song Manager - 環境構築スクリプト
echo =========================================

if exist "bin\python.exe" (
    echo [情報] 既に bin フォルダが存在します。セットアップをスキップします。
    goto :end
)

echo [1/3] Python実行環境をダウンロードしています...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.3/python-3.12.3-embed-amd64.zip' -OutFile 'python-embed.zip'"
if not exist "python-embed.zip" (
    echo [エラー] Pythonのダウンロードに失敗しました。
    pause
    exit /b 1
)

echo [2/3] Python実行環境を展開しています...
powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath 'bin' -Force"
del python-embed.zip

echo [設定] import site を有効化しています...
powershell -Command "(Get-Content 'bin\python312._pth') -replace '#import site', 'import site' | Set-Content 'bin\python312._pth'"

echo [3/3] 依存ライブラリをインストールしています...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
bin\python.exe get-pip.py
del get-pip.py

bin\python.exe -m pip install -r core\requirements.txt

echo =========================================
echo セットアップが完了しました！
echo 今後は run.vbs をダブルクリックしてアプリを起動してください。
echo =========================================
:end
pause
