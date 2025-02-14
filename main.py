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
        bankroll = float(entry_bankroll.get())
        kelly_fraction = float(entry_kelly_fraction.get()) / 100  # Convert percentage to decimal

        # Ensure all entries are filled and valid
        for key in entries:
            if not entries[key].get():
                raise ValueError(f"Please enter a value for {key.replace('entry_', '').replace('_', ' ').title()}")

        values = {key: float(entries[key].get()) for key in entries if key not in ["entry_match_score"]}
        home_goals, away_goals = map(int, entries["entry_match_score"].get().split("-"))

        remaining_time_factor = 0.5
        league_adjustment = (values["entry_league_position_away"] - values["entry_league_position_home"]) * 0.02

        # Red card impact: 30% reduction for the team with red cards, 30% increase for the opponent
        red_card_penalty_home = 0.3 if values["entry_red_cards_home"] > 0 else 0
        red_card_penalty_away = 0.3 if values["entry_red_cards_away"] > 0 else 0

        adjusted_home_goals = ((values["entry_home_scored"] + values["entry_xg_home"] * 0.5 - values["entry_away_conceded"]) *
                                remaining_time_factor * (1 + values["entry_possession_home"] / 100 + 
                                (values["entry_corners_home"] * 0.02) + (values["entry_shots_on_target_home"] * 0.03) - 
                                (values["entry_injuries_home"] * 0.05) - (values["entry_yellow_cards_home"] * 0.03) - 
                                red_card_penalty_home + league_adjustment))

        adjusted_away_goals = ((values["entry_away_scored"] + values["entry_xg_away"] * 0.5 - values["entry_home_conceded"]) *
                                remaining_time_factor * (1 + values["entry_possession_away"] / 100 + 
                                (values["entry_corners_away"] * 0.02) + (values["entry_shots_on_target_away"] * 0.03) - 
                                (values["entry_injuries_away"] * 0.05) - (values["entry_yellow_cards_away"] * 0.03) - 
                                red_card_penalty_away - league_adjustment))

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

        fair_odds = {
            "Home": 1 / home_win_prob, 
            "Draw": 1 / draw_prob, 
            "Away": 1 / away_win_prob
        }

        result_text = "Outcome | Fair Odds | Bookmaker Odds | Edge (%)\n"
        result_text += "-" * 50 + "\n"

        lay_bets = {}
        for outcome in fair_odds:
            bookmaker_odds = values[f"entry_bookmaker_odds_{outcome.lower()}"]
            if bookmaker_odds < fair_odds[outcome]:  
                lay_bets[outcome] = fair_odds[outcome]

            fair_prob = 1 / fair_odds[outcome]
            bookmaker_prob = 1 / bookmaker_odds
            edge = (fair_prob - bookmaker_prob) / bookmaker_prob * 100  # Convert to percentage

            result_text += f"{outcome}: {fair_odds[outcome]:.2f} | {bookmaker_odds:.2f} | {edge:.2f}%\n"

        if lay_bets:
            best_lay = min(lay_bets, key=lay_bets.get)
            bookmaker_odds = values[f"entry_bookmaker_odds_{best_lay.lower()}"]
            
            fair_prob = 1 / lay_bets[best_lay]
            bookmaker_prob = 1 / bookmaker_odds
            edge = (fair_prob - bookmaker_prob) / bookmaker_prob

            if edge > 0:
                kelly_stake_fraction = (edge / (bookmaker_odds - 1)) * kelly_fraction
                lay_stake = kelly_stake_fraction * bankroll
                liability = lay_stake * (bookmaker_odds - 1)

                result_text += "\nRecommended Lay Bet:\n"
                result_text += f"- {best_lay}\n"
                result_text += f"- Kelly Stake: £{lay_stake:.2f} ({kelly_stake_fraction * 100:.2f}%)\n"
                result_text += f"- Liability: £{liability:.2f}\n"
            else:
                result_text += "\nNo suitable lay bets found (No positive edge)."
        else:
            result_text += "\nNo suitable lay bets found."

        result_label["text"] = result_text

    except ValueError as e:
        result_label["text"] = f"Please enter valid numerical values. Error: {str(e)}"

def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    entry_bankroll.delete(0, tk.END)
    entry_kelly_fraction.delete(0, tk.END)
    result_label["text"] = ""

root = tk.Tk()
root.title("Half-Time Lay Betting Value Finder")
root.geometry("800x600")  # Set window size to 800x600

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
    ("Home Red Cards", "entry_red_cards_home"),
    ("Away Red Cards", "entry_red_cards_away"),
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

ttk.Label(root, text="Bankroll (£):").grid(row=len(fields), column=0, sticky="w")
entry_bankroll = ttk.Entry(root)
entry_bankroll.grid(row=len(fields), column=1, sticky="ew")

ttk.Label(root, text="Kelly Fraction (%):").grid(row=len(fields)+1, column=0, sticky="w")
entry_kelly_fraction = ttk.Entry(root)
entry_kelly_fraction.grid(row=len(fields)+1, column=1, sticky="ew")

calculate_button = ttk.Button(root, text="Calculate Lay Bet", command=calculate_probabilities)
calculate_button.grid(column=0, row=len(fields)+2, columnspan=2, pady=5, sticky="ew")

reset_button = ttk.Button(root, text="Reset Fields", command=reset_fields)
reset_button.grid(column=0, row=len(fields)+3, columnspan=2, pady=5, sticky="ew")

result_label = ttk.Label(root, text="", justify="left")
result_label.grid(column=0, row=len(fields)+4, columnspan=2, pady=5, sticky="ew")

root.mainloop()
