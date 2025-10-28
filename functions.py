import streamlit as st
import os
import time
from pathlib import Path
import wave
import pyaudio
import subprocess
import numpy as np
from scipy.io.wavfile import write
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
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
        with open(audio_input_file_path, "wb") as f:
            f.write(audio_bytes)
        st.success("✅ 音声が保存されました！")
    else:
        st.stop()


def transcribe_audio(audio_input_file_path):
    """
    音声入力ファイルから文字起こしテキストを取得
    Args:
        audio_input_file_path: 音声入力ファイルのパス
    """

    with open(audio_input_file_path, 'rb') as audio_input_file:
        transcript = st.session_state.openai_obj.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input_file,
            language="en"
        )

    # 音声入力ファイルを削除
    os.remove(audio_input_file_path)

    return transcript


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
    音声ファイルの読み上げ
    Args:
        audio_output_file_path: 音声ファイルのパス
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
    """

    # waveモジュールでファイルを開いて再生
    with wave.open(audio_output_file_path, 'rb') as play_target_file:
        p = pyaudio.PyAudio()

        # 再生ストリームを開く
        stream = p.open(
            format=p.get_format_from_width(play_target_file.getsampwidth()),
            channels=play_target_file.getnchannels(),
            rate=int(play_target_file.getframerate() * speed),
            output=True
        )

        data = play_target_file.readframes(1024)
        while data:
            stream.write(data)
            data = play_target_file.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()

    # 再生後にwavファイル削除
    os.remove(audio_output_file_path)


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
