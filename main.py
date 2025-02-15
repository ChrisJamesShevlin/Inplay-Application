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
        pre_match_home_odds = float(entry_home_odds.get())
        pre_match_away_odds = float(entry_away_odds.get())
        pre_match_draw_odds = float(entry_draw_odds.get())

        halftime_home_odds = float(entry_halftime_home_odds.get())
        halftime_away_odds = float(entry_halftime_away_odds.get())
        halftime_draw_odds = float(entry_halftime_draw_odds.get())

        avg_home_goals_scored = float(entry_avg_home_goals_scored.get())
        avg_home_goals_conceded = float(entry_avg_home_goals_conceded.get())
        avg_away_goals_scored = float(entry_avg_away_goals_scored.get())
        avg_away_goals_conceded = float(entry_avg_away_goals_conceded.get())
        
        home_possession = float(entry_home_possession.get())
        away_possession = float(entry_away_possession.get())
        home_shots_on_target = float(entry_home_shots.get())
        away_shots_on_target = float(entry_away_shots.get())
        home_expected_goals = float(entry_home_xg.get())
        away_expected_goals = float(entry_away_xg.get())
        home_corners = float(entry_home_corners.get())
        away_corners = float(entry_away_corners.get())
        home_yellow_cards = float(entry_home_yellow.get())
        away_yellow_cards = float(entry_away_yellow.get())
        home_red_cards = float(entry_home_red.get())
        away_red_cards = float(entry_away_red.get())
        home_injuries = float(entry_home_injuries.get())
        away_injuries = float(entry_away_injuries.get())
        current_score = entry_score.get()

        # Adjust attack/defense strength
        home_attack_strength = avg_home_goals_scored / avg_away_goals_conceded
        away_attack_strength = avg_away_goals_scored / avg_home_goals_conceded

        # Adjust for in-play factors (Simple weighting system)
        weight = 0.2
        attack_boost_home = (home_shots_on_target + 0.5 * home_expected_goals + 0.3 * home_corners) * weight
        attack_boost_away = (away_shots_on_target + 0.5 * away_expected_goals + 0.3 * away_corners) * weight
        defense_penalty_home = (home_yellow_cards * 0.1 + home_red_cards * 0.3 + home_injuries * 0.2) * weight
        defense_penalty_away = (away_yellow_cards * 0.1 + away_red_cards * 0.3 + away_injuries * 0.2) * weight

        adjusted_home_strength = home_attack_strength + attack_boost_home - defense_penalty_home
        adjusted_away_strength = away_attack_strength + attack_boost_away - defense_penalty_away

        halftime_home_goals = adjusted_home_strength * 0.5
        halftime_away_goals = adjusted_away_strength * 0.5

        home_win_prob = 1 - zero_inflated_poisson(halftime_home_goals)
        away_win_prob = 1 - zero_inflated_poisson(halftime_away_goals)

        # Proper Draw Probability Calculation
        draw_prob = sum(poisson_pmf(i, halftime_home_goals) * poisson_pmf(i, halftime_away_goals) for i in range(5))
        draw_prob = max(min(draw_prob, 1), 0.01)  # Keep within valid bounds

        # Normalize all probabilities
        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        away_win_prob /= total_prob
        draw_prob /= total_prob

        # Compute Fair Odds
        fair_home_odds = 1 / home_win_prob if home_win_prob > 0 else 100
        fair_away_odds = 1 / away_win_prob if away_win_prob > 0 else 100
        fair_draw_odds = 1 / draw_prob if draw_prob > 0 else 100  # Fix draw odds issue

        kelly_home = kelly_criterion(fair_home_odds, halftime_home_odds)
        kelly_away = kelly_criterion(fair_away_odds, halftime_away_odds)
        kelly_draw = kelly_criterion(fair_draw_odds, halftime_draw_odds)

        fair_odds_text = f"Fair Odds:\nHome: {fair_home_odds:.2f} vs {halftime_home_odds:.2f}, Stake: {kelly_home:.2f}\n" \
                         f"Away: {fair_away_odds:.2f} vs {halftime_away_odds:.2f}, Stake: {kelly_away:.2f}\n" \
                         f"Draw: {fair_draw_odds:.2f} vs {halftime_draw_odds:.2f}, Stake: {kelly_draw:.2f}"

        fair_odds_label.config(text=fair_odds_text)
    except ValueError:
        fair_odds_label.config(text="Error: Enter valid numbers")

# Tkinter GUI setup
root = tk.Tk()
root.title("Football Betting Model")
root.geometry("400x1000")

labels = ["Pre-Match Home Odds", "Pre-Match Away Odds", "Pre-Match Draw Odds", "Halftime Home Odds", "Halftime Away Odds", "Halftime Draw Odds", "Avg Home Goals Scored", "Avg Home Goals Conceded", "Avg Away Goals Scored", "Avg Away Goals Conceded", "Home Possession (%)", "Away Possession (%)", "Home Shots on Target", "Away Shots on Target", "Home Expected Goals", "Away Expected Goals", "Home Corners", "Away Corners", "Home Yellow Cards", "Away Yellow Cards", "Home Red Cards", "Away Red Cards", "Home Injuries", "Away Injuries", "Current Score"]

entries = []
for label in labels:
    frame = ttk.Frame(root)
    frame.pack(pady=2)
    ttk.Label(frame, text=label).pack(side=tk.LEFT)
    entry = ttk.Entry(frame)
    entry.pack(side=tk.RIGHT)
    entries.append(entry)

(entry_home_odds, entry_away_odds, entry_draw_odds, entry_halftime_home_odds, entry_halftime_away_odds, entry_halftime_draw_odds, entry_avg_home_goals_scored, entry_avg_home_goals_conceded, entry_avg_away_goals_scored, entry_avg_away_goals_conceded, entry_home_possession, entry_away_possession, entry_home_shots, entry_away_shots, entry_home_xg, entry_away_xg, entry_home_corners, entry_away_corners, entry_home_yellow, entry_away_yellow, entry_home_red, entry_away_red, entry_home_injuries, entry_away_injuries, entry_score) = entries

calculate_button = ttk.Button(root, text="Calculate Fair Odds", command=calculate_fair_odds)
calculate_button.pack(pady=5)

fair_odds_label = ttk.Label(root, text="Fair Odds: ")
fair_odds_label.pack()

root.mainloop()
