import tkinter as tk
from tkinter import ttk
import math

def poisson_probability(mean, k):
    return (math.exp(-mean) * (mean ** k)) / math.factorial(k)

def zero_inflated_poisson_probability(mean, k, p_zero_inflation):
    if k == 0:
        return p_zero_inflation + (1 - p_zero_inflation) * poisson_probability(mean, k)
    else:
        return (1 - p_zero_inflation) * poisson_probability(mean, k)

def calculate_probabilities():
    try:
        values = {key: float(entries[key].get()) for key in entries if key not in ["entry_match_score"]}
        home_goals, away_goals = map(int, entries["entry_match_score"].get().split("-"))
        
        remaining_time_factor = 0.5
        league_adjustment = (values["entry_league_position_away"] - values["entry_league_position_home"]) * 0.02
        
        adjusted_home_goals = ((values["entry_home_scored"] + values["entry_xg_home"] * 0.5 - values["entry_away_conceded"]) *
                                remaining_time_factor * (1 + values["entry_possession_home"] / 100 + (values["entry_corners_home"] * 0.02) +
                                (values["entry_shots_on_target_home"] * 0.03) - (values["entry_injuries_home"] * 0.05) -
                                (values["entry_yellow_cards_home"] * 0.03) + league_adjustment))
        
        adjusted_away_goals = ((values["entry_away_scored"] + values["entry_xg_away"] * 0.5 - values["entry_home_conceded"]) *
                                remaining_time_factor * (1 + values["entry_possession_away"] / 100 + (values["entry_corners_away"] * 0.02) +
                                (values["entry_shots_on_target_away"] * 0.03) - (values["entry_injuries_away"] * 0.05) -
                                (values["entry_yellow_cards_away"] * 0.03) - league_adjustment))
        
        p_zero_inflation_home = max(0, min(0.3, 0.1 - values["entry_xg_home"] * 0.05 - values["entry_shots_on_target_home"] * 0.02))
        p_zero_inflation_away = max(0, min(0.3, 0.1 - values["entry_xg_away"] * 0.05 - values["entry_shots_on_target_away"] * 0.02))

        home_win_prob = sum([zero_inflated_poisson_probability(adjusted_home_goals, i + home_goals, p_zero_inflation_home) for i in range(5)])
        away_win_prob = sum([zero_inflated_poisson_probability(adjusted_away_goals, i + away_goals, p_zero_inflation_away) for i in range(5)])
        draw_prob = sum([zero_inflated_poisson_probability(adjusted_home_goals, i + home_goals, p_zero_inflation_home) * 
                         zero_inflated_poisson_probability(adjusted_away_goals, i + away_goals, p_zero_inflation_away) for i in range(5)])
        
        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        fair_odds = {"Home": 1 / home_win_prob, "Draw": 1 / draw_prob, "Away": 1 / away_win_prob}
        
        lay_bets = {outcome: fair_odds[outcome] for outcome in fair_odds if values[f"entry_bookmaker_odds_{outcome.lower()}"] < fair_odds[outcome]}
        
        if lay_bets:
            best_lay = min(lay_bets, key=lay_bets.get)
            result_label["text"] = f"Recommended Lay Bet: {best_lay}\nFair Odds: {lay_bets[best_lay]:.2f}\nBookmaker Odds: {values[f'entry_bookmaker_odds_{best_lay.lower()}']:.2f}"
        else:
            result_label["text"] = "No suitable Lay bets found."
    except ValueError:
        result_label["text"] = "Please enter valid numerical values."

root = tk.Tk()
root.title("Half-Time Lay Betting Value Finder")

fields = [
    ("Home Avg Goals Scored", "entry_home_scored"),
    ("Home Avg Goals Conceded", "entry_home_conceded"),
    ("Away Avg Goals Scored", "entry_away_scored"),
    ("Away Avg Goals Conceded", "entry_away_conceded"),
    ("Match Score (e.g., 1-1)", "entry_match_score"),
    ("Home xG", "entry_xg_home"),
    ("Away xG", "entry_xg_away"),
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
    ("Home League Position", "entry_league_position_home"),
    ("Away League Position", "entry_league_position_away"),
    ("Bookmaker Odds Home", "entry_bookmaker_odds_home"),
    ("Bookmaker Odds Draw", "entry_bookmaker_odds_draw"),
    ("Bookmaker Odds Away", "entry_bookmaker_odds_away")
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    ttk.Label(root, text=label_text).grid(row=i, column=0, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(row=i, column=1, sticky="ew")
    entries[var_name] = entry

calculate_button = ttk.Button(root, text="Calculate Lay Bet", command=calculate_probabilities)
calculate_button.grid(column=0, row=len(entries), columnspan=2, pady=5, sticky="ew")

reset_button = ttk.Button(root, text="Reset Fields", command=lambda: [entry.delete(0, tk.END) for entry in entries.values()])
reset_button.grid(column=0, row=len(entries)+1, columnspan=2, pady=5, sticky="ew")

result_label = tk.Label(root, text="", font=("Helvetica", 12))
result_label.grid(column=0, row=len(entries)+2, columnspan=2, pady=5)

root.columnconfigure(1, weight=1)
root.mainloop()
