import base64
import tempfile
from typing import Dict

from project.config import settings


class Chatbot:
    chat_history = []

    def __init__(self, memory=None):
        if memory is None:
            memory = []
        self.chat_history = memory

    @staticmethod
    def _transform_bytes_to_file(data_bytes) -> str:
        audio_bytes = base64.b64decode(data_bytes)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        try:
            temp_file.write(audio_bytes)
            filepath = temp_file.name
        finally:
            temp_file.close()
        return filepath

    @staticmethod
    def _transcript_audio(temp_filepath: str) -> str:
        with open(temp_filepath, 'rb') as file:
            transcript = settings.OPENAI_CLIENT.audio.transcriptions.create(
                model='whisper-1',
                file=file
            )
        text = transcript.text
        return text

    def _get_ai_response(self, query: str, personality_type: str, target_audience: str) -> str:
        user_message = {"role": 'user', "content": query}
        self.chat_history.append(user_message)
        messages = [
            {
                "role": 'system',
                "content": (
                    f"You are a {target_audience} to whom a sales representative (user) has written. The user will "
                    f"offer you to buy a specific product. Be a {personality_type} person. Occasionally respond with "
                    f"'oh, ah', or just silence, ask questions about the product, express some interest in it.\n"
                    "Don't ask too many questions and don't be overly "
                    f"interested. Respond {personality_type}. "
                ),
            }
        ]
        messages = messages + self.chat_history
        chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
            max_tokens=128,
            n=1,
        )

        response = chat_completion.choices[0].message.content
        assistant_message = {"role": 'assistant', "content": response}
        self.chat_history.append(assistant_message)
        return response

    @staticmethod
    def _convert_response_to_voice(ai_response: str) -> str:
        audio = settings.OPENAI_CLIENT.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_response
        )
        encoded_audio = base64.b64encode(audio.content).decode('utf-8')
        return encoded_audio

    def ask(self, data: dict) -> dict:
        audio = data['audio']
        personality_type = data['personality_type']
        target_audience = data['target_customer']
        print(data)
        temp_filepath = self._transform_bytes_to_file(audio)
        transcript = self._transcript_audio(temp_filepath)
        ai_response = self._get_ai_response(transcript, personality_type, target_audience)
        voice_ai_response = self._convert_response_to_voice(ai_response)
        data = {
            'user_query': transcript,
            'ai_response': ai_response,
            'voice_response': voice_ai_response
        }
        return data
