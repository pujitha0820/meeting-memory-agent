import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Hindsight configuration
# -----------------------------

hindsight = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

BANK_ID = os.getenv("HINDSIGHT_BANK_ID")


# -----------------------------
# Groq configuration
# -----------------------------

groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------
# Data models
# -----------------------------

class Meeting(BaseModel):
    person: str
    company: str
    discussion: str
    action_items: str
    preferences: str


class Question(BaseModel):
    question: str


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Meeting Memory Agent is running!"
    }


# -----------------------------
# Save meeting
# -----------------------------

@app.post("/save-meeting")
def save_meeting(meeting: Meeting):

    memory_text = f"""
    Meeting with {meeting.person} from {meeting.company}.

    Discussion:
    {meeting.discussion}

    Action items:
    {meeting.action_items}

    Preferences:
    {meeting.preferences}
    """

    hindsight.retain(
        bank_id=BANK_ID,
        content=memory_text,
        context="business meeting"
    )

    return {
        "message": "Meeting saved to Hindsight successfully!"
    }


# -----------------------------
# Ask question
# -----------------------------

@app.post("/ask")
def ask_question(data: Question):

    memories = hindsight.recall(
        bank_id=BANK_ID,
        query=data.question
    )

    memory_text = "\n".join(
        memory.text for memory in memories.results
    )

    prompt = f"""
You are a professional Meeting Preparation Agent.

Use the following memories from previous meetings:

{memory_text}

User's question:
{data.question}

Answer using the remembered information.

If the memories do not contain the answer, clearly say that
the information was not found in previous meetings.

Keep the answer concise and useful.
"""

    response = groq.chat.completions.create(
       model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful meeting preparation assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "memories_used": memory_text
    }