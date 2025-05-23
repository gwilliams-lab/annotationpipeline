#!/usr/bin/env python3

import os
import sys
import torch
import whisper
import librosa
import soundfile as sf
import pandas as pd
import textgrid
import nltk
from pathlib import Path
import argparse
import ssl

# below modification adding charsiu to python path for proper location
SCRIPT_DIR = Path(__file__).parent.absolute()
CHARSIU_DIR = SCRIPT_DIR / "charsiu" / "src"
sys.path.append(str(CHARSIU_DIR))

# necessary to fix the certification issue
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# NLTK data is downloaded because Charsiu uses it to tag (tokenization) and also labeling words with tags like noun, verb, adjective, etc.
nltk.download('averaged_perceptron_tagger_eng', quiet=True)


class AudioTranscriber:
    def __init__(self, input_dir: str, output_dir: str):
        #initializing input and output directories
        self.input_dir = Path(input_dir).absolute()
        self.output_dir = Path(output_dir).absolute()
        self.model = None
        self.charsiu = None

        # Validate input directory
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")

        # Initialize Whisper model
        print("Loading Whisper model.....")
        self.model = whisper.load_model("base")

        # Initialize Charsiu model
        print("Loading Charsiu model.....")
        try:
            from Charsiu import charsiu_forced_aligner
            self.charsiu = charsiu_forced_aligner(aligner='charsiu/en_w2v2_fc_10ms')
        except ImportError as e:
            print(f"Error loading Charsiu: {e}")
            print(f"PYTHONPATH: {sys.path}")
            raise

    # using whisper function to transcribe input audio
    def transcribe(self, audio_path: str) -> str:
        result = self.model.transcribe(audio_path)
        return result["text"]

    # convert audio to 16kHz sample rate
    def convert_sample_rate(self, audio_path: str):
        audio, sr = librosa.core.load(audio_path, sr=16000)
        sf.write(audio_path, audio, sr)

    # perform a forced alignment using Charsiu
    def forced_align(self, audio_path: str, transcript: str, output_path: str):
        self.charsiu.serve(audio=audio_path, text=transcript, save_to=output_path)

    # convert TextGrid to CSV with word and phoneme information
    def textgrid_to_csv(self, textgrid_path: str, csv_path: str):
        tg = textgrid.TextGrid.fromFile(textgrid_path)
        data = []

        word_tier = tg.getFirst("words")
        phoneme_tier = tg.getFirst("phones")

        for word_interval in word_tier:
            word = word_interval.mark
            word_start = word_interval.minTime
            word_end = word_interval.maxTime
            phoneme_position = 1

            for phoneme_interval in phoneme_tier:
                if (phoneme_interval.minTime >= word_start and
                        phoneme_interval.maxTime <= word_end):
                    data.append([
                        word,
                        word_start,
                        word_end,
                        phoneme_interval.mark,
                        phoneme_position,
                        phoneme_interval.minTime,
                        phoneme_interval.maxTime
                    ])
                    phoneme_position += 1

        pd.DataFrame(data, columns=[
            'Word', 'Word_Start_Time', 'Word_End_Time',
            'Phoneme', 'Phoneme_Position',
            'Phoneme_Start_Time', 'Phoneme_End_Time'
        ]).to_csv(csv_path, index=False)

    # Process a single audio file
    def process_file(self, audio_file: str):
        print(f"Processing: {audio_file}")

        # Full paths
        audio_path = self.input_dir / audio_file
        base_name = audio_file.rsplit('.', 1)[0]
        textgrid_path = self.output_dir / f"{base_name}.TextGrid"
        csv_path = self.output_dir / f"{base_name}.csv"

        # Get transcript
        transcript = self.transcribe(str(audio_path))
        print(f"Transcript: {transcript}")

        # output transcript in the output folder
        with open(self.output_dir / f"{base_name}.txt", "w") as f:
            f.write(transcript)
        print(f"Saved transcript to: {self.output_dir / f'{base_name}.txt'}")

        # Convert sample rate
        self.convert_sample_rate(str(audio_path))

        # Perform forced alignment
        self.forced_align(str(audio_path), transcript, str(textgrid_path))

        # Convert to CSV
        self.textgrid_to_csv(str(textgrid_path), str(csv_path))
        print(f"Created CSV: {csv_path}")

    # Process all WAV files in the input directory
    def process_all_files(self):
        """Process all WAV files in the input directory."""
        wav_files = [f for f in os.listdir(self.input_dir) if f.endswith('.wav')]

        if not wav_files:
            print(f"No WAV files found in the input directory: {self.input_dir}")
            print("Please add some .wav files and try again.")
            return

        print(f"Found {len(wav_files)} WAV files to process:")
        for wav_file in wav_files:
            print(f"  - {wav_file}")

        for wav_file in wav_files:
            try:
                self.process_file(wav_file)
            except Exception as e:
                print(f"Error processing {wav_file}: {str(e)}")


# Note: argparse command used for command line operations
def main():
    parser = argparse.ArgumentParser(
        description="Audio Transcription and Alignment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process all WAV files in the input directory
    python transcribe.py --input-dir ./input --output-dir ./output

    # Process a specific WAV file
    python transcribe.py --input-dir /path/to/wavs --output-dir /path/to/output *
        """
    )

    parser.add_argument("--input-dir", required=True,
                        help="Directory containing WAV files")
    parser.add_argument("--output-dir", required=True,
                        help="Directory for output files")

    args = parser.parse_args()

    try:
        # Create and run transcriber
        transcriber = AudioTranscriber(args.input_dir, args.output_dir)
        transcriber.process_all_files()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()