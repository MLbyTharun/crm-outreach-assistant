import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from dotenv import load_dotenv

load_dotenv()  

class FollowUpGenerator:

    MODEL = "llama-3.3-70b-versatile"
    MAX_TOKENS = 300
    TEMPERATURE = 0.85

    SYSTEM_PROMPT = """You are a sharp, friendly sales rep writing follow-up emails on behalf of a small business.

Your emails should feel like they came from a real human — not a template. They should be warm, specific, and get to the point fast.

Rules you never break:
- Always address the person by their first name
- Only mention things that are actually in the notes — never invent details
- No filler openers like "I hope this email finds you well" or "I wanted to follow up"
- No bullet points — this is an email, write in natural sentences
- Sound like a person, not a software tool
- End with one clear, low-pressure next step"""

    def __init__(self, api_key):
        self._client = Groq(api_key=api_key)

    def _get_first_name(self, full_name: str) -> str:
        """Extract first name so we never say 'Hi John Smith'"""
        return full_name.strip().split()[0] if full_name.strip() else "there"

    def _build_prompt(self, customer: dict, tone: str) -> str:
        first_name = self._get_first_name(customer.get("name", ""))
        
        tone_guide = {
            "professional": "Polished and respectful, but still human. Not stiff.",
            "friendly":     "Warm and casual, like you've met before and got along well.",
            "polite":       "Considerate and gentle — not pushy at all.",
            "persuasive":   "Confident and compelling, but not salesy. Focus on their benefit.",
        }.get(tone, "Natural and genuine.")

        return f"""Write a follow-up email to {first_name} from {customer.get('company', 'their company')}.

Tone to aim for: {tone_guide}

What you know about them:
- Status: {customer.get('status', '')}
- Interest level: {customer.get('interest_level', '')}
- Last spoke: {customer.get('last_interaction', 'unknown')}
- Notes from last conversation: {customer.get('notes', 'No notes available')}

Write the email body only — no subject line, no "Email body:" label.
Start directly with "Hi {first_name}," and keep it under 120 words.
Make it feel personal using the notes. If the notes mention something specific, reference it naturally.
End with one clear next step that feels easy to say yes to."""

    def generate(self, customer: dict, tone: str = "professional") -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user",   "content": self._build_prompt(customer, tone)},
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error generating message: {str(e)}"