import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class FollowUpGenerator:
    """
    Handles all LLM interactions for generating customer follow-up messages.
    Uses Groq inference with llama-3.3-70b-versatile.

    Usage:
        generator = FollowUpGenerator()
        message = generator.generate(customer_dict, tone="professional")
    """

    MODEL = "llama-3.3-70b-versatile"
    MAX_TOKENS = 200
    TEMPERATURE = 0.7

    SYSTEM_PROMPT = (
        "You are a helpful AI assistant for a small business sales team. "
        "Write short, personalized customer follow-up messages. "
        "Never invent facts not present in the customer notes. "
        "Always end with a clear, specific next step."
    )

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set. Add it to your environment or Streamlit secrets."
            )
        self._client = Groq(api_key=api_key)

    def _build_prompt(self, customer: dict, tone: str) -> str:
        return f"""Write one {tone} follow-up message for this customer.

Customer name:  {customer.get('name', '')}
Company:        {customer.get('company', '')}
Last interaction: {customer.get('last_interaction', '')}
Next follow-up: {customer.get('next_followup', '')}
Status:         {customer.get('status', '')}
Interest level: {customer.get('interest_level', '')}
Notes:          {customer.get('notes', '')}

Requirements:
- Tone: {tone}
- Under 120 words
- Personalise using the notes above
- Do not invent any facts
- End with a clear next step
"""

    def generate(self, customer: dict, tone: str = "professional") -> str:
        """
        Generate a personalised follow-up message for a customer.

        Args:
            customer: dict with keys name, company, last_interaction,
                      next_followup, status, interest_level, notes
            tone:     one of professional | friendly | polite | persuasive

        Returns:
            Generated message string, or an error string prefixed with ⚠️
        """
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