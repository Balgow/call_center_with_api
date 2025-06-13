import io
import grpc
import struct
import socket
from typing import Optional, List
import yandex.cloud.ai.tts.v3.tts_pb2 as tts_pb2
import yandex.cloud.ai.tts.v3.tts_service_pb2_grpc as tts_service_pb2_grpc
from ..utils.config import YANDEX_API_KEY
from ..utils.logger import default_logger, timing_decorator

class AudioStreamer:
    def __init__(self, host='0.0.0.0', port=23456):
        self.logger = default_logger.getChild("RemoteAudioRecorder")
        self.host = host
        self.port = port
        self.client_socket = None
        self.conn = None
        self.logger.info("AudioRecorder initialized")


    def start_streaming(self):
        """Wait for TCP connection and start receiving audio"""
        self.logger.info(f"Waiting for TCP audio stream on {self.host}:{self.port}...")
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen(1)
        self.client_socket, addr = self.conn.accept()
        self.logger.info(f"TCP stream connected from {addr}")

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


class AudioStreamer:
    def __init__(self, host='0.0.0.0', port=23456):
        self.logger = default_logger.getChild("RemoteAudioRecorder")
        self.host = host
        self.port = port
        self.client_socket = None
        self.conn = None

    def start_streaming(self):
        """Wait for TCP connection and start receiving audio"""
        self.logger.info(f"Waiting for TCP audio stream on {self.host}:{self.port}...")
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen(1)
        self.client_socket, addr = self.conn.accept()
        self.logger.info(f"TCP stream connected from {addr}")

    def send_segments(self, segments: List [bytes]):
        for segment in segments:
            if not segment:
                continue
            length = len(segment)
            header = struct.pack('>I', length)
            self.client_socket.sendall(header + segment)
    
    def close(self):
        self.conn.close()
        self.sock.close()

class SpeechSynthesizer:
    def __init__(self):
        self.logger = default_logger
        self.cred = grpc.ssl_channel_credentials()
        # self.channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', self.cred)
        self.socket = None
        # self.socket_conn = None
        self.channel = grpc.secure_channel('tts.api.ml.yandexcloud.kz:443', self.cred)
        self.stub = tts_service_pb2_grpc.SynthesizerStub(self.channel)
        self.connect_socket()
        # self.socket = AudioStreamer()
        self.logger.info("SpeechSynthesizer initialized")

    def connect_socket(self):
        try:
            if self.socket is None:
                print("""Wait for TCP connection and start receiving audio""")

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind(('0.0.0.0', 23456))
                self.socket.listen(1)
                self.socket_conn, addr = self.socket.accept()
                print("""connected""")

        except Exception as e:
            print('error')
            self.socket = None 

    def get_synthesis_request(self, text: str) -> tts_pb2.UtteranceSynthesisRequest:
        """Get synthesis request for Yandex Text-to-Speech"""
        return tts_pb2.UtteranceSynthesisRequest(
            text=text,
            output_audio_spec=tts_pb2.AudioFormatOptions(
                container_audio=tts_pb2.ContainerAudio(
                    container_audio_type=tts_pb2.ContainerAudio.WAV
                )
            ),
            hints=[
                tts_pb2.Hints(voice='zhanar_ru'),
                tts_pb2.Hints(speed=1.0),  
                tts_pb2.Hints(role = 'friendly'),
            ],
            loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS
        )

    @timing_decorator(default_logger)
    def synthesize_speech(self, text: str):
        """Synthesize speech from text using Yandex TTS gRPC API"""
        try:
            self.logger.info(f"Synthesizing speech for text: {text[:100]}...")

            # Create synthesis request
            request = self.get_synthesis_request(text)

            # Send request to Yandex TTS API
            response_iterator = self.stub.UtteranceSynthesis(
                request,
                metadata=[('authorization', f'Api-Key {YANDEX_API_KEY}')]
            )

            # Collect audio chunks
            audio = io.BytesIO()
            for response in response_iterator:
                audio.write(response.audio_chunk.data)
            
            audio.seek(0)
            return audio.read()
        except grpc.RpcError as e:
            self.logger.error(f"RPC failed: {e.code()}: {e.details()}")
            return None
        except Exception as e:
            self.logger.error(f"Error synthesizing speech: {e}")
            return None

    def play_audio(self, audio_bytes: bytes) -> None:
        """Play synthesized audio using pydub"""
        try:
            # self.connect_socket()
            self.socket_conn.sendall(audio_bytes)
            print("sent _____________________________________________-")
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            
    def play_audio_segments(self, audio_segments: List[bytes]) -> None:
        """Play synthesized audio using pydub"""
        try:
            # self.connect_socket()
            # self.socket.send_segments(audio_segments)
            for audio_segment in audio_segments:
                self.play_audio(audio_segment)
        except Exception as e:
            self.logger.error(f"Eterror playing audio: {e}")
            

    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            self.socket.close()
        self.logger.info("SpeechSynthesizer resources cleaned up")
