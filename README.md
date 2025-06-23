**Streamlined annotation pipeline VERSION 1** by Riya Anand

Note: this code is modeled and referenced from Whisper (for transcript) + Charsiu (for alignment) functions.

Note: Jupyter Notebook in progress...

Note: Code works best for file lengths under around 20 minutes. 

**[Google Colab Notebook version](https://colab.research.google.com/drive/1QaeiHJw8ga0DNkx8_2xey5fqyDtdk5EF?usp=sharing)**

The Whisper portion is a streamlined version of [OpenAI's free Whisper speech recognition model ](https://openai.com/blog/whisper/) and is based on an [original notebook by @amrrs](https://github.com/amrrs/openai-whisper-webapp), with added documentation and test files by Pete Warden.

The Charsiu portion is based off [Charsiu's alignment model and their provided Colab Notebooks](https://github.com/lingjzhu/charsiu). Forced alignment functions were utilized as it takes in the transcript generated from Whisper's model.

-----------

**PULLING REPO INSTRUCTIONS** 
1) Pull from the main branch as well as from the dropdown "development" branch to ensure proper cloning of the Charsiu code. If this doesn't work, the following command can be run in the terminal:

           git clone  https://github.com/lingjzhu/charsiu
           cd charsiu
**USER INSTRUCTIONS** 

1) Upload .wav files into an "input" folder of your choice
2) Create an output directory for your files. For an input, "a.wav" the code will produce various outputs. If "transcribe.py" is run, the code will output "a.txt" (the raw transcript of the audio file through Whisper), "a.csv" and "a.TextGrid" which are the basic annotations. If the user chooses to run "features.py" the code will also output "a_with_features.csv" which outputs the phonetic feature annotation. 
3) to run transcript.py, use the following commands: 

    
        python transcribe.py --input-dir ./input --output-dir ./output (for all .wav files in a directory)
    
        python transcribe.py --input-dir /path/to/wavs --output-dir /path/to/output (for specific .wav file)

   
5) run features.py to get phonetic features if necessary

       python features.py --input-dir ./input --output-dir ./output




Below: to recreate virtual environment:


    python -m venv .venv
    source .venv/bin/activate  # (or .venv\Scripts\activate on Windows)
    pip install -r requirements.txt

** Pipeline still is a work in progress!! Formatting needs to be edited. 


