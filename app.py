from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pyttsx3
import os


app = Flask(__name__)
engine = pyttsx3.init()


# データベースへの接続
def connect_db():
    return sqlite3.connect('memo.db')

# データベースの初期化
def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

# メモ一覧を表示
@app.route('/')
def show_memos():
    db = connect_db()
    cur = db.execute('SELECT id, title, content FROM memo ORDER BY id DESC')
    memos = cur.fetchall()
    db.close()
    return render_template('show_memos.html', memos=memos)

# メモの詳細を表示
@app.route('/memo/<int:memo_id>')
def show_memo(memo_id):
    db = connect_db()
    cur = db.execute('SELECT id, title, content FROM memo WHERE id = ?', [memo_id])
    memo = cur.fetchone()
    db.close()

    # 音声ファイルを static フォルダに保存
    audio_file_path = os.path.join('static', 'output.mp3')
    read_aloud(memo[2], audio_file_path)

    return render_template('show_memo.html', memo=memo)

def read_aloud(text, output_file_path):
    # 読み上げ速度
    engine.setProperty('rate', 130) 
    
    # テキストを音声に変換して保存
    engine.save_to_file(text, output_file_path)
    engine.runAndWait()

# メモを追加
@app.route('/add_memo', methods=['GET', 'POST'])
def add_memo():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = connect_db()
        db.execute('INSERT INTO memo (title, content) VALUES (?, ?)', [title, content])
        db.commit()
        db.close()
        return redirect(url_for('show_memos'))
    return render_template('add_memo.html')

#メモを削除
@app.route('/delete_memo/<int:memo_id>')
def delete_memo(memo_id):
    db = connect_db()
    db.execute('DELETE FROM memo WHERE id = ?', [memo_id])
    db.commit()
    db.close()
    return redirect(url_for('show_memos'))


if __name__ == '__main__':
    app.run(debug=True)
    