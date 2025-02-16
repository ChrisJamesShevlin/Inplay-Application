import tkinter as tk
from tkinter import ttk
import math

# Tkinter GUI setup
root = tk.Tk()
root.title("Football Probability Calculator")
root.geometry("700x600")

# User input fields
frame_input = ttk.Frame(root)
frame_input.pack(pady=10)

ttk.Label(frame_input, text="Match Time (minutes):").grid(row=0, column=0)
time_var = tk.IntVar()
time_entry = ttk.Entry(frame_input, textvariable=time_var)
time_entry.grid(row=0, column=1)

ttk.Label(frame_input, text="Home Goals:").grid(row=1, column=0)
home_goals_var = tk.IntVar()
home_goals_entry = ttk.Entry(frame_input, textvariable=home_goals_var)
home_goals_entry.grid(row=1, column=1)

ttk.Label(frame_input, text="Away Goals:").grid(row=2, column=0)
away_goals_var = tk.IntVar()
away_goals_entry = ttk.Entry(frame_input, textvariable=away_goals_var)
away_goals_entry.grid(row=2, column=1)

ttk.Label(frame_input, text="Pre-match Home Odds:").grid(row=3, column=0)
home_odds_var = tk.DoubleVar()
home_odds_entry = ttk.Entry(frame_input, textvariable=home_odds_var)
home_odds_entry.grid(row=3, column=1)

ttk.Label(frame_input, text="Pre-match Away Odds:").grid(row=4, column=0)
away_odds_var = tk.DoubleVar()
away_odds_entry = ttk.Entry(frame_input, textvariable=away_odds_var)
away_odds_entry.grid(row=4, column=1)

ttk.Label(frame_input, text="Pre-match Draw Odds:").grid(row=5, column=0)
draw_odds_var = tk.DoubleVar()
draw_odds_entry = ttk.Entry(frame_input, textvariable=draw_odds_var)
draw_odds_entry.grid(row=5, column=1)

ttk.Label(frame_input, text="Current Home xG:").grid(row=6, column=0)
home_xg_var = tk.DoubleVar()
home_xg_entry = ttk.Entry(frame_input, textvariable=home_xg_var)
home_xg_entry.grid(row=6, column=1)

ttk.Label(frame_input, text="Current Away xG:").grid(row=7, column=0)
away_xg_var = tk.DoubleVar()
away_xg_entry = ttk.Entry(frame_input, textvariable=away_xg_var)
away_xg_entry.grid(row=7, column=1)

def poisson_probability(lam, goals):
    return (math.exp(-lam) * (lam ** goals)) / math.factorial(goals)

def calculate_probability():
    time = time_var.get()
    remaining_time = 90 - time
    home_goals = home_goals_var.get()
    away_goals = away_goals_var.get()
    home_xg = home_xg_var.get()
    away_xg = away_xg_var.get()
    
    # Adjust xG for remaining time proportionally
    remaining_home_xg = (home_xg / time) * remaining_time
    remaining_away_xg = (away_xg / time) * remaining_time
    
    # Calculate probabilities of scoring more goals
    home_prob_future = 1 - sum(poisson_probability(remaining_home_xg, i) for i in range(1))
    away_prob_future = 1 - sum(poisson_probability(remaining_away_xg, i) for i in range(1))
    
    # Adjust probabilities for current score
    if home_goals > away_goals:
        home_prob = 0.7 + home_prob_future * 0.3
        away_prob = away_prob_future * 0.3
        draw_prob = 1 - (home_prob + away_prob)
    elif home_goals < away_goals:
        away_prob = 0.7 + away_prob_future * 0.3
        home_prob = home_prob_future * 0.3
        draw_prob = 1 - (home_prob + away_prob)
    else:
        home_prob = home_prob_future * 0.5
        away_prob = away_prob_future * 0.5
        draw_prob = 1 - (home_prob + away_prob)
    
    home_prob *= 100
    away_prob *= 100
    draw_prob *= 100
    
    result_label.config(text=f"Home Win: {home_prob:.2f}% | Draw: {draw_prob:.2f}% | Away Win: {away_prob:.2f}%")

# Calculate button
calc_button = ttk.Button(frame_input, text="Calculate Probability", command=calculate_probability)
calc_button.grid(row=8, columnspan=2, pady=10)

# Result label
result_label = ttk.Label(root, text="", font=("Arial", 12))
result_label.pack()

root.mainloop()
