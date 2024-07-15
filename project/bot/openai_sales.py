import base64
import os
import tempfile

from project.bot.schemas import ProspectProfile, ChatSettings
from project.config import settings


class Chatbot:

    def __init__(self, memory=None):
        if memory is None:
            memory = []
        self.chat_history = memory
        self.chat_settings: ChatSettings | None = None
        self.random_persona = None
        self.prompt = None

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

    def _get_ai_response(self, query: str) -> str:
        user_message = {"role": 'user', "content": query}
        self.chat_history.append(user_message)
        messages = [
            {
                "role": 'system',
                "content": settings.CONVERSATIONAL_PROMPT.replace('{profile}', self.random_persona)
            }
        ]
        messages = messages + self.chat_history
        chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
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

    def set_settings(self, data: dict[str, str]):
        profile_settings = {k: v for k, v in data.items() if k.startswith('profile') if v is not None}
        other_settings = {k: v for k, v in data.items() if not k.startswith('profile') and v is not None}
        profile_object = ProspectProfile(**profile_settings)
        self.chat_settings = ChatSettings(**other_settings)
        self.chat_settings.prospect_profile = profile_object

    def generate_random_persona(self):
        persona_json = self.chat_settings.prospect_profile.model_dump_json()
        messages = [
            {
                'role': 'system',
                'content': settings.GENERATE_RANDOM_PERSONA.replace("{profile}", persona_json)
            }
        ]
        completion = settings.OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            temperature=1,
            n=1,
            model='gpt-4o',
        )
        response = completion.choices[0].message.content
        self.random_persona = response
        return {
            'type': 'random_persona',
            'data': {
                'persona': response
            }
        }

    def ask(self, data: dict) -> dict:
        audio = data['audio']
        temp_filepath = self._transform_bytes_to_file(audio)
        transcript = self._transcript_audio(temp_filepath)
        ai_response = self._get_ai_response(transcript)
        voice_ai_response = self._convert_response_to_voice(ai_response)
        data = {
            'type': 'answering',
            'data': {
                'user_query': transcript,
                'ai_response': ai_response,
                'voice_response': voice_ai_response
            }
        }
        os.remove(temp_filepath)
        return data
