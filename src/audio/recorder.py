import pyaudio
import wave
from typing import Generator, List
import grpc
import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
import yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc
from ..utils.config import AUDIO_SETTINGS, YANDEX_API_KEY
from ..utils.logger import default_logger, timing_decorator

class AudioRecorder:
    def __init__(self):
        self.logger = default_logger.getChild("AudioRecorder")
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self._setup_audio()
        self.logger.info("AudioRecorder initialized")

    def _setup_audio(self):
        """Initialize audio settings"""
        self.format = getattr(pyaudio, AUDIO_SETTINGS['FORMAT'])
        self.channels = AUDIO_SETTINGS['CHANNELS']
        self.rate = AUDIO_SETTINGS['RATE']
        self.chunk = AUDIO_SETTINGS['CHUNK']
        self.record_seconds = AUDIO_SETTINGS['RECORD_SECONDS']
        self.logger.debug(f"Audio settings configured: {AUDIO_SETTINGS}")

    @timing_decorator(default_logger)
    def start_recording(self):
        """Start recording audio"""
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.frames = []
        # self.logger.info("Recording started")

    @timing_decorator(default_logger)
    def stop_recording(self):
        """Stop recording and save to file"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self._save_audio()
            # self.logger.info("Recording stopped and saved")

    @timing_decorator(default_logger)
    def _save_audio(self):
        """Save recorded audio to WAV file"""
        wave_file = wave.open(AUDIO_SETTINGS['WAVE_OUTPUT_FILENAME'], 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
        # self.logger.debug(f"Audio saved to {AUDIO_SETTINGS['WAVE_OUTPUT_FILENAME']}")

    @timing_decorator(default_logger)
    def record_chunk(self) -> bytes:
        """Record a single chunk of audio"""
        if not self.stream:
            self.logger.error("Attempted to record chunk without active stream")
            raise RuntimeError("Recording not started")
        data = self.stream.read(self.chunk)
        self.frames.append(data)
        return data

    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()
        # self.logger.info("Audio resources cleaned up")

class SpeechRecognizer:
    def __init__(self):
        self.logger = default_logger.getChild("SpeechRecognizer")
        self.cred = grpc.ssl_channel_credentials()
        # self.channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', self.cred)
        self.channel = grpc.secure_channel('stt.api.ml.yandexcloud.kz:443', self.cred)
        self.stub = stt_service_pb2_grpc.RecognizerStub(self.channel)
        self.logger.info("SpeechRecognizer initialized")

    def get_recognition_options(self) -> stt_pb2.StreamingOptions:
        """Get recognition options for Yandex Speech-to-Text"""
        # self.logger.debug("Getting recognition options")
        return stt_pb2.StreamingOptions(
            recognition_model=stt_pb2.RecognitionModelOptions(
                audio_format=stt_pb2.AudioFormatOptions(
                    raw_audio=stt_pb2.RawAudio(
                        audio_encoding=stt_pb2.RawAudio.LINEAR16_PCM,
                        sample_rate_hertz=8000,
                        audio_channel_count=1
                    )
                ),
                text_normalization=stt_pb2.TextNormalizationOptions(
                    text_normalization=stt_pb2.TextNormalizationOptions.TEXT_NORMALIZATION_ENABLED,
                    profanity_filter=True,
                    literature_text=False
                ),
                language_restriction=stt_pb2.LanguageRestrictionOptions(
                    restriction_type=stt_pb2.LanguageRestrictionOptions.WHITELIST,
                    language_code=['ru-RU']
                ),
                audio_processing_type=stt_pb2.RecognitionModelOptions.REAL_TIME
            )
        )

    @timing_decorator(default_logger)
    def recognize_stream(self, audio_generator: Generator) -> Generator:
        """Stream audio to Yandex Speech-to-Text and get recognition results"""
        try:
            # self.logger.info("Starting speech recognition stream")
            recognition_stream = self.stub.RecognizeStreaming(
                audio_generator,
                metadata=[('authorization', f'Api-Key {YANDEX_API_KEY}')]
            )
            return recognition_stream
        except grpc.RpcError as e:
            self.logger.error(f"RPC failed: {e.code()}: {e.details()}")
            raise 