# import streamlit as st
# import os
# import time
# from pathlib import Path
# import wave
# import pyaudio
# import subprocess
# import numpy as np
# from scipy.io.wavfile import write
# from langchain.prompts import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )
# from langchain.schema import SystemMessage
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain_openai import ChatOpenAI
# from langchain.chains import ConversationChain
# import constants as ct
import streamlit as st
import os
import time
import io
from pathlib import Path
import subprocess

from pydub import AudioSegment, silence
from streamlit_webrtc import webrtc_streamer, WebRtcMode

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

import constants as ct


def record_audio(audio_input_file_path):
    """
    🎤 Streamlit標準のst.audio_inputを使用して音声を録音・保存する関数
    Args:
        audio_input_file_path: 保存先のファイルパス
    """

    st.info("下のマイクボタンを押して話してください。録音後、自動で保存されます。")

    # Streamlit標準の音声入力コンポーネント
    audio_bytes = st.audio_input("🎙️ 音声を録音してください")

    # 録音された場合のみ保存
    if audio_bytes:
        # ✅ UploadedFile なので read() で bytes データを取得する
        audio_data = audio_bytes.read()

        # ファイルにバイナリで書き込む
        with open(audio_input_file_path, "wb") as f:
            f.write(audio_data)

        st.success("✅ 音声が保存されました！")
    else:
        st.stop()



# def record_audio(audio_input_file_path):
#     """
#     🎤 Streamlit標準のst.audio_inputを使用して音声を録音・保存する関数
#     Args:
#         audio_input_file_path: 保存先のファイルパス
#     """

#     st.info("下のマイクボタンを押して話してください。録音後、自動で保存されます。")

#     # Streamlit標準の音声入力コンポーネント
#     audio_bytes = st.audio_input("🎙️ 音声を録音してください")

#     # 録音された場合のみ保存
#     if audio_bytes:
#         with open(audio_input_file_path, "wb") as f:
#             f.write(audio_bytes)
#         st.success("✅ 音声が保存されました！")
#     else:
#         st.stop()

def transcribe_audio(audio_input_file_path):
    """
    既存モード用：音声ファイルから文字起こし（その後ファイル削除）
    """
    with open(audio_input_file_path, "rb") as audio_input_file:
        transcript = st.session_state.openai_obj.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input_file,
            language="en"
        )
    os.remove(audio_input_file_path)
    return transcript


def transcribe_audio_buffer(audio_buffer):
    """
    自動会話モード用：BytesIO上の音声データをWhisperで文字起こし
    """
    audio_buffer.seek(0)
    transcript = st.session_state.openai_obj.audio.transcriptions.create(
        model="whisper-1",
        file=audio_buffer,
        language="en"
    )
    return transcript.text.strip()


# def transcribe_audio(audio_input_file_path):
#     """
#     音声入力ファイルから文字起こしテキストを取得
#     Args:
#         audio_input_file_path: 音声入力ファイルのパス
#     """

#     with open(audio_input_file_path, 'rb') as audio_input_file:
#         transcript = st.session_state.openai_obj.audio.transcriptions.create(
#             model="whisper-1",
#             file=audio_input_file,
#             language="en"
#         )

#     # 音声入力ファイルを削除
#     os.remove(audio_input_file_path)

#     return transcript


