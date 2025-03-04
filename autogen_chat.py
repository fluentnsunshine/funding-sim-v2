from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import logging
import re  # Added for number extraction
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain_core.runnables import RunnableLambda
from langchain.prompts import PromptTemplate

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventType(Enum):
    FUNDING_CUT = "Funding Cut"
    SURPRISE_DONOR = "Surprise Donor"
    SCANDAL = "Scandal!"
    TIME_PRESSURE = "Time Pressure"

@dataclass
class Offer:
    amount: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        return f"${self.amount:,.2f}: {self.message}"

# 📌 Number Extraction Fix
def extract_number(text):
    """Extracts the first valid number from a string"""
    matches = re.findall(r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)", text)
    if matches:
        return float(matches[0].replace(",", "").replace("$", ""))
    return None

class CorporateTactic(Enum):
    CONDITIONAL_TERMS = "Conditional Terms"
    BAIT_AND_SWITCH = "Bait and Switch"
    DELAY = "Delay Response"
    WALKAWAY = "Walkaway Threat"

class NonprofitTactic(Enum):
    URGENCY_APPEAL = "Urgency Appeal"
    COMPETITIVE_OFFER = "Competitive Offer"
    WALKAWAY_THREAT = "Walkaway Threat"

class NegotiationHistory:
    def __init__(self):
        self.corporate_offers: List[Offer] = []
        self.nonprofit_offers: List[Offer] = []
        self.events: List[Tuple[EventType, datetime]] = []
        
    def get_last_offer(self, party: str) -> Optional[Offer]:
        if party == "corporate" and self.corporate_offers:
            return self.corporate_offers[-1]
        elif party == "nonprofit" and self.nonprofit_offers:
            return self.nonprofit_offers[-1]
        return None

    def add_offer(self, party: str, offer: Offer):
        if party == "corporate":
            self.corporate_offers.append(offer)
        elif party == "nonprofit":
            self.nonprofit_offers.append(offer)

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
        self.nonprofit_urgency = 5  # Default urgency level
        
        # Initialize history as a NegotiationHistory object instead of a list
        self.history = NegotiationHistory()
        
        # For the nonprofit negotiator
        self.min_acceptable = initial_funding * 1.2  # Example value
    
    def update_offer(self, new_offer: float):
        self.funding_offered = new_offer
        logger.info(f"Updated funding offer to: ${new_offer:,.2f}")

class CorporateNegotiator:
    def __init__(self):
        self.reputation_score = 100
        self.original_offer = None
        self.delay_counter = 0

    def choose_tactic(self, state):
        """Decides which tactic to use based on the situation."""
        if state.current_round < 3 and random.random() < 0.3:
            return CorporateTactic.BAIT_AND_SWITCH
        elif state.current_round > 4 and state.funding_offered < state.funding_requested * 0.8:
            return CorporateTactic.WALKAWAY
        elif random.random() < 0.2:
            return CorporateTactic.CONDITIONAL_TERMS
        return None

    def make_offer(self, state):
        """Makes an offer with strategic adjustments."""
        tactic = self.choose_tactic(state)
        base_offer = state.funding_offered

        if tactic == CorporateTactic.BAIT_AND_SWITCH:
            if not self.original_offer:
                self.original_offer = state.funding_requested * 0.9
                return Offer(self.original_offer, f"We are offering a generous ${self.original_offer:,.2f}!")
            else:
                reduced_offer = self.original_offer * 0.75
                return Offer(reduced_offer, f"Due to budget constraints, we must lower our offer to ${reduced_offer:,.2f}.")

        elif tactic == CorporateTactic.WALKAWAY:
            return Offer(base_offer, "If we can't reach an agreement, we may need to walk away.")

        elif tactic == CorporateTactic.CONDITIONAL_TERMS:
            increased_offer = base_offer * 1.1
            return Offer(increased_offer, f"We can increase funding to ${increased_offer:,.2f} if you match 10%.")

        return Offer(base_offer, f"We maintain our offer of ${base_offer:,.2f}.")

import random
from enum import Enum

class NonprofitTactic(Enum):
    URGENCY_APPEAL = "Urgency Appeal"
    COMPETITIVE_OFFER = "Competitive Offer"
    WALKAWAY_THREAT = "Walkaway Threat"
    GRADUAL_COMPROMISE = "Gradual Compromise"
    FINAL_APPEAL = "Final Appeal"

class Offer:
    def __init__(self, amount, message):
        self.amount = amount
        self.message = message

    def __str__(self):
        return f"${self.amount:,.2f}: {self.message}"

