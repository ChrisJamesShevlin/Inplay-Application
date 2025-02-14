import tkinter as tk
from tkinter import ttk
import math

def poisson_probability(mean, k):
    return (math.exp(-mean) * (mean ** k)) / math.factorial(k)

def calculate_probabilities():
    try:
        avg_goals_home_scored = float(entries["entry_home_scored"].get())
        avg_goals_home_conceded = float(entries["entry_home_conceded"].get())
        avg_goals_away_scored = float(entries["entry_away_scored"].get())
        avg_goals_away_conceded = float(entries["entry_away_conceded"].get())
        current_home_goals = int(entries["entry_current_home_goals"].get())
        current_away_goals = int(entries["entry_current_away_goals"].get())
        elapsed_time = int(entries["entry_elapsed_time"].get())
        xg_home = float(entries["entry_xg_home"].get())
        xg_away = float(entries["entry_xg_away"].get())
        possession_home = float(entries["entry_possession_home"].get()) / 100
        possession_away = float(entries["entry_possession_away"].get()) / 100
        shots_on_target_home = int(entries["entry_shots_on_target_home"].get())
        shots_on_target_away = int(entries["entry_shots_on_target_away"].get())
        corners_home = int(entries["entry_corners_home"].get())
        corners_away = int(entries["entry_corners_away"].get())
        injuries_home = int(entries["entry_injuries_home"].get())
        injuries_away = int(entries["entry_injuries_away"].get())
        yellow_cards_home = int(entries["entry_yellow_cards_home"].get())
        yellow_cards_away = int(entries["entry_yellow_cards_away"].get())
        league_position_home = int(entries["entry_league_position_home"].get())
        league_position_away = int(entries["entry_league_position_away"].get())
        bookmaker_odds_home = float(entries["entry_bookmaker_odds_home"].get())
        bookmaker_odds_draw = float(entries["entry_bookmaker_odds_draw"].get())
        bookmaker_odds_away = float(entries["entry_bookmaker_odds_away"].get())
        account_balance = float(entries["entry_account_balance"].get())

        # Adjust goals based on various factors, including league position
        remaining_time_factor = max(0.1, (90 - elapsed_time) / 90)
        league_adjustment = (league_position_away - league_position_home) * 0.02
        adjusted_home_goals = (avg_goals_home_scored + xg_home * 0.5 - avg_goals_away_conceded) * remaining_time_factor * (1 + possession_home + (corners_home * 0.02) + (shots_on_target_home * 0.03) - (injuries_home * 0.05) - (yellow_cards_home * 0.03) + league_adjustment)
        adjusted_away_goals = (avg_goals_away_scored + xg_away * 0.5 - avg_goals_home_conceded) * remaining_time_factor * (1 + possession_away + (corners_away * 0.02) + (shots_on_target_away * 0.03) - (injuries_away * 0.05) - (yellow_cards_away * 0.03) - league_adjustment)

        # Predict probabilities using Poisson distribution
        home_win_prob = sum([poisson_probability(adjusted_home_goals, i) for i in range(5)])
        away_win_prob = sum([poisson_probability(adjusted_away_goals, i) for i in range(5)])
        draw_prob = sum([poisson_probability(adjusted_home_goals, i) * poisson_probability(adjusted_away_goals, i) for i in range(5)])

        # Normalize probabilities
        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        # Convert probabilities to fair odds
        fair_odds = {
            "Home": 1 / home_win_prob,
            "Draw": 1 / draw_prob,
            "Away": 1 / away_win_prob,
        }

        # Calculate edges
        edges = {
            "Home": (1 / bookmaker_odds_home) - (1 / fair_odds["Home"]),
            "Draw": (1 / bookmaker_odds_draw) - (1 / fair_odds["Draw"]),
            "Away": (1 / bookmaker_odds_away) - (1 / fair_odds["Away"]),
        }

        best_bet = max(edges, key=edges.get)
        best_edge = edges[best_bet]

        # Kelly criterion for staking
        def kelly_stake(edge, balance):
            return max(0, (0.20 * edge * balance)) if edge > 0 else 0

        recommended_stake = kelly_stake(best_edge, account_balance)

        result_label["text"] = (f"Recommended Bet: {best_bet}\n"
                                f"Edge: {best_edge:.4f}\n"
                                f"Stake: £{recommended_stake:.2f}\n"
                                f"Fair Odds: {fair_odds[best_bet]:.2f}\n"
                                f"Bookmaker Odds: {eval(f'bookmaker_odds_{best_bet.lower()}'):.2f}")
    except ValueError:
        result_label["text"] = "Please enter valid numerical values."

def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    result_label["text"] = ""

# UI setup
root = tk.Tk()
root.title("In-Play Match Odds Value Finder")

# Create a dictionary to hold the entry widgets
entries = {}

# Define the fields and their labels
fields = [
    ("Home Team Average Goals Scored", "entry_home_scored"),
    ("Home Team Average Goals Conceded", "entry_home_conceded"),
    ("Away Team Average Goals Scored", "entry_away_scored"),
    ("Away Team Average Goals Conceded", "entry_away_conceded"),
    ("Current Home Goals", "entry_current_home_goals"),
    ("Current Away Goals", "entry_current_away_goals"),
    ("Elapsed Time (minutes)", "entry_elapsed_time"),
    ("Home Expected Goals (xG)", "entry_xg_home"),
    ("Away Expected Goals (xG)", "entry_xg_away"),
    ("Home Possession (%)", "entry_possession_home"),
    ("Away Possession (%)", "entry_possession_away"),
    ("Home Shots on Target", "entry_shots_on_target_home"),
    ("Away Shots on Target", "entry_shots_on_target_away"),
    ("Home Corners", "entry_corners_home"),
    ("Away Corners", "entry_corners_away"),
    ("Home Injuries", "entry_injuries_home"),
    ("Away Injuries", "entry_injuries_away"),
    ("Home Yellow Cards", "entry_yellow_cards_home"),
    ("Away Yellow Cards", "entry_yellow_cards_away"),
    ("Home Team League Position", "entry_league_position_home"),
    ("Away Team League Position", "entry_league_position_away"),
    ("Bookmaker Odds for Home Win", "entry_bookmaker_odds_home"),
    ("Bookmaker Odds for Draw", "entry_bookmaker_odds_draw"),
    ("Bookmaker Odds for Away Win", "entry_bookmaker_odds_away"),
    ("Account Balance", "entry_account_balance"),
]

# Create the labels and entry widgets in a grid layout
for idx, (label_text, var_name) in enumerate(fields):
    label = tk.Label(root, text=label_text)
    label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")
    entries[var_name] = entry

# Add the calculate and reset buttons
calculate_button = ttk.Button(root, text="Calculate Value Bets", command=calculate_probabilities)
calculate_button.grid(row=len(fields), column=0, columnspan=2, pady=10, sticky="ew")

reset_button = ttk.Button(root, text="Reset Fields", command=reset_fields)
reset_button.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10, sticky="ew")

# Add the result label
result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.grid(row=len(fields) + 2, column=0, columnspan=2, pady=10)

# Make the second column expandable
root.columnconfigure(1, weight=1)

root.mainloop()
