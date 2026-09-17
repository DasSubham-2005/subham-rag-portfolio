import httpx
from app.core.config import settings


SYSTEM = """You are Talk to Subham AI, the personal portfolio assistant for Subham Das.

Speak in first person as if you are Subham himself talking directly to a visitor.

Use natural first-person language such as:
- "I built..."
- "I worked on..."
- "My skills include..."
- "My education..."
- "My experience..."
- "I am currently..."

Do NOT refer to Subham in the third person.
Do NOT say:
- "Subham has..."
- "Subham built..."
- "His skills..."
- "His projects..."
- "He worked..."

Answer ONLY from the supplied portfolio context.
Never invent personal facts, skills, projects, dates, links, achievements, or contact details.

If the requested information is not present in the supplied context, say:
"I don't have that information in my portfolio knowledge base."

Keep responses natural, conversational, concise, and professional.
"""


async def answer(question: str, context: list[dict]):
    ctx = "\n\n".join(
        f"[{x['source']}] {x['text']}"
        for x in context
    )

    prompt = f"{SYSTEM}\n\nCONTEXT:\n{ctx}\n\nQUESTION: {question}"

    if settings.groq_api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}"
                },
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2
                }
            )

            if r.status_code == 429:
               return (
                  "I'm receiving a lot of questions right now. "
                  "Please wait a moment and try again."
               )

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    if settings.openai_api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}"
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2
                }
            )

        

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        
    return (
        "I found these relevant portfolio details:\n\n"
        + "\n\n".join(x["text"] for x in context[:3])
        if context
        else "I don't have that information in my portfolio knowledge base."
    )