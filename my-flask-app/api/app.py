from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
from flask import jsonify, request, send_file
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # すべてのオリジンから許可


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
        
        # 新しい音声ファイルを保存
        new_audio.export(output_file, format="mp3")

        # ダウンロードした元のファイルを削除
        os.remove(audio_file)

        return output_file, video_title  # ファイルパスを返す

    except Exception as e:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None, str(e)

# サーバーレス関数としてFlaskを使う
def handler(request):
    try:
        data = request.get_json()
        url = data.get("URL")
        pitch = data.get("pitch")

        if not url or pitch is None:
            return jsonify({"error": "URL またはピッチが指定されていません"}), 400

        # 音声処理
        output_file, error_message = process_audio(url, pitch)

        if output_file is None:
            return jsonify({"error": error_message}), 400

        # 処理した音声ファイルを返す
        return send_file(output_file, as_attachment=True, download_name=output_file)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
