import json
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import threading
import numpy as np
import tkinter as tk
from tkinter import filedialog

class TranscriptionThread(threading.Thread):
    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.result = None

    def run(self):
        try:
            # Load the audio file
            audio = AudioSegment.from_file(self.input_file)

            # Compress audio to MP3 format
            compressed_file = Path(self.input_file + ".mp3")
            audio.export(compressed_file, format="mp3")

            # Convert compressed audio to raw data
            compressed_audio = AudioSegment.from_file(compressed_file)
            compressed_audio_raw = np.array(compressed_audio.get_array_of_samples())

            # Transcribe audio using the Google Web Speech API
            recognizer = sr.Recognizer()
            sample_width = compressed_audio.sample_width
            frame_rate = compressed_audio.frame_rate
            audio_sr = sr.AudioData(compressed_audio_raw.tobytes(), sample_rate=frame_rate, sample_width=sample_width)
            text = recognizer.recognize_google(audio_sr)

            # Extract phonemes and timings, including silence (" ") when nothing is being said
            phonemes = []
            current_time = 0.0
            for word in text.split():
                phoneme_duration = len(word) * (1000 / frame_rate)  # Duration in milliseconds
                for phoneme in word:
                    phoneme_data = {'phoneme': phoneme, 'starts': current_time}
                    phonemes.append(phoneme_data)
                    current_time += phoneme_duration

                # Add silence timing (" ") between words
                if word != text.split()[-1]:
                    silence_duration = (len(" ") * (1000 / frame_rate))  # Duration in milliseconds
                    phoneme_data = {'phoneme': " ", 'starts': current_time}
                    phonemes.append(phoneme_data)
                    current_time += silence_duration

            # Adjust the final timing based on the actual audio duration
            total_audio_duration = len(compressed_audio) / 1000.0  # Duration in seconds
            timing_adjustment = total_audio_duration / current_time
            for phoneme_data in phonemes:
                phoneme_data['starts'] *= timing_adjustment

            self.result = phonemes

        except Exception as e:
            print(f"Error during transcription: {str(e)}")

        finally:
            # Clean up the compressed file
            if compressed_file.exists():
                compressed_file.unlink()


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
    selected_file_label.config(text=file_path)

def select_output_path():
    output_path = filedialog.askdirectory()
    selected_output_label.config(text=output_path)

def phonemize():
    input_file = selected_file_label.cget("text")
    output_path = selected_output_label.cget("text")

    if input_file and output_path:
        # Create the transcription thread
        transcription_thread = TranscriptionThread(input_file, output_path)

        # Start the transcription thread
        transcription_thread.start()

        # Wait for the transcription thread to finish
        transcription_thread.join()

        # Get the transcribed phonemes
        phonemes = transcription_thread.result

        # Convert the phonemes list to a NumPy array
        phonemes_array = np.array(phonemes)

        # Specify the output JSON file path
        output_file = output_path + "/outputPhonemesTHREADING.json"

        # Export to JSON using a context manager
        try:
            with open(output_file, 'w') as json_file:
                json.dump(phonemes_array.tolist(), json_file)
            print("Phonemes exported to JSON successfully.")

            # Read the JSON file and check if it is empty
            with open(output_file) as json_file:
                data = json.load(json_file)
                if not data:
                    error_label.config(text="Audio didn't phonemize. Try using a higher quality audio.")
                else:
                    error_label.config(text="")

        except Exception as e:
            print(f"Error exporting phonemes to JSON: {str(e)}")

# Create the Tkinter window
window = tk.Tk()
window.title("Phoneme Extractor")

# Set the window size
window.geometry("450x250")
window.iconbitmap("wahhhh.ico")

# Create the file selection button
select_file_button = tk.Button(window, text="Select WAV File", command=select_file)
select_file_button.pack(pady=10)

# Create a label to display the selected file
selected_file_label = tk.Label(window, text="")
selected_file_label.pack()

# Create the output path selection button
select_output_button = tk.Button(window, text="Select Output Path", command=select_output_path)
select_output_button.pack(pady=10)

# Create a label to display the selected output path
selected_output_label = tk.Label(window, text="")
selected_output_label.pack()

# Create the phonemize button
phonemize_button = tk.Button(window, text="Phonemize", command=phonemize)
phonemize_button.pack(pady=10)

# Create a label for error messages
error_label = tk.Label(window, text="")
error_label.pack()

# Run the Tkinter event loop
window.mainloop()
