import io
import grpc
import pydub
from pydub.playback import play
from typing import Optional, List
import yandex.cloud.ai.tts.v3.tts_pb2 as tts_pb2
import yandex.cloud.ai.tts.v3.tts_service_pb2_grpc as tts_service_pb2_grpc
from ..utils.config import YANDEX_API_KEY
from ..utils.logger import default_logger, timing_decorator

class SpeechSynthesizer:
    def __init__(self):
        self.logger = default_logger
        self.cred = grpc.ssl_channel_credentials()
        # self.channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', self.cred)

        self.channel = grpc.secure_channel('tts.api.ml.yandexcloud.kz:443', self.cred)
        self.stub = tts_service_pb2_grpc.SynthesizerStub(self.channel)
        self.logger.info("SpeechSynthesizer initialized")

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
    def synthesize_speech(self, text: str) -> Optional[pydub.AudioSegment]:
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
            return pydub.AudioSegment.from_wav(audio)

        except grpc.RpcError as e:
            self.logger.error(f"RPC failed: {e.code()}: {e.details()}")
            return None
        except Exception as e:
            self.logger.error(f"Error synthesizing speech: {e}")
            return None

    def play_audio(self, audio_segment: pydub.AudioSegment) -> None:
        """Play synthesized audio using pydub"""
        try:
            play(audio_segment)
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            
    def play_audio_segments(self, audio_segments: List[pydub.AudioSegment]) -> None:
        """Play synthesized audio using pydub"""
        try:
            for audio_segment in audio_segments:
                play(audio_segment)
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            

    def cleanup(self):
        """Clean up resources"""
        self.logger.info("SpeechSynthesizer resources cleaned up")
