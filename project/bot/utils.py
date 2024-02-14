from typing import List, Dict

from project.config import settings


def get_ai_report(history: List[Dict]) -> Dict:
    print(history)
    chat_history_str = ""
    for entry in history:
        role = 'buyer' if entry['type'] == 'bot' else 'seller'
        chat_history_str += f"{role}: {entry['content']}\n"
    messages = [
        {
            "role": 'system',
            "content": (
                f"{settings.REPORT_PROMPT}"
                f"Chat history: ```{chat_history_str}```\n"
            ),
        }
    ]
    chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.6,
        max_tokens=1024,
        n=1,
    )

    response = chat_completion.choices[0].message.content
    print(response)
    return {'response': response}
