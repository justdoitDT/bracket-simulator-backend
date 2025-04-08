from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
import random
import math


app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def upset_probability(seedA, seedB, madness_level):
    high_seed = min(seedA, seedB)
    low_seed = max(seedA, seedB)
    seed_diff = abs(seedA - seedB)

    exponent = seed_diff ** (math.exp(-0.5117 * (madness_level - 1)))

    numerator = high_seed ** exponent
    denominator = high_seed ** exponent + low_seed ** exponent

    prob = numerator / denominator

    # Return the probability that seedA wins
    return prob if seedA < seedB else 1 - prob


def game_winner(seedA, seedB, madness_level):
    high_seed = min(seedA, seedB)
    low_seed = max(seedA, seedB)
    upset_prob = upset_probability(seedA, seedB, madness_level)
    return low_seed if random.random() < upset_prob else high_seed


def simulate_region(region_name, madness_level):
    """Simulates one region of the bracket and returns all rounds."""
    field = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
    round_of_32 = [game_winner(field[i], field[i+1], madness_level) for i in range(0, 16, 2)]
    sweet_16 = [game_winner(round_of_32[i], round_of_32[i+1], madness_level) for i in range(0, 8, 2)]
    elite_8 = [game_winner(sweet_16[i], sweet_16[i+1], madness_level) for i in range(0, 4, 2)]
    regional_champ = game_winner(elite_8[0], elite_8[1], madness_level)

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
def generate_bracket(madness_level: int = Query(5, ge=0, le=10)):
    # Simulate regions
    top_left = simulate_region("Top Left", madness_level)
    bottom_left = simulate_region("Bottom Left", madness_level)
    top_right = simulate_region("Top Right", madness_level)
    bottom_right = simulate_region("Bottom Right", madness_level)

    # Get regional champs
    left_champ_seed = game_winner(top_left["regional_champ"], bottom_left["regional_champ"], madness_level)
    right_champ_seed = game_winner(top_right["regional_champ"], bottom_right["regional_champ"], madness_level)

    # Helper to find the region based on seed
    def find_team(seed, regions):
        for region in regions:
            if region["regional_champ"] == seed:
                return {"region": region["region"], "seed": seed}
        return {"region": "Unknown", "seed": seed}

    # Build final four teams
    left_team = find_team(left_champ_seed, [top_left, bottom_left])
    right_team = find_team(right_champ_seed, [top_right, bottom_right])

    # Determine national champ seed and region
    national_champ_seed = game_winner(left_champ_seed, right_champ_seed, madness_level)
    national_champ_team = find_team(national_champ_seed, [top_left, bottom_left, top_right, bottom_right])

    # Return full bracket
    return {
        "top_left": top_left,
        "bottom_left": bottom_left,
        "top_right": top_right,
        "bottom_right": bottom_right,
        "final_four": {
            "left": left_team,
            "right": right_team
        },
        "national_champion": national_champ_team
    }

