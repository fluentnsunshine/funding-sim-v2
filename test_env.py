import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Quick check
print("Neon Database URL:", os.getenv("NEON_DATABASE_URL"))