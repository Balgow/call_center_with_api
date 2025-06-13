import socket
import wave
from typing import Generator, List
import grpc
import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
import yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc
from ..utils.config import AUDIO_SETTINGS, YANDEX_API_KEY
from ..utils.logger import default_logger, timing_decorator

class AudioRecorder:
    def __init__(self, host='0.0.0.0', port=12345, chunk=4096):
        self.logger = default_logger.getChild("RemoteAudioRecorder")
        self.host = host
        self.port = port
        self.chunk = chunk
        self.client_socket = None
        self.conn = None
        self.logger.info("AudioRecorder initialized")


    def start_recording(self):
        """Wait for TCP connection and start receiving audio"""
        self.logger.info(f"Waiting for TCP audio stream on {self.host}:{self.port}...")
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen(1)
        self.client_socket, addr = self.conn.accept()
        self.logger.info(f"TCP stream connected from {addr}")

    def _save_audio(self):
        """Save recorded audio to WAV file"""
        wave_file = wave.open(AUDIO_SETTINGS['WAVE_OUTPUT_FILENAME'], 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()

    def record_chunk(self) -> bytes:
        """Receive audio chunk from TCP stream"""
        if not self.client_socket:
            raise RuntimeError("TCP connection not established")
        data = self.client_socket.recv(self.chunk)
        if not data:
            raise RuntimeError("Audio stream ended")
        return data

    def stop_recording(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def cleanup(self):
        """Close all sockets"""
        self.stop_recording()


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