import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
import requests
from moviepy.editor import AudioFileClip
from groq import Groq
import threading
import time
import tkinter as tk
from tkinter import scrolledtext
import queue
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo key.env
load_dotenv('key.env')

# Configura tus claves API como variables de entorno
os.environ["DEEPGRAM_API_KEY"] = os.getenv('DEEPGRAM_API_KEY')
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

# Inicializa el cliente de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Configuración de parámetros
RATE = 44100  # Tasa de muestreo (Hz)
RECORD_SECONDS = 5  # Duración de la grabación
is_recording = False  # Variable para controlar el estado de la grabación

# Directorio para almacenar las grabaciones
recordings_dir = "grabaciones"
if not os.path.exists(recordings_dir):
    os.makedirs(recordings_dir)

# Listar todos los dispositivos de entrada
devices = sd.query_devices()
valid_device_index = None
max_channels = 0

for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        valid_device_index = i
        max_channels = device['max_input_channels']
        break

if valid_device_index is None:
    raise ValueError("No se encontró ningún dispositivo de entrada válido con canales de entrada.")

# Cola para almacenar las grabaciones para procesamiento
audio_queue = queue.Queue()

# Función para grabar audio en fragmentos continuos con solapamiento mayor
def record_audio():
    global is_recording
    while is_recording:
        file_name = os.path.join(recordings_dir, f"grabacion_{time.time()}.wav")
        recording = sd.rec(int(RECORD_SECONDS * RATE), samplerate=RATE, channels=max_channels, dtype='int16', device=valid_device_index)
        sd.wait()
        write(file_name, RATE, recording)
        audio_queue.put(file_name)
        time.sleep(0.5)  # Aumentar el solapamiento a 0.5 segundos

# Función para convertir el archivo de audio a formato WAV usando moviepy
def convert_audio_to_wav(audio_path):
    audio_clip = AudioFileClip(audio_path)
    wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
    audio_clip.write_audiofile(wav_path, codec='pcm_s16le')
    return wav_path

# Función para transcribir audio usando Deepgram
def transcribe_audio_deepgram(audio_path):
    wav_path = convert_audio_to_wav(audio_path)
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {os.environ.get('DEEPGRAM_API_KEY')}",
        "Content-Type": "audio/wav"
    }
    with open(wav_path, 'rb') as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['results']['channels'][0]['alternatives'][0]['transcript']
    else:
        return None

# Función para traducir texto usando la API de Groq
def translate_text_groq(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Translate the received text to Spanish. DO NOT reply anything else but the text."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return None

# Función para manejar el procesamiento de audio
def process_audio():
    while True:
        file_name = audio_queue.get()
        transcript = transcribe_audio_deepgram(file_name)
        if transcript:
            translated_text = translate_text_groq(transcript)
            update_text(transcript, translated_text)
        os.remove(file_name)

# Función para actualizar el texto en la interfaz gráfica
def update_text(transcript, translated_text):
    transcript_text.config(state=tk.NORMAL)
    transcript_text.insert(tk.END, f"Transcripción: {transcript}\nTraducción: {translated_text}\n\n")
    transcript_text.config(state=tk.DISABLED)
    transcript_text.see(tk.END)

# Función para iniciar la grabación
def start_recording():
    global is_recording
    is_recording = True
    threading.Thread(target=record_audio).start()

# Función para detener la grabación
def stop_recording():
    global is_recording
    is_recording = False

# Configurar la interfaz gráfica
root = tk.Tk()
root.title("Transcripción y Traducción en Tiempo Real")
root.geometry("1000x200")
root.configure(bg='white')

frame = tk.Frame(root, bg='white')
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

buttons_frame = tk.Frame(frame, bg='white')
buttons_frame.pack(side=tk.LEFT, padx=10, pady=10)

start_button = tk.Button(buttons_frame, text="Iniciar", command=start_recording, bg='lightgray')
start_button.pack(pady=5)

stop_button = tk.Button(buttons_frame, text="Detener", command=stop_recording, bg='lightgray')
stop_button.pack(pady=5)

transcript_text = scrolledtext.ScrolledText(frame, width=60, height=20, state=tk.DISABLED, bg='white', wrap=tk.WORD)
transcript_text.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Iniciar el thread de procesamiento de audio
threading.Thread(target=process_audio, daemon=True).start()

root.mainloop()
