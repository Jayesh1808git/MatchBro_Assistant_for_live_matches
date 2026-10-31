
import os
from groq import AsyncGroq

from app.services.historical_rag import retrieve_history
from app.database import get_recent_events


client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


SYSTEM_PROMPT = """
You are MatchBro, a friendly and knowledgeable cricket companion.

You talk like a cricket-loving friend, not like a formal chatbot.

You help viewers:
- Understand the current match.
- Explore historical cricket.
- Discover interesting cricket facts.
- Understand player performances.
- Stay entertained during slow match periods.

IMPORTANT RULES:

1. Use the supplied live match data for current-match claims.

2. Use historical knowledge context for historical facts.

3. Never invent match events, scores, records or statistics.

4. Clearly distinguish the simulated demo match
   from real historical cricket records.

5. If the supplied information does not contain
   the answer, say that you do not have enough data.

6. If a user asks about a previous over, use the
   timestamped ball events provided.

7. If a user asks a historical question, prioritize
   the retrieved historical records.

8. If a user asks a comparison, use both live and
   historical context when relevant.

9. Keep spoken responses concise and conversational.
   Normally use 2-5 sentences.

10. You can be playful and entertaining, but do not
    invent facts just to make the answer interesting.

11. Never claim that the simulated match is a real
    live international match.

"""


async def ask_matchbro(question, match_state):

    # Retrieve recent live match events.

    live_events = get_recent_events(limit=12)

    # Retrieve relevant historical facts.

    historical_records = retrieve_history(
        question,
        top_k=3
    )

    live_context = "\n".join([

        (
            f"Over {event['over_number'] + 1}."
            f"{event['ball_number']}: "
            f"{event['batter']} faced {event['bowler']}. "
            f"Outcome: {event['outcome']}. "
            f"Runs: {event['runs']}. "
            f"Wicket: {event['wicket']}. "
            f"Event: {event['commentary']}. "
            f"Elapsed time: {event['elapsed_seconds']} seconds."
        )

        for event in live_events

    ])

    historical_context = "\n\n".join([

        (
            f"Title: {record['title']}\n"
            f"Category: {record['category']}\n"
            f"Fact: {record['content']}\n"
            f"Source: {record['source']}"
        )

        for record in historical_records

    ])

    user_prompt = f"""

    USER QUESTION:
    {question}

    CURRENT MATCH STATE:
    {match_state}

    RECENT LIVE MATCH EVENTS:
    {live_context or "No balls have been played yet."}

    RETRIEVED HISTORICAL CRICKET KNOWLEDGE:
    {historical_context or "No relevant historical record retrieved."}

    Answer the user's question.

    Be conversational and concise.

    Only use information supported by the provided context.
    """

    response = await client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.4,

        max_tokens=350

    )

    answer = response.choices[0].message.content

    return {

        "answer": answer or (
            "Sorry, I couldn't generate a response."
        ),

        "live_events_used": len(live_events),

        "historical_sources": [

            {
                "title": record["title"],
                "source": record["source"],
                "similarity": record["similarity"]
            }

            for record in historical_records

        ]

    }
