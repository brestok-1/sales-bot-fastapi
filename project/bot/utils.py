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
                f"""
Given the chat settings and message history between a simulated buyer (the user) and a sales representative, conduct a thorough analysis to generate a report that evaluates the sales representative's interaction effectiveness. This report should be meticulously structured to include:

1. **Introduction to the Interaction**:
   {'- ** Purpose Pursued by the Seller **:'+ chat_settings.get('goal') if chat_settings.get('goal') else ''}
   {'- **Reason for Calling the Buyer**:'+ chat_settings.get('reason') if chat_settings.get('reason') else ''} 
   {'- **Product Description**:'+chat_settings.get('product_details') if chat_settings.get('product_details') else ''}
2. **Detailed Interaction Analysis**: - **Highlight Positive Aspects**: Recognize the sales representative's 
strengths demonstrated during the interaction. This includes their use of effective communication strategies, 
rapport-building efforts, and proficiency in employing sales techniques. 
   
   - **Identify Areas for Improvement**: Scrutinize the conversation for elements that could potentially impede the 
   sales process, such as missed engagement opportunities, ineffective communication methods, and insufficient 
   customer engagement. 
   
   - **Interaction Details**: Use specific excerpts from the message history to illustrate both positive aspects and 
   areas needing improvement in the sales representative's approach. 

3. **Constructive Recommendations**: - Offer precise advice aimed at bolstering the sales representative's 
communication skills. Suggestions should cover improved questioning tactics, strategies for fostering stronger 
customer relationships, and effective sales closing techniques. 
   
   - Recommendations should be actionable, enabling the sales representative to implement these strategies in future 
   interactions. 

4. **Summary and Motivation**: - Provide a summarizing evaluation of the sales representative's overall performance, 
integrating insights from the analysis. - Encourage continuous skill development and learning, emphasizing the 
importance of applying feedback to enhance sales effectiveness. 

**Leverage the chat settings and message history to inform your analysis, ensuring that the report is tailored to the 
specific context of each interaction. Your comprehensive evaluation and recommendations will guide users in refining 
their sales techniques, fostering both professional growth and sales success.** 

"""
            ),
        }
    ]
    chat_completion = settings.OPENAI_CLIENT.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        temperature=0.3,
        # max_tokens=1024,
        n=1,
    )

    response = chat_completion.choices[0].message.content
    return {'response': response}
