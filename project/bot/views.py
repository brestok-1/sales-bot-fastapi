from project.bot import bot_router
from project.bot.schemas import UserFilterQuerySchema
from project.bot.utils import get_ai_report


@bot_router.post('/report', name='filter-message')
async def get_report(chat_history: UserFilterQuerySchema) -> dict:
    report = get_ai_report(chat_history.history, chat_history.settings)
    return report
