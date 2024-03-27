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
        prompt = """
        You are an AI acting as a buyer with a specific professional background, engaging in a conversation with a 
        user who is the seller. Your responses should mimic natural human interactions, incorporating aspects of 
        curiosity, skepticism, and occasional admissions of not being fully informed about the product or its 
        relevance to your profession. Utilize the following settings to shape the conversation dynamically: 
        """
        if self.target_profile:
            prompt += f"- Target Profile: {self.target_profile}. Your inquiries and comments, about limited, will " \
                      f"subtly reflect this professional background, shaping your perspective on the product's utility " \
                      f"and relevance."
        if self.objections:
            objections_str = f'"{", ".join(self.objections)}"'
            prompt += f"- Objections: {objections_str}. Seamlessly weave these objections into the conversation as " \
                      f"brief reasons for hesitation or skepticism, without delving deeply into discussions or seeking" \
                      f" extensive clarifications."
        if self.personality_type:
            prompt += f"- Personality Type: {self.personality_type}. Your " \
                      f"responses should reflect this mood, adjusting the tone and approach of your interactions. "
        if self.pitch_script:
            prompt += f"- Pitch Script: {self.pitch_script}. Your initial reaction will be influenced by the type of " \
                      f"call, showing varying degrees of openness or reluctance based on whether it's a cold, mock, " \
                      f"or warm call. "
        if self.goal:
            prompt += f"- Goal: {self.goal}. Although your responses are concise, aim to subtly guide the seller " \
                      f"towards addressing these improvement areas through their pitch, providing minimal but pointed " \
                      f"feedback. "
        if self.reason:
            prompt += f"- Reason: {self.reason}. Your minimal questions or comments will indirectly relate to this " \
                      f"purpose, indicating a passive interest in what the seller has to offer based on the call's " \
                      f"intent."
        if self.last_contact:
            prompt += f"- Last Contact: {self.last_contact}. This information will influence your recognition of the " \
                      f"seller and the context of your relationship, whether it's a first-time conversation or a " \
                      f"follow-up. "
        if self.product_details:
            prompt += f"- Product Detail: {self.product_details}. Mention or hint at these details sparingly to show " \
                      f"a basic understanding or awareness, primarily allowing the seller to elaborate on the " \
                      f"product's features and benefits. "
        if self.company_description:
            prompt += f"- Company Description: {self.company_description}. Utilize this to assess the seller's pitch " \
                      f"critically but with minimal outward curiosity, focusing on how they present the product's " \
                      f"alignment with your professional needs. "
        prompt += "Incorporate these elements to create a realistic and dynamic interaction,This revised approach " \
                  "emphasizes your role as a typical customer on the receiving end of a sales call, characterized by " \
                  "brief responses and a general posture of passive reception rather than active inquiry. "
        return prompt


class Chatbot:
    chat_history = []
    prompt = None

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

    def set_settings(self, data: dict[str, str]):
        chat_settings = ChatSettings()
        chat_settings.target_profile = data.get('target_profile')
        chat_settings.objections = [d["value"] for d in data['objections']]
        chat_settings.personality_type = data.get('personality_type')
        chat_settings.pitch_script = data.get('pitch_script')
        chat_settings.goal = data.get('goal')
        chat_settings.rfeason = data.get('reason')
        chat_settings.last_contact = data.get('last_contact')
        chat_settings.product_details = data.get('product_details')
        chat_settings.company_description = data.get('company_description')
        chat_settings.personal_background = data.get('personal_background')
        self.prompt = chat_settings.get_prompt()

    def ask(self, data: dict) -> dict:
        audio = data['audio']
        temp_filepath = self._transform_bytes_to_file(audio)
        transcript = self._transcript_audio(temp_filepath)
        ai_response = self._get_ai_response(transcript)
        voice_ai_response = self._convert_response_to_voice(ai_response)
        data = {
            'user_query': transcript,
            'ai_response': ai_response,
            'voice_response': voice_ai_response
        }
        return data
