import sys
import time
from typing import Generator, List
import yandex.cloud.ai.stt.v3.stt_pb2 as stt_pb2
from .audio.recorder import AudioRecorder, SpeechRecognizer
from .audio.synthesizer import SpeechSynthesizer
from .api.gpt_handler import GPTHandler
from .utils.logger import default_logger, timing_decorator
# from .rag.local_loader_v1 import DocumentLoader
from .utils.config import DOCUMENT_NON_EXISTING, DOCUMENT_END, DOCUMENT_START
class VoiceAssistant:
    def __init__(self):
        self.logger = default_logger
        self.audio_recorder = AudioRecorder()
        self.speech_recognizer = SpeechRecognizer()
        self.speech_synthesizer = SpeechSynthesizer()
        self.gpt_handler = GPTHandler()
        
        # self.document_loader = DocumentLoader()
        self.is_recording = False
        self.last_recognition_time = 0
        self.pause_threshold = 1
        self.recognized_text_buffer = []

    def audio_generator(self) -> Generator:
        """Generate audio chunks for streaming"""
        yield stt_pb2.StreamingRequest(
            session_options=self.speech_recognizer.get_recognition_options()
        )

        self.audio_recorder.start_recording()
        self.is_recording = True

        try:
            while self.is_recording:
                chunk = self.audio_recorder.record_chunk()
                yield stt_pb2.StreamingRequest(chunk=stt_pb2.AudioChunk(data=chunk))
        finally:
            self.audio_recorder.stop_recording()

    def check_for_pause(self) -> bool:
        """Check if there has been a pause in speech"""
        current_time = time.time()
        time_since_last_recognition = current_time - self.last_recognition_time
        return time_since_last_recognition >= self.pause_threshold

    def process_buffered_text(self, lang_code="ru"):
        """Process the buffered text and send to GPT"""
        if not self.recognized_text_buffer:
            return

        combined_text = " ".join(self.recognized_text_buffer).strip()
        if not combined_text:
            return
        self.logger.info(f"User: {combined_text}")
        segments = []

        gpt_response = self.gpt_handler.generate_response_from_text(combined_text)
        if gpt_response == "NO_CONTEXT":
            audio_segment = self.speech_synthesizer.synthesize_speech(DOCUMENT_NON_EXISTING)
            self.speech_synthesizer.play_audio(audio_segment)
        else:
            chunks = self.gpt_handler.split_text_into_chunks(gpt_response)
            for chunk in chunks:
                audio_segment = self.speech_synthesizer.synthesize_speech(chunk)
                segments.append(audio_segment)
            segments.append(self.speech_synthesizer.synthesize_speech(DOCUMENT_END))
            self.speech_synthesizer.play_audio_segments(segments)
        
        self.recognized_text_buffer = []

    def process_recognition_result(self, result):
        """Process recognition results and generate GPT response"""
        event_type = result.WhichOneof('Event')
        alternatives = None

        if event_type == 'final_refinement':
            alternatives = [a.text for a in result.final_refinement.normalized_text.alternatives]
            self.last_recognition_time = time.time()
            self.recognized_text_buffer.append(alternatives[0])

        if self.recognized_text_buffer:
            self.process_buffered_text()

    def run(self):
        """Main run loop"""
        print("Voice Assistant started. Press Ctrl+C to stop.")
        print("Speak into the microphone. The system will process your speech after you pause.")
        try:
            while True:
                print("\nPress Enter to start recording (Ctrl+C to exit)...")
                input()
                
                audio_segment = self.speech_synthesizer.synthesize_speech(DOCUMENT_START)
                if audio_segment:
                    self.speech_synthesizer.play_audio(audio_segment)
                    
                self.last_recognition_time = time.time()
                self.recognized_text_buffer = []
                
                recognition_stream = self.speech_recognizer.recognize_stream(self.audio_generator())
                
                for result in recognition_stream:
                    self.process_recognition_result(result)
                
                self.audio_recorder.cleanup()
                self.is_recording = False

        except KeyboardInterrupt:
            print("\nStopping Voice Assistant...")
            self.audio_recorder.cleanup()
            self.speech_synthesizer.cleanup()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            self.audio_recorder.cleanup()
            self.speech_synthesizer.cleanup()
            sys.exit(1)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run() 