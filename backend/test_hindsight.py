import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID")
BASE_URL = os.getenv("HINDSIGHT_BASE_URL")

client = Hindsight(
    base_url=BASE_URL,
    api_key=API_KEY
)

print("Connected to Hindsight!")

print("\nSaving meeting memory...")

client.retain(
    bank_id=BANK_ID,
    content="""
    Meeting with John from Acme Corporation.
    John wants API integration for the project.
    He prefers a short weekly progress update.
    We promised to show the API demo on Friday.
    The main concern is keeping the integration simple.
    """,
    context="client meeting"
)

print("Memory saved successfully!")

print("\nRecalling memory...")

result = client.recall(
    bank_id=BANK_ID,
    query="What did John from Acme Corporation ask for and what did we promise?"
)

print("\n--- HINDSIGHT MEMORY ---")

for memory in result.results:
    print(memory.text)

print("\n--- TEST COMPLETE ---")

client.close()