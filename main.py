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


def win_probability(seedA, seedB, madness_level):
    """
    Returns the win probability for seedA over seedB based on madness level (0 = chalk, 10 = madness).
    Uses nonlinear exponent scaling and special handling for 1v16, 2v15.
    """
    chaos = madness_level / 10

    # At full madness, return pure 50/50
    if chaos >= 0.999:
        return 0.5

    # Special protection for 1 vs 16 and 2 vs 15, fades with madness
    if (seedA, seedB) in [(1, 16), (16, 1)]:
        base_prob = 0.993
        return base_prob * (1 - chaos) + 0.5 * chaos
    elif (seedA, seedB) in [(2, 15), (15, 2)]:
        base_prob = 0.938
        return base_prob * (1 - chaos) + 0.5 * chaos

    # Use nonlinear exponent: exponential decay gives more variety across range
    exponent = 2 ** (1 - chaos)  # e.g., 5 at chalk, ~1.0 at 0.7, ~0.5 at 0.9

    powerA = seedA ** exponent
    powerB = seedB ** exponent

    return powerB / (powerA + powerB)


def game_winner(seedA, seedB, madness_level):
    prob = win_probability(seedA, seedB, madness_level)
    return seedA if random.random() < prob else seedB

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

