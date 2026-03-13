from piper.voice import PiperVoice
import sounddevice as sd
import numpy as np
from pathlib import Path
import os

import unicodedata
import re

def clean_for_tts(text: str) -> str:
    allowed_symbols = set("°%.,:-+/() ")

    cleaned = []

    for ch in text:
        cat = unicodedata.category(ch)

        # Keep letters and numbers
        if cat.startswith(("L", "N")):
            cleaned.append(ch)

        # Keep allowed symbols
        elif ch in allowed_symbols:
            cleaned.append(ch)

        elif ch.isspace():
            cleaned.append(" ")

    result = "".join(cleaned)

    # remove extra spaces
    result = re.sub(r"\s+", " ", result).strip()

    return result


BASE_DIR = Path(__file__).resolve().parent

tts_model=PiperVoice.load(model_path=os.path.join(BASE_DIR,"voices/","en_US-lessac-medium.onnx"),config_path=os.path.join(BASE_DIR,"voices/","en_US-lessac-medium.onnx.json"))

def speak(input:str):
    audio=tts_model.synthesize(clean_for_tts(input))
    stream_audio_playback:sd.OutputStream=None
    for chunk in audio:
        audio_play=np.frombuffer(chunk.audio_int16_bytes,dtype=np.int16)
        if stream_audio_playback is None:
            stream_audio_playback=sd.OutputStream(
                samplerate=chunk.sample_rate,
                channels=chunk.sample_channels,
                dtype="int16"
            )
            stream_audio_playback.start()
        stream_audio_playback.write(audio_play)
    if stream_audio_playback:
        stream_audio_playback.stop()
        stream_audio_playback.close()


if __name__=="__main__":
    speak("Hello rohan batra")