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
        home_goals, away_goals = map(int, entries["entry_match_score"].get().split("-"))
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

        # Time adjustment factor (only 45 mins left)
        remaining_time_factor = 0.5

        # League position impact
        league_adjustment = (league_position_away - league_position_home) * 0.02

        # Adjust expected goals for second half
        adjusted_home_goals = ((avg_goals_home_scored + xg_home * 0.5 - avg_goals_away_conceded) *
                                remaining_time_factor * (1 + possession_home + (corners_home * 0.02) +
                                (shots_on_target_home * 0.03) - (injuries_home * 0.05) -
                                (yellow_cards_home * 0.03) + league_adjustment))
        adjusted_away_goals = ((avg_goals_away_scored + xg_away * 0.5 - avg_goals_home_conceded) *
                                remaining_time_factor * (1 + possession_away + (corners_away * 0.02) +
                                (shots_on_target_away * 0.03) - (injuries_away * 0.05) -
                                (yellow_cards_away * 0.03) - league_adjustment))
        
        # Poisson probabilities for second half goals
        home_win_prob = sum([poisson_probability(adjusted_home_goals, i + home_goals) for i in range(5)])
        away_win_prob = sum([poisson_probability(adjusted_away_goals, i + away_goals) for i in range(5)])
        draw_prob = sum([poisson_probability(adjusted_home_goals, i + home_goals) * poisson_probability(adjusted_away_goals, i + away_goals) for i in range(5)])

        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        fair_odds = {
            "Home": 1 / home_win_prob,
            "Draw": 1 / draw_prob,
            "Away": 1 / away_win_prob,
        }

        # Only considering LAY bets (when bookmaker odds are lower than calculated fair odds)
        lay_bets = {}
        for outcome in ["Home", "Draw", "Away"]:
            if eval(f'bookmaker_odds_{outcome.lower()}') < fair_odds[outcome]:
                lay_bets[outcome] = fair_odds[outcome]
        
        if lay_bets:
            best_lay = min(lay_bets, key=lay_bets.get)
            result_label["text"] = f"Recommended Lay Bet: {best_lay}\nFair Odds: {lay_bets[best_lay]:.2f}\nBookmaker Odds: {eval(f'bookmaker_odds_{best_lay.lower()}'):.2f}"
        else:
            result_label["text"] = "No suitable Lay bets found."
    except ValueError:
        result_label["text"] = "Please enter valid numerical values."

# UI setup
root = tk.Tk()
root.title("Half-Time Lay Betting Value Finder")

fields = [
    ("Home Team Avg Goals Scored", "entry_home_scored"),
    ("Home Team Avg Goals Conceded", "entry_home_conceded"),
    ("Away Team Avg Goals Scored", "entry_away_scored"),
    ("Away Team Avg Goals Conceded", "entry_away_conceded"),
    ("Match Score (e.g., 1-1)", "entry_match_score"),
    ("Home Team xG", "entry_xg_home"),
    ("Away Team xG", "entry_xg_away"),
    ("Home Team Possession (%)", "entry_possession_home"),
    ("Away Team Possession (%)", "entry_possession_away"),
    ("Home Team Shots on Target", "entry_shots_on_target_home"),
    ("Away Team Shots on Target", "entry_shots_on_target_away"),
    ("Home Team Corners", "entry_corners_home"),
    ("Away Team Corners", "entry_corners_away"),
    ("Home Team Injuries", "entry_injuries_home"),
    ("Away Team Injuries", "entry_injuries_away"),
    ("Home Team Yellow Cards", "entry_yellow_cards_home"),
    ("Away Team Yellow Cards", "entry_yellow_cards_away"),
    ("Home Team League Position", "entry_league_position_home"),
    ("Away Team League Position", "entry_league_position_away"),
    ("Bookmaker Odds Home", "entry_bookmaker_odds_home"),
    ("Bookmaker Odds Draw", "entry_bookmaker_odds_draw"),
    ("Bookmaker Odds Away", "entry_bookmaker_odds_away"),
    ("Account Balance", "entry_account_balance")
]

entries = {}
for label_text, var_name in fields:
    label = tk.Label(root, text=label_text)
    label.grid(column=0, row=len(entries), padx=10, pady=5, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(column=1, row=len(entries), padx=10, pady=5, sticky="ew")
    entries[var_name] = entry

calculate_button = ttk.Button(root, text="Calculate Lay Bet", command=calculate_probabilities)
calculate_button.grid(column=0, row=len(entries), columnspan=2, pady=10, sticky="ew")
reset_button = ttk.Button(root, text="Reset Fields", command=lambda: [entry.delete(0, tk.END) for entry in entries.values()])
reset_button.grid(column=0, row=len(entries)+1, columnspan=2, pady=10, sticky="ew")
result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.grid(column=0, row=len(entries)+2, columnspan=2, pady=10)
root.columnconfigure(1, weight=1)
root.mainloop()
