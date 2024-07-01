from typing import List, Dict

from project.config import settings


def get_ai_report(history: List[Dict], chat_settings: Dict[str, str]) -> Dict:
    chat_history_str = ""
    for entry in history:
        role = 'buyer' if entry['type'] == 'bot' else 'seller'
        chat_history_str += f"{role}: {entry['content']}\n"
    chat_settings_str = ""
    for k, v in chat_settings_str:
        chat_settings_str += f"{k} - {v}"
    messages = [
        {
            "role": 'system',
            "content": (
                f"""Always return message: Coming soon..."""
            ),
        }
    ]
    chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        n=1,
    )

    response = chat_completion.choices[0].message.content
    return {'response': response}
