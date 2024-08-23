import os
import subprocess
from gtts import gTTS
import pyaudio
import wave
import speech_recognition as sr
import pygame
import sounddevice as sd

def play_audio(pro_path="", mp3_file_path=""):
    """
    Plays an audio file using a specified program.

    Args:
    - pro_path: Path to the program to use for playing the audio.
    - mp3_file_path: Path to the MP3 file to play.

    Returns:
    - 'opened' if successful.
    - 'Not Found File' if the file does not exist.
    """
    if os.path.exists(mp3_file_path):
        subprocess.Popen([pro_path, mp3_file_path])
        return "opened"
    else:
        return "Not Found File"

def play_sound(filename="tts.mp3"):
    """
    Plays a sound file using pygame.

    Args:
    - filename: Path to the sound file (MP3).

    Returns:
    - 'played' if successful.
    """
    pygame.mixer.init()
    sound = pygame.mixer.Sound(filename)
    sound.play()
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)
    sound.stop()
    return "played"


def play_audio_online(pro_path="", mp3_file_link=""):
    """
    Plays an online audio file using a specified program.

    Args:
    - pro_path: Path to the program to use for playing the audio.
    - mp3_file_link: URL or link to the MP3 file to play.

    Returns:
    - 'opened' if successful.
    """
    subprocess.Popen([pro_path, mp3_file_link])
    return "opened"
    

def record_audio(filename="recorder.wav", duration=5, fs=44100, device_number=None):
    """
    Records audio using the default or specified audio device.

    Args:
    - filename: Name of the WAV file to save the recorded audio.
    - duration: Duration of the recording in seconds.
    - fs: Sampling frequency (default: 44100).
    - device_number: Optional device number to record from.

    Returns:
    - 'saved' if successful.
    - Error message if unsuccessful.
    """
    if device_number is not None:
        sd.default.device = device_number
    try:
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())
        return "saved"
    except Exception as e:
        print("An error occurred:", e)
        return "An error occurred:", e
    

def transcribe_audio(filename="recorder.wav", language_="en-US"):
    """
    Transcribes audio from a WAV file using Google Speech Recognition.

    Args:
    - filename: Path to the WAV file to transcribe.
    - language_: Language code for the language spoken (default: 'en-US').

    Returns:
    - Transcribed text if successful.
    - Empty string if no speech detected or unrecognized.
    - Error message if unsuccessful.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            query = recognizer.recognize_google(audio, language=language_)
            return query
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return f"Could not request results; {e}"
        

def stop_recording():
    """
    Stops recording audio by terminating PyAudio instances.
    """
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        p.terminate()
        

def text_to_speech(text="", filename="tts.mp3", language='en'):
    """
    Converts text to speech and saves it as an MP3 file using gTTS.

    Args:
    - text: Text to convert to speech.
    - filename: Name of the output MP3 file.
    - language: Language code for the language spoken (default: 'en').

    Returns:
    - 'saved' if successful.
    """
    tts = gTTS(text, lang=language)
    tts.save(filename)
    return "saved"
