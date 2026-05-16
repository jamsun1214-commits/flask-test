import os
import json
import io
from flask import Flask, send_file, render_template_string
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)

# 🔑 Google Drive APIに接続するための認証関数
def get_drive_service():
    # 【本番環境（Render）用】環境変数からJSONの文字列を読み込む
    render_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    
    if render_creds:
        info = json.loads(render_creds)
        creds = service_account.Credentials.from_service_account_info(info)
    else:
        # 【ローカル環境（あなたのPC）用】フォルダ内の secret-key.json を読み込む
        json_path = os.path.join(os.path.dirname(__file__), 'secret-key.json')
        if os.path.exists(json_path):
            creds = service_account.Credentials.from_service_account_file(json_path)
        else:
            raise Exception("認証用のJSON鍵（secret-key.json）が見つかりません。")
            
    # ドライブAPIを操作するサービスを作成（読み取り専用権限）
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    creds = creds.with_scopes(scopes)
    return build('drive', 'v3', credentials=creds)


# 🏠 1. トップページ
@app.route('/')
def index():
    # 簡単なテスト画面をHTMLで表示
    return """
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>🔮 Googleドライブ画像読み込みテスト</h1>
        <p>下のボタンを押すと、プログラムがあなたのGoogleドライブから「testimage.png」を探して表示します。</p>
        <p style="color: gray; font-size: 12px;">（Renderが眠っても画像は消えません）</p>
        <br>
        <a href="/view-image"><button style="padding: 10px 20px; font-size: 16px; cursor: pointer;">画像を読み込む</button></a>
    </div>
    """


# 🖼️ 2. Googleドライブから画像をダウンロードしてブラウザに返す処理
@app.route('/view-image')
def view_image():
    try:
        service = get_drive_service()
        
        # 【処理A】ロボットがアクセスできるファイルから「testimage.png」を検索
        results = service.files().list(
            q="name = 'testimage.png' and trashed = false",
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            return """
            <h3>❌ 画像が見つかりませんでした。</h3>
            <p>以下の原因が考えられます：</p>
            <ul>
                <li>Googleドライブに「testimage.png」という名前で保存されていない</li>
                <li>フォルダの共有設定に、ロボットのメールアドレスを追加し忘れている</li>
            </ul>
            <a href="/">戻る</a>
            """, 404
            
        # 見つかった最初のファイルのIDと種類（MimeType）を取得
        file_id = files[0]['id']
        mime_type = files[0].get('mimeType', 'image/png')
        
        # 【処理B】ファイルをバイナリデータ（データそのもの）としてダウンロード
        request_media = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request_media)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        # データの読み込み位置を先頭に戻す
        file_stream.seek(0)
        
        # 【処理C】画像をそのままブラウザに「画像ファイル」として出力
        return send_file(file_stream, mimetype=mime_type)
        
    except Exception as e:
        return f"<h3>❌ エラーが発生しました</h3><p>{str(e)}</p><a href='/'>戻る</a>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)