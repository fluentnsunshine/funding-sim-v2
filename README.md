Funding Journey Simulator 🏛💰

An AI-powered negotiation game between corporate funders and nonprofits


🔹 About the Project

Funding Journey Simulator is an AI-driven negotiation simulation where a corporate funder and a nonprofit attempt to reach a funding agreement. This interactive tool models real-world funding discussions, strategic decision-making, and AI-driven deal-making.
	•	💼 Corporate Tactics: Bait-and-switch, conditional terms, delay responses, walkaway threats
	•	🏛 Nonprofit Strategies: Urgency appeals, competitive offers, gradual compromises
	•	🎭 Random Events: Funding cuts, surprise donors, time pressure, and scandals

This project uses LangChain + AutoGen to simulate AI-powered negotiations.

🚀 Features

✅ Multi-turn AI negotiation loop
✅ Strategic decision-making for corporate & nonprofit roles
✅ Dynamic negotiation history tracking
✅ Memory-based adaptation for smarter AI responses

🛠️ Installation & Setup

1️⃣ Clone the Repository

git clone git@github.com:fluentnsunshine/funding-sim-v2.git
cd funding-sim-v2

2️⃣ Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate  # (Mac/Linux)
venv\Scripts\activate      # (Windows)

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Set Up Your .env File

Create a .env file and add your OpenAI API key:

OPENAI_API_KEY=your-key-here

(Note: The .env file is ignored in Git and should not be shared.)

▶️ Running the Simulator

Start the negotiation simulator with:

python autogen_chat.py

The AI will begin a back-and-forth negotiation between Corporate Baddie and Nonprofit Baby, tracking offers, counteroffers, and strategic decisions.

📌 Future Improvements

🔹 Improve AI memory for more adaptive negotiations
🔹 Add visualization tools to track funding history
🔹 Enhance strategy logic for better realism

📜 License

This project is licensed under the MIT License.

🤝 Contributing

Pull requests are welcome! If you’d like to contribute, fork the repo and submit a PR.