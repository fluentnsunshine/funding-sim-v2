import os
import time
import random
import openai
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from enum import Enum
from dataclasses import dataclass, field

# Load API keys and environment variables
load_dotenv()


# 📌 OpenAI Retry Handler (Prevents Rate Limit Issues)
def call_openai_with_retry(prompt):
    """Retries OpenAI API calls if rate-limited (Error 429)."""
    max_retries = 5
    wait_time = 2  # Start with a 2-second wait

    for attempt in range(max_retries):
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a skilled negotiator."},
                          {"role": "user", "content": prompt}],
                temperature=0.8
            )
            return response.choices[0].message.content

        except openai.RateLimitError:
            if attempt == max_retries - 1:
                raise  # Give up after max retries
            wait_time *= 2  # Exponential backoff
            print(f"⚠️ Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)  # Wait before retrying


# 📌 Offer Data Class
@dataclass
class Offer:
    amount: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"${self.amount:,.2f}: {self.message}"


# 📌 Negotiation History
class NegotiationHistory:
    def __init__(self):
        self.corporate_offers = []
        self.nonprofit_offers = []

    def add_offer(self, role, offer):
        """Track offers made during negotiation."""
        if role == "corporate":
            self.corporate_offers.append(offer)
        elif role == "nonprofit":
            self.nonprofit_offers.append(offer)

    def get_last_offer(self, role):
        """Returns the last offer made by a given role."""
        if role == "corporate" and self.corporate_offers:
            return self.corporate_offers[-1]
        elif role == "nonprofit" and self.nonprofit_offers:
            return self.nonprofit_offers[-1]
        return None


# 📌 Corporate Negotiator
class CorporateNegotiator:
    def __init__(self):
        self.last_offer = None
        self.negotiation_tactic = None

    def make_offer(self, state):
        """Generate corporate funding offer dynamically."""
        base_offer = state.funding_offered * 1.05  # Increment offer

        prompt = f"""
        You are a **corporate negotiator** allocating funding.
        - Nonprofit requests **${state.funding_requested:,.2f}** 
        - You are offering **${base_offer:,.2f}**.

        **Guidelines:**
        - Keep responses short (2-3 sentences max).
        - Justify your offer using ROI, ESG impact, and budget limits.
        - If nonprofit insists, consider adding **final conditions**.

        Example: "We can commit to ${base_offer:,.2f} based on financial strategy. Can we adjust project scope to match?"
        """

        message = call_openai_with_retry(prompt)
        self.last_offer = base_offer
        return Offer(base_offer, message)


# 📌 Nonprofit Negotiator
class NonprofitNegotiator:
    def __init__(self):
        self.last_counter_offer = None
        self.previous_responses = []

    def make_offer(self, state):
        """Generate nonprofit funding request dynamically."""
        counter_offer = state.funding_requested if not self.last_counter_offer else max(self.last_counter_offer * 0.95, state.funding_offered * 1.05)

        # 🎭 Choose rebuttal tactics
        tactics = [
            "Urgency Appeal",  # "Delays cost lives—action is needed now."
            "Expose Corporate Contradiction",  # "You claim ESG is a priority, yet funding is uncertain?"
            "Guilt Trip",  # "Every dollar lost means a child loses opportunity."
            "Competitive Offer",  # "We have other funders interested."
            "Counter-Condition",  # "We will accept **X amount** if funds are guaranteed upfront."
            "Callout on Delays",  # "Pushing this to next quarter means lost opportunities."
        ]
        negotiation_tactic = random.choice(tactics)

        tactic_map = {
            "Urgency Appeal": "We can’t afford to wait—delays directly impact lives.",
            "Expose Corporate Contradiction": "You emphasize ESG, but funding hesitations slow real impact.",
            "Guilt Trip": "Every delay means a child loses access to education.",
            "Competitive Offer": "Other funders are interested, but we prefer working with you.",
            "Counter-Condition": f"We’ll agree to **${counter_offer:,.2f}**, but only with upfront payment.",
            "Callout on Delays": "Next quarter is too late. Are we committing today or not?"
        }
        negotiation_message = tactic_map[negotiation_tactic]

        if negotiation_message in self.previous_responses:
            negotiation_message = "This isn’t just numbers—it’s real impact."

        self.previous_responses.append(negotiation_message)

        # 📢 AI Prompt for Nonprofit
        prompt = f"""
        You are a **nonprofit negotiator** advocating for funding.
        - Corporate offers **${state.funding_offered:,.2f}**, 
        - You are requesting **${counter_offer:,.2f}**.

        **Rules:**
        - Speak like a negotiator (not an email).
        - Keep responses sharp (2-3 sentences max).
        - Apply pressure and challenge contradictions.

        Example: "{negotiation_message} We believe ${counter_offer:,.2f} is necessary. Can we align today?"
        """

        message = call_openai_with_retry(prompt)
        self.last_counter_offer = counter_offer
        return Offer(counter_offer, message)


# 📌 Negotiation State
class NegotiationState:
    def __init__(self, initial_funding: float, requested_funding: float, max_rounds: int = 10):
        if initial_funding <= 0:
            raise ValueError("Initial funding must be positive")
        if requested_funding <= initial_funding:
            raise ValueError("Requested funding must be greater than initial")

        self.initial_funding = initial_funding
        self.funding_offered = initial_funding
        self.funding_requested = requested_funding
        self.current_round = 1
        self.rounds_remaining = max_rounds
        self.status = "ONGOING"

        # ✅ Corporate & Nonprofit Goals
        self.corporate_goals = "We prioritize impactful, scalable projects aligned with ESG goals."
        self.nonprofit_mission = "Providing education & resources to underserved communities."
        self.nonprofit_impact = "Last year, we helped 10,000 students gain access to better learning materials."

        # ✅ Track Negotiation History
        self.history = NegotiationHistory()


# 📌 Negotiation Simulator
class NegotiationSimulator:
    def __init__(self, initial_funding: float, requested_funding: float, max_rounds: int = 10):
        self.state = NegotiationState(initial_funding, requested_funding, max_rounds)
        self.corporate = CorporateNegotiator()
        self.nonprofit = NonprofitNegotiator()

    def run(self):
        while self.state.status == "ONGOING" and self.state.current_round <= self.state.rounds_remaining:
            corporate_offer = self.corporate.make_offer(self.state)
            nonprofit_offer = self.nonprofit.make_offer(self.state)

            print(f"💼 Corporate: {corporate_offer}")
            print(f"🏛 Nonprofit: {nonprofit_offer}")

# Run the simulation
if __name__ == "__main__":
    simulator = NegotiationSimulator(100000, 150000)
    simulator.run()