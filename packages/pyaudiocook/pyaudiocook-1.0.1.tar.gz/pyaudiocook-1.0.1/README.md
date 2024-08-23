# pyaudiocook

A Python package for recording and transcribing audio.

- [pyaudiocook](#pyaudiocook)
  - [Installation](#installation)
  - [Usage](#usage)
    - [AudioRecorder](#audiorecorder)
      - [Example: start recording](#example-start-recording)
      - [Example: pause/resume recording](#example-pauseresume-recording)
      - [Example: stop recording](#example-stop-recording)
    - [AudioTranscriber](#audiotranscriber)
      - [Example: Local whisper model and single audio file](#example-local-whisper-model-and-single-audio-file)
      - [Example: Local whisper model and multiple audio file](#example-local-whisper-model-and-multiple-audio-file)
      - [Example: Calling OpenAI API](#example-calling-openai-api)
      - [Example: Using another model](#example-using-another-model)

## Installation

```bash
pip install pyaudiocook
```

## Usage

The package contains two classes: `AudioRecorder` and `AudioTranscriber`.

### AudioRecorder

#### Example: start recording

```python
recorder = AudioRecorder()
recorder.start_recording()
```

#### Example: pause/resume recording

```python
recorder = AudioRecorder()
recorder.toggle_recording()
```

#### Example: stop recording

```python
recorder = AudioRecorder()
recorder.stop_recording()
```

### AudioTranscriber

Before getting started, make sure you have already obtained an API key on OpenAI. If you have not done so, follow [this guide](https://platform.openai.com/docs/quickstart/create-and-export-an-api-key) to create one.

#### Example: Local whisper model and single audio file

```python
# Transcribe using local whisper model, which is the default
transcriber = AudioTranscriber('audio_1.wav')
transcriber.transcribe()
print(transcriber.texts)
```

#### Example: Local whisper model and multiple audio file

```python
# You can pass multiple audio files for transcribing
transcriber = AudioTranscriber('audio_1.wav', 'audio_2.wav')
transcriber.transcribe()
print(transcriber.texts)
```

#### Example: Calling OpenAI API

*Note: API usage fee applies.*

```python
# You can pass multiple audio files for transcribing
transcriber = AudioTranscriber('audio_1.wav', 'audio_2.wav', mode='remote')
transcriber.transcribe()
print(transcriber.texts)
```

#### Example: Using another model

*Note: this only applies when local whisper model is used*

```python
# Default is tiny.en
transcriber = AudioTranscriber('audio_1.wav', 'audio_2.wav', mode='local', model='base.en')
transcriber.transcribe()
print(transcriber.texts)
```
