import tkinter as tk
from tkinter import ttk
import math

def poisson_probability(mean, k):
    return (math.exp(-mean) * (mean ** k)) / math.factorial(k)

def empirical_goal_probability(avg_goals, variance=0.8):
    """Approximates goal probability using a normal distribution assumption."""
    return 1 - math.exp(-avg_goals / variance)

def calculate_probabilities():
    try:
        bankroll = float(entries["entry_bankroll"].get())
        kelly_fraction = float(entries["entry_kelly_fraction"].get()) / 100

        values = {key: float(entries[key].get()) for key in entries if key != "entry_match_score"}
        home_goals, away_goals = map(int, entries["entry_match_score"].get().split("-"))

        # Adjust time scaling based on match score
        remaining_time_factor = 0.35 if away_goals > home_goals else (0.6 if home_goals > away_goals else 0.5)

        # Adjust goal expectancy dynamically
        adjusted_home_goals = values["entry_home_avg_goals_scored"] * remaining_time_factor
        adjusted_away_goals = values["entry_away_avg_goals_scored"] * remaining_time_factor

        if home_goals < away_goals:
            adjusted_home_goals *= 1.2  # Boost attacking intent for trailing team
            adjusted_away_goals *= 0.9  # Defensive adjustments for leading team
        elif home_goals > away_goals:
            adjusted_home_goals *= 0.85
            adjusted_away_goals *= 1.1

        # Apply league position weighting (teams higher in the league tend to perform better)
        league_position_factor = 1 + ((values["entry_league_position_away"] - values["entry_league_position_home"]) * 0.02)
        adjusted_home_goals *= league_position_factor
        adjusted_away_goals /= league_position_factor

        # Apply empirical second-half probabilities
        historical_win_rates = {
            "Trailing Home Team": 0.18,
            "Leading Away Team": 0.55,
            "Drawn at Half": 0.27
        }

        if home_goals < away_goals:
            home_win_prob = historical_win_rates["Trailing Home Team"]
            away_win_prob = historical_win_rates["Leading Away Team"]
        elif home_goals > away_goals:
            home_win_prob = historical_win_rates["Leading Away Team"]
            away_win_prob = historical_win_rates["Trailing Home Team"]
        else:
            home_win_prob = historical_win_rates["Drawn at Half"]
            away_win_prob = 1 - (home_win_prob + (1 - home_win_prob - away_win_prob))

        draw_prob = 1 - (home_win_prob + away_win_prob)

        # Normalize probabilities
        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        # Compute fair odds
        fair_odds = {
            "Home": 1 / home_win_prob,
            "Draw": 1 / draw_prob,
            "Away": 1 / away_win_prob
        }

        # Market calibration
        market_calibration_factor = values["entry_bookmaker_odds_home"] / fair_odds["Home"]
        final_fair_odds = {outcome: fair_odds[outcome] * market_calibration_factor for outcome in fair_odds}

        # Compute edge percentages and Kelly staking
        best_lay_bet = None
        best_edge = float('inf')  # We are looking for the most negative edge
        best_stake = 0

        result_text = "Outcome | Fair Odds | Bookmaker Odds | Edge (%) | Kelly Stake (£)\n" + "-" * 70 + "\n"
        for outcome in final_fair_odds:
            bookmaker_odds = values[f"entry_bookmaker_odds_{outcome.lower()}"]
            fair_prob = 1 / final_fair_odds[outcome]
            bookmaker_prob = 1 / bookmaker_odds
            edge = (fair_prob - bookmaker_prob) / bookmaker_prob * 100
            kelly_stake = 0

            if edge <= -50:  # Only consider edges of -50 or less
                kelly_stake = bankroll * kelly_fraction * (edge / 100)  # Kelly Criterion applied
                if edge < best_edge:  # Select the best lay bet with the most negative edge
                    best_edge = edge
                    best_lay_bet = outcome
                    best_stake = kelly_stake

            result_text += f"{outcome}: {final_fair_odds[outcome]:.2f} | {bookmaker_odds:.2f} | {edge:.2f}% | {kelly_stake:.2f}\n"

        if best_lay_bet:
            result_text += f"\nBest Lay Bet: {best_lay_bet} for £{best_stake:.2f} at odds {values[f'entry_bookmaker_odds_{best_lay_bet.lower()}']}"
        else:
            result_text += "\nNo suitable lay bet found based on current market prices."

        result_label["text"] = result_text

    except ValueError as e:
        result_label["text"] = f"Please enter valid numerical values. Error: {str(e)}"

# **🔹 UI Setup**
root = tk.Tk()
root.title("Half-Time Lay Betting Value Finder")
root.geometry("800x900")

fields = [
    ("Match Score (e.g., 1-1)", "entry_match_score"),
    ("Home Avg Goals Scored", "entry_home_avg_goals_scored"),
    ("Home Avg Goals Conceded", "entry_home_avg_goals_conceded"),
    ("Away Avg Goals Scored", "entry_away_avg_goals_scored"),
    ("Away Avg Goals Conceded", "entry_away_avg_goals_conceded"),
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
    ("Bookmaker Odds Away", "entry_bookmaker_odds_away"),
    ("Bankroll (£)", "entry_bankroll"),
    ("Kelly Fraction (%)", "entry_kelly_fraction"),
]

entries = {var: ttk.Entry(root) for _, var in fields}
for i, (label, var) in enumerate(fields):
    ttk.Label(root, text=label).grid(row=i, column=0, sticky="w")
    entries[var].grid(row=i, column=1, sticky="ew")

calculate_button = ttk.Button(root, text="Calculate Lay Bet", command=calculate_probabilities)
calculate_button.grid(column=0, row=len(fields)+2, columnspan=2, pady=5, sticky="ew")

result_label = ttk.Label(root, text="", justify="left")
result_label.grid(column=0, row=len(fields)+3, columnspan=2, pady=5, sticky="ew")

root.mainloop()