def save_to_wav(llm_response_audio, audio_output_file_path):
    """
    pydubを使わずにffmpegコマンドでmp3→wav変換する関数
    Args:
        llm_response_audio: LLMからの回答の音声データ
        audio_output_file_path: 出力先のファイルパス
    """

    # 一時的にmp3ファイルを作成
    temp_audio_output_filename = f"{ct.AUDIO_OUTPUT_DIR}/temp_audio_output_{int(time.time())}.mp3"
    with open(temp_audio_output_filename, "wb") as temp_audio_output_file:
        temp_audio_output_file.write(llm_response_audio)

    # ffmpegでmp3→wav変換
    subprocess.run(
        ["ffmpeg", "-y", "-i", temp_audio_output_filename, audio_output_file_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 一時ファイル削除
    os.remove(temp_audio_output_filename)


def play_wav(audio_output_file_path, speed=1.0):
    """
    音声ファイルをブラウザ上で再生（PyAudio非依存版）
    Cloud環境でも動作可能。
    Args:
        audio_output_file_path: 音声ファイルのパス
        speed: 再生速度（未使用・将来対応用）
    """

    try:
        # 🔹 WAVファイルをバイナリで読み込む
        with open(audio_output_file_path, "rb") as f:
            audio_bytes = f.read()

        # 🔹 Streamlitでブラウザ再生（クラウド対応）
        st.audio(audio_bytes, format="audio/wav")

        # 🔹 再生後にファイル削除（不要ならこの行をコメントアウト）
        if os.path.exists(audio_output_file_path):
            os.remove(audio_output_file_path)

    except Exception as e:
        st.error(f"音声の再生中にエラーが発生しました: {e}")


# def play_wav(audio_output_file_path, speed=1.0):
#     """
#     音声ファイルの読み上げ
#     Args:
#         audio_output_file_path: 音声ファイルのパス
#         speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
#     """

#     # waveモジュールでファイルを開いて再生
#     with wave.open(audio_output_file_path, 'rb') as play_target_file:
#         p = pyaudio.PyAudio()

#         # 再生ストリームを開く
#         stream = p.open(
#             format=p.get_format_from_width(play_target_file.getsampwidth()),
#             channels=play_target_file.getnchannels(),
#             rate=int(play_target_file.getframerate() * speed),
#             output=True
#         )

#         data = play_target_file.readframes(1024)
#         while data:
#             stream.write(data)
#             data = play_target_file.readframes(1024)

#         stream.stop_stream()
#         stream.close()
#         p.terminate()

#     # 再生後にwavファイル削除
#     os.remove(audio_output_file_path)


def create_chain(system_template):
    """
    LLMによる回答生成用のChain作成
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_template),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    chain = ConversationChain(
        llm=st.session_state.llm,
        memory=st.session_state.memory,
        prompt=prompt
    )

    return chain


def create_problem_and_play_audio():
    """
    問題生成と音声ファイルの再生
    Args:
        chain: 問題文生成用のChain
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
        openai_obj: OpenAIのオブジェクト
    """

    # 問題文を生成するChainを実行し、問題文を取得
    problem = st.session_state.chain_create_problem.predict(input="")

    # LLMからの回答を音声データに変換
    llm_response_audio = st.session_state.openai_obj.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=problem
    )

    # 音声ファイルの作成
    audio_output_file_path = f"{ct.AUDIO_OUTPUT_DIR}/audio_output_{int(time.time())}.wav"
    save_to_wav(llm_response_audio.content, audio_output_file_path)

    # 音声ファイルの読み上げ
    play_wav(audio_output_file_path, st.session_state.speed)

    return problem, llm_response_audio


def create_evaluation():
    """
    ユーザー入力値の評価生成
    """

    llm_response_evaluation = st.session_state.chain_evaluation.predict(input="")

    return llm_response_evaluation


def record_until_silence(
    timeout_sec: int = 3,
    min_silence_len_ms: int = 800,
    silence_thresh_dbfs: int = -40,
):
    """
    🎤 自動英会話モード用（クラウド対応版）：
    - ローカル環境では streamlit-webrtc で自動録音
    - Streamlit Cloud など webrtc_streamer が使えない環境では st.audio_input を使用
    戻り値:
        BytesIO (wav形式) or None（音声が取れなかった場合）
    """

    # --- 🔍 まずは webrtc が使えるかどうか確認 ---
    try:
        from streamlit_webrtc import webrtc_streamer, WebRtcMode
        webrtc_available = True
    except Exception:
        webrtc_available = False

    # --- ☁️ Streamlit Cloud fallback ---
    if not webrtc_available or is_cloud:
        st.info("🎤 下のマイクボタンを押して話してください。話し終えたら自動で認識します。")

        audio = st.audio_input("🎙️ 音声を録音")
        if audio is None:
            st.warning("録音を待っています...")
            return None

        buf = io.BytesIO(audio.read())
        buf.seek(0)
        st.success("✅ 音声を取得しました！（Cloudモード）")
        return buf

    # --- 🖥️ ローカルモード（webrtc対応） ---
    st.info("🎤 話してください。話し終えて約3秒黙ると、自動でAIが返答します。")

    # ✅ webrtc_streamer をセッション内で1回だけ初期化
    if "webrtc_ctx" not in st.session_state:
        st.session_state.webrtc_ctx = webrtc_streamer(
            key="auto_conversation",
            mode=WebRtcMode.RECVONLY,
            media_stream_constraints={"audio": True, "video": False},
        )

    webrtc_ctx = st.session_state.webrtc_ctx

    if not webrtc_ctx.audio_receiver:
        st.warning("マイク接続待機中です...")
        return None

    audio_bytes = b""
    last_voice_time = time.time()
    started = False

    while True:
        try:
            frame = webrtc_ctx.audio_receiver.get_frame(timeout=1)
        except:
            break

        if frame is None:
            if started and (time.time() - last_voice_time) > timeout_sec:
                break
            continue

        segment = AudioSegment(
            frame.to_ndarray().tobytes(),
            sample_width=2,
            frame_rate=frame.sample_rate,
            channels=1,
        )
        audio_bytes += segment.raw_data
        started = True

        sound = AudioSegment(
            data=audio_bytes,
            sample_width=2,
            frame_rate=frame.sample_rate,
            channels=1,
        )
        nonsilent = silence.detect_nonsilent(
            sound,
            min_silence_len=min_silence_len_ms,
            silence_thresh=silence_thresh_dbfs,
        )

        if nonsilent:
            last_voice_end_ms = nonsilent[-1][1]
            last_voice_time = time.time() - (len(sound) - last_voice_end_ms) / 1000.0

        if started and (time.time() - last_voice_time) > timeout_sec:
            break

    if not audio_bytes:
        return None

    buf = io.BytesIO()
    final = AudioSegment(
        data=audio_bytes,
        sample_width=2,
        frame_rate=16000,
        channels=1,
    )
    final.export(buf, format="wav")
    buf.seek(0)

    st.success("🛑 録音終了（自動検知・ローカルモード）")
    return buf





def generate_ai_response_auto(user_text: str):
    """
    自動英会話モード用：
    - 会話履歴つきでAI応答を生成
    - TTSで音声も生成
    戻り値:
        (ai_text: str, audio_bytes: bytes)
    """

    # すでに main.py 側で st.session_state.llm / memory は用意している想定
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You are a friendly English conversation partner. "
                "Keep responses concise and natural. Correct the user's English gently within the reply."
            )
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

    chain = ConversationChain(
        llm=st.session_state.llm,
        memory=st.session_state.memory,
        prompt=prompt,
    )

    ai_text = chain.predict(input=user_text)

    tts_res = st.session_state.openai_obj.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=ai_text,
    )

    # OpenAI SDKのresponseは .content or .read() でバイト列取得（環境に合わせて）
    audio_bytes = tts_res.content if hasattr(tts_res, "content") else tts_res.read()

    return ai_text, audio_bytes
