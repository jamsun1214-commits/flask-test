import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

app = Flask(__name__)

# アップロードされたファイルを保存するフォルダの指定
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 保存先フォルダがなければ自動で作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 1. トップページ：ファイルの一覧を表示
@app.route('/')
def index():
    # uploadsフォルダの中にあるファイル名の一覧を取得
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

# 2. ファイルアップロード処理
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # フォルダにファイルを保存
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('index'))

# 3. ファイルを表示・ダウンロードする処理
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 4. ファイル削除処理
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path) # ファイルを削除
        return "暗証番号なしで削除に成功しました", 200
    else:
        return "ファイルが見つかりません", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)