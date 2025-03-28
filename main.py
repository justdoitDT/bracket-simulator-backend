from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def game_winner(seedA, seedB):
    """Simulates a game between two seeds."""
    if seedA == 1 and seedB == 16:
        odds = 0.993
    elif seedA == 2 and seedB == 15:
        odds = 0.938
    else:
        odds = 0.91 * max(seedA, seedB) / (seedA + seedB)
    return min(seedA, seedB) if odds > random.uniform(0, 1) else max(seedA, seedB)

def simulate_region(region_name):
    """Simulates one region of the bracket and returns all rounds."""
    field = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

    round_of_32 = [game_winner(field[i], field[i+1]) for i in range(0, 16, 2)]
    sweet_16 = [game_winner(round_of_32[i], round_of_32[i+1]) for i in range(0, 8, 2)]
    elite_8 = [game_winner(sweet_16[i], sweet_16[i+1]) for i in range(0, 4, 2)]
    regional_champ = game_winner(elite_8[0], elite_8[1])

    return {
        "region": region_name,
        "round_of_32": round_of_32,
        "sweet_16": sweet_16,
        "elite_8": elite_8,
        "regional_champ": regional_champ
    }

@app.get("/")
def root():
    """Root endpoint for testing."""
    return {"message": "Bracket Simulator API is live!"}

@app.get("/bracket")
def generate_bracket():
    """Simulates an entire bracket and returns all rounds."""
    
    top_left = simulate_region("Top Left")
    bottom_left = simulate_region("Bottom Left")
    top_right = simulate_region("Top Right")
    bottom_right = simulate_region("Bottom Right")

    left_champ = game_winner(top_left["regional_champ"], bottom_left["regional_champ"])
    right_champ = game_winner(top_right["regional_champ"], bottom_right["regional_champ"])
    national_champ = game_winner(left_champ, right_champ)

    return {
        "top_left": top_left,
        "bottom_left": bottom_left,
        "top_right": top_right,
        "bottom_right": bottom_right,
        "final_four": {"left": left_champ, "right": right_champ},
        "national_champion": national_champ
    }
