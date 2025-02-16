import tkinter as tk
from tkinter import ttk
import math

def poisson_pmf(k, lam):
    """Manual Poisson probability mass function."""
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def zero_inflated_poisson(lam, zero_inflation=0.1):
    """Calculate the probability mass function with zero inflation."""
    return zero_inflation + (1 - zero_inflation) * poisson_pmf(0, lam)

def kelly_criterion(fair_odds, bookmaker_odds, bankroll=100, fraction=0.25):
    if bookmaker_odds >= fair_odds:
        return 0  # No value bet
    edge = (fair_odds - bookmaker_odds) / bookmaker_odds
    kelly_fraction = edge / fair_odds
    return bankroll * kelly_fraction * fraction

def calculate_fair_odds():
    try:
        values = {}
        for entry, widget in entries.items():
            if entry == 'current_score':
                home_score, away_score = map(int, widget.get().split('-'))
                values['home_score'] = home_score
                values['away_score'] = away_score
            else:
                values[entry.replace('-', '_')] = float(widget.get())  # Replace hyphens with underscores
        print("Input values:", values)  # Debugging print statement

        home_attack_strength = (values['avg_home_goals_scored'] / values['avg_away_goals_conceded']) * (1 / values['pre_match_home_odds'])
        away_attack_strength = (values['avg_away_goals_scored'] / values['avg_home_goals_conceded']) * (1 / values['pre_match_away_odds'])

        weight = 0.1  # Reduced from 0.2
        attack_boost_home = (values['home_shots_on_target'] + 0.5 * values['home_expected_goals'] + 0.3 * values['home_corners']) * weight
        attack_boost_away = (values['away_shots_on_target'] + 0.5 * values['away_expected_goals'] + 0.3 * values['away_corners']) * weight
        defense_penalty_home = (values['home_yellow_cards'] * 0.1 + values['home_red_cards'] * 0.3 + values['home_injuries'] * 0.2) * weight
        defense_penalty_away = (values['away_yellow_cards'] * 0.1 + values['away_red_cards'] * 0.3 + values['away_injuries'] * 0.2) * weight

        adjusted_home_strength = home_attack_strength + attack_boost_home - defense_penalty_home
        adjusted_away_strength = away_attack_strength + attack_boost_away - defense_penalty_away

        halftime_home_goals = max(adjusted_home_strength * 0.5, 0.1)  # Prevent extreme values
        halftime_away_goals = max(adjusted_away_strength * 0.5, 0.1)

        home_win_prob = 1 - zero_inflated_poisson(halftime_home_goals)
        away_win_prob = 1 - zero_inflated_poisson(halftime_away_goals)

        draw_prob = sum(poisson_pmf(i, halftime_home_goals) * poisson_pmf(i, halftime_away_goals) for i in range(5))
        draw_prob = max(min(draw_prob, 1), 0.05)

        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        fair_home_odds = 1 / home_win_prob if home_win_prob > 0 else 100
        fair_away_odds = 1 / away_win_prob if away_win_prob > 0 else 100
        fair_draw_odds = 1 / draw_prob if draw_prob > 0 else 100

        kelly_home = kelly_criterion(fair_home_odds, values['halftime_home_odds'])
        kelly_away = kelly_criterion(fair_away_odds, values['halftime_away_odds'])
        kelly_draw = kelly_criterion(fair_draw_odds, values['halftime_draw_odds'])

        fair_odds_text = f"Fair Odds:\nHome: {fair_home_odds:.2f} vs {values['halftime_home_odds']:.2f}, Stake: {kelly_home:.2f}\n" \
                         f"Away: {fair_away_odds:.2f} vs {values['halftime_away_odds']:.2f}, Stake: {kelly_away:.2f}\n" \
                         f"Draw: {fair_draw_odds:.2f} vs {values['halftime_draw_odds']:.2f}, Stake: {kelly_draw:.2f}"

        fair_odds_label.config(text=fair_odds_text)
    except ValueError as e:
        print("Error:", e)  # Debugging print statement
        fair_odds_label.config(text="Error: Enter valid numbers")
    except KeyError as e:
        print("Missing key:", e)  # Debugging print statement
        fair_odds_label.config(text=f"Error: Missing key {e}")

root = tk.Tk()
root.title("Football Betting Model")
root.geometry("400x1000")

labels = ["Pre-Match Home Odds", "Pre-Match Away Odds", "Pre-Match Draw Odds", "Halftime Home Odds", "Halftime Away Odds", "Halftime Draw Odds", "Avg Home Goals Scored", "Avg Home Goals Conceded", "Avg Away Goals Scored", "Avg Away Goals Conceded", "Home Possession (%)", "Away Possession (%)", "Home Shots on Target", "Away Shots on Target", "Home Expected Goals", "Away Expected Goals", "Home Corners", "Away Corners", "Home Yellow Cards", "Away Yellow Cards", "Home Red Cards", "Away Red Cards", "Home Injuries", "Away Injuries", "Current Score"]

entries = {}
for label in labels:
    frame = ttk.Frame(root)
    frame.pack(pady=2)
    ttk.Label(frame, text=label).pack(side=tk.LEFT)
    entry = ttk.Entry(frame)
    entry.pack(side=tk.RIGHT)
    entries[label.lower().replace(' ', '_').replace('-', '_')] = entry  # Ensure consistency in key names

calculate_button = ttk.Button(root, text="Calculate Fair Odds", command=calculate_fair_odds)
calculate_button.pack(pady=5)

fair_odds_label = ttk.Label(root, text="Fair Odds: ")
fair_odds_label.pack()

root.mainloop()
