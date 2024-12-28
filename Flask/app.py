from flask import Flask, send_from_directory, request, jsonify, send_file
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import re

app = Flask(
    __name__,
    static_folder="out",  # React のビルドフォルダを指定
    static_url_path=""      # URL ルートにマッピング
)

# React のルートを提供
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, "index.html")

# React のルーティング対応
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")


# 音声の処理ロジック
def process_audio(url, pitch):
    if int(pitch) == 0:
        return None, "ピッチに0は使用しないでください"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'postprocessor-args': ['-acodec', 'libmp3lame', '-q:a', '4'],
    }
    try:
        # YouTube 音声のダウンロード
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "unknown_title")
            audio_file = ydl.prepare_filename(info)  # ダウンロードしたファイル名を取得
            print(f"タイトル:{video_title}")

        # 音声ファイルの読み込み
        audio = AudioSegment.from_file(audio_file)

        # ピッチ変更
        semitones = int(pitch)
        new_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * (2 ** (semitones / 12.0)))
        }).set_frame_rate(audio.frame_rate)

        # 保存先のファイル名
        if int(pitch) > 0:
            plusminus = "+"
        else:
            plusminus = "-"
        output_file = f"{video_title}{plusminus}{pitch}.mp3"
        print(f"{video_title}{plusminus}{pitch}")
        #output_file = re.sub(r'[\/\\\:\*\?\"<>\|]', '_', output_file)

        # 新しい音声ファイルを保存
        new_audio.export(output_file, format="mp3")

        # ダウンロードした元のファイルを削除
        os.remove(audio_file)

        return output_file, video_title  # ファイルパスを返す

    except Exception as e:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None, str(e)


# API エンドポイント: 音声の処理
@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        url = data.get("URL")
        pitch = data.get("pitch")

        if not url or pitch is None:
            return jsonify({"error": "URL またはピッチが指定されていません"}), 400

        # 音声処理
        output_file, error_message = process_audio(url, pitch)

        if output_file is None:
            return jsonify({"error": error_message}), 400

        # 処理結果を送信
        return send_file(output_file, as_attachment=True, download_name=output_file)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Flask サーバーを起動
if __name__ == "__main__":
    app.run(debug=True)
