import base64
import tempfile

from project.config import settings


class ChatSettings:
    target_profile: str = None
    objections: list[str] = []
    personality_type: str = None
    pitch_script: str = None
    goal: str = None
    reason: str = None
    last_contact: str = None
    product_details: str = None
    company_description: str = None
    personal_background: str = None

    def get_prompt(self) -> str:
        objections_str = f'"{", ".join(self.objections)}"'
        if self.personality_type.lower() == 'aggressive':
            personality_type = 'a bit aggressive'
        else:
            personality_type = self.personality_type
        prompt = settings.CONVERSATIONAL_PROMPT.replace('{personality_type}', personality_type).replace(
            '{potential_objections}', objections_str)
        return prompt


class Chatbot:
    chat_history = []
    chat_settings = {}
    prompt = None
    PERSONA = ''

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

    def _get_ai_response(self, query: str) -> str:
        user_message = {"role": 'user', "content": query}
        self.chat_history.append(user_message)
        messages = [
            {
                "role": 'system',
                "content": (
                    self.prompt
                ),
            }
        ]
        messages = messages + self.chat_history
        chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.1,
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

    def set_settings(self, data: dict[str, str]):
        chat_settings = ChatSettings()
        chat_settings.target_profile = data.get('target_customer')
        chat_settings.objections = [d["value"] for d in data['objections']]
        chat_settings.personality_type = data.get('personality_type')
        chat_settings.pitch_script = data.get('pitch_script')
        chat_settings.goal = data.get('goal')
        chat_settings.reason = data.get('reason')
        chat_settings.last_contact = data.get('last_contact')
        chat_settings.product_details = data.get('product_details')
        chat_settings.company_description = data.get('company_description')
        chat_settings.personal_background = data.get('personal_background')
        self.chat_settings = chat_settings
        self.prompt = chat_settings.get_prompt()

    def generate_random_persona(self):
        necessary_settings_str = ''
        if self.chat_settings.target_profile:
            necessary_settings_str += f'Job: {self.chat_settings.target_profile}\n'
        if self.chat_settings.personality_type:
            necessary_settings_str += f"Character: {self.chat_settings.personality_type}\n"
        if self.chat_settings.personal_background:
            necessary_settings_str += f'Personal background: {self.chat_settings.target_profile}\n'
        messages = [
            {
                'role': 'system',
                'content': f'{settings.GENERATE_RANDOM_PERSONA.replace("{message}", necessary_settings_str)}\n'
            }
        ]
        completion = settings.OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            temperature=0.4,
            n=1,
            model='gpt-4-turbo',
        )
        response = completion.choices[0].message.content
        self.prompt = self.prompt.replace("{random_persona}", response)
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
        return data