class NonprofitNegotiator:
    def __init__(self):
        self.last_counter_offer = None
        self.competitive_offer = None
        self.concession_step = 0.05  # Reduce ask by 5% each round if no movement

    def choose_tactic(self, state):
        """Decides which tactic to use based on negotiation conditions."""
        if state.nonprofit_urgency > 7 and random.random() < 0.4:
            return NonprofitTactic.URGENCY_APPEAL
        elif state.current_round > 3 and random.random() < 0.3:
            return NonprofitTactic.COMPETITIVE_OFFER
        elif state.current_round > 5 and random.random() < 0.2:
            return NonprofitTactic.WALKAWAY_THREAT
        elif state.current_round > 7:
            return NonprofitTactic.GRADUAL_COMPROMISE
        elif state.current_round == state.rounds_remaining - 1:
            return NonprofitTactic.FINAL_APPEAL
        return None

    def make_offer(self, state):
        """Makes a counter-offer based on the selected tactic."""
        tactic = self.choose_tactic(state)
        counter_offer = state.funding_requested

        if tactic == NonprofitTactic.URGENCY_APPEAL:
            counter_offer = max(state.funding_offered * 1.15, state.min_acceptable)
            return Offer(counter_offer, "Without additional funding, we may have to cut critical programs. We urgently request ${:,.2f}.".format(counter_offer))

        elif tactic == NonprofitTactic.COMPETITIVE_OFFER:
            counter_offer = max(state.funding_offered * 1.10, state.min_acceptable)
            return Offer(counter_offer, "Another sponsor has shown interest in funding us at ${:,.2f}. Can you match this?".format(counter_offer))

        elif tactic == NonprofitTactic.WALKAWAY_THREAT:
            return Offer(state.funding_offered, "If we cannot secure the necessary funding, we may need to seek alternative donors. We hope you can reconsider.")

        elif tactic == NonprofitTactic.GRADUAL_COMPROMISE:
            new_offer = max(state.funding_requested * (1 - self.concession_step * state.current_round), state.funding_offered * 1.05)
            return Offer(new_offer, "We are willing to adjust our request to ${:,.2f} to find a middle ground.".format(new_offer))

        elif tactic == NonprofitTactic.FINAL_APPEAL:
            return Offer(state.funding_offered, "This is our final appeal. We need your support to continue our mission.")

        return Offer(counter_offer, "We maintain our request for ${:,.2f}.".format(counter_offer))

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
        self.nonprofit_urgency = 5  # Default urgency level
        self.history = []  # Store history of offers and events as a list of dictionaries
    
    def add_offer(self, role, offer):
        """Track offers made during negotiation."""
        self.history.append({"role": role, "offer": offer})

class NegotiationSimulator:
    def __init__(self, initial_funding: float, requested_funding: float, max_rounds: int = 10):
        self.state = NegotiationState(initial_funding, requested_funding, max_rounds)
        self.corporate = CorporateNegotiator()
        self.nonprofit = NonprofitNegotiator()
        
    def run(self):
        logger.info("Starting AI-powered negotiation simulation...")
        
        while self.state.status == "ONGOING" and self.state.current_round <= self.state.rounds_remaining:
            print(f"\n🔄 Round {self.state.current_round}")

            corporate_offer = self.corporate.make_offer(self.state)
            self.state.history.add_offer("corporate", corporate_offer)
            print(f"💼 Corporate: {corporate_offer}")

            nonprofit_offer = self.nonprofit.make_offer(self.state)
            self.state.history.add_offer("nonprofit", nonprofit_offer)
            print(f"🏛 Nonprofit: {nonprofit_offer}")

            if corporate_offer.amount >= nonprofit_offer.amount:
                self.state.status = "ACCEPTED"
                print("🤝 Agreement reached!")

            self.state.current_round += 1

        self._print_final_report()

    def _print_final_report(self):
        print("\n📊 AI-Powered Negotiation Final Report")
        print(f"Status: {self.state.status}")
        print(f"Initial Offer: ${self.state.initial_funding:,.2f}")
        print(f"Final Offer: ${self.state.funding_offered:,.2f}")
        print(f"Requested: ${self.state.funding_requested:,.2f}")
        print(f"Rounds Completed: {self.state.current_round - 1}")

if __name__ == "__main__":
    simulator = NegotiationSimulator(
        initial_funding=100000,
        requested_funding=150000
    )
    simulator.run()