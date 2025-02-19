import tkinter as tk
from tkinter import ttk
from math import exp, factorial

class FootballBettingModel:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Betting Model")
        self.create_widgets()

    def create_widgets(self):
        self.fields = {
            "Home Avg Goals Scored": tk.DoubleVar(),
            "Home Avg Goals Conceded": tk.DoubleVar(),
            "Away Avg Goals Scored": tk.DoubleVar(),
            "Away Avg Goals Conceded": tk.DoubleVar(),
            "Home Xg": tk.DoubleVar(),
            "Away Xg": tk.DoubleVar(),
            "Over 2.5 Goals Odds": tk.DoubleVar(),
            "Elapsed Minutes": tk.DoubleVar(),
            "Home Goals": tk.IntVar(),
            "Away Goals": tk.IntVar(),
            "In-Game Home Xg": tk.DoubleVar(),
            "In-Game Away Xg": tk.DoubleVar(),
            "Home Possession %": tk.DoubleVar(),
            "Away Possession %": tk.DoubleVar(),
            "Account Balance": tk.DoubleVar(),
            "Live Home Odds": tk.DoubleVar(),
            "Live Away Odds": tk.DoubleVar(),
            "Live Draw Odds": tk.DoubleVar()
        }

        row = 0
        for field, var in self.fields.items():
            label = ttk.Label(self.root, text=field)
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(self.root, textvariable=var)
            entry.grid(row=row, column=1, padx=5, pady=5)
            row += 1

        calculate_button = ttk.Button(self.root, text="Calculate", command=self.calculate_fair_odds)
        calculate_button.grid(row=row, column=0, columnspan=2, pady=10)
        
        reset_button = ttk.Button(self.root, text="Reset Fields", command=self.reset_fields)
        reset_button.grid(row=row+1, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self.root, text="")
        self.result_label.grid(row=row+2, column=0, columnspan=2, pady=10)

    def reset_fields(self):
        for var in self.fields.values():
            if isinstance(var, tk.DoubleVar):
                var.set(0.0)
            elif isinstance(var, tk.IntVar):
                var.set(0)

    def zero_inflated_poisson_probability(self, lam, k, p_zero=0.10):
        """Zero-inflated Poisson for realistic goal probabilities."""
        if k == 0:
            return p_zero + (1 - p_zero) * exp(-lam)
        return (1 - p_zero) * ((lam ** k) * exp(-lam)) / factorial(k)

    def time_decay_adjustment(self, lambda_xg, elapsed_minutes):
        """Scales expected goals based on time decay, avoiding exponential overcorrection."""
        decay_factor = 1 - (elapsed_minutes / 90)
        return lambda_xg * max(0.3, decay_factor)  # Ensures reasonable lower limit

    def dynamic_kelly(self, edge, odds):
        """Kelly staking strategy adjusted dynamically to avoid excessive staking."""
        if odds > 12.0:
            return 0  # Skip high-odds bets
        elif odds <= 2.5:
            fraction = 1/10  # Conservative for lower odds
        elif odds <= 6.0:
            fraction = 1/20
        else:
            fraction = 1/30

        return max(0, fraction * (edge / (odds - 1))) if odds > 1 else 0

    def calculate_fair_odds(self):
        home_xg = self.fields["Home Xg"].get()
        away_xg = self.fields["Away Xg"].get()
        elapsed_minutes = self.fields["Elapsed Minutes"].get()
        home_goals = self.fields["Home Goals"].get()
        away_goals = self.fields["Away Goals"].get()
        in_game_home_xg = self.fields["In-Game Home Xg"].get()
        in_game_away_xg = self.fields["In-Game Away Xg"].get()
        home_possession = self.fields["Home Possession %"].get()
        away_possession = self.fields["Away Possession %"].get()
        account_balance = self.fields["Account Balance"].get()
        live_home_odds = self.fields["Live Home Odds"].get()
        live_away_odds = self.fields["Live Away Odds"].get()
        live_draw_odds = self.fields["Live Draw Odds"].get()
        over_2_5_goals_odds = self.fields["Over 2.5 Goals Odds"].get()
        
        # Adjusted goal expectations
        home_avg_goals_scored = self.fields["Home Avg Goals Scored"].get()
        home_avg_goals_conceded = self.fields["Home Avg Goals Conceded"].get()
        away_avg_goals_scored = self.fields["Away Avg Goals Scored"].get()
        away_avg_goals_conceded = self.fields["Away Avg Goals Conceded"].get()

        remaining_minutes = 90 - elapsed_minutes
        lambda_home = self.time_decay_adjustment(in_game_home_xg + (home_xg * remaining_minutes / 90), elapsed_minutes)
        lambda_away = self.time_decay_adjustment(in_game_away_xg + (away_xg * remaining_minutes / 90), elapsed_minutes)
        
        # Improved weight-based goal adjustment
        lambda_home = (lambda_home * 0.6) + ((home_avg_goals_scored / away_avg_goals_conceded) * 0.4)
        lambda_away = (lambda_away * 0.6) + ((away_avg_goals_scored / home_avg_goals_conceded) * 0.4)

        lambda_home *= 1 + ((home_possession - 50) / 200)
        lambda_away *= 1 + ((away_possession - 50) / 200)

        home_win_probability = 0
        away_win_probability = 0
        draw_probability = 0

        for home_goals_remaining in range(6):
            for away_goals_remaining in range(6):
                home_final_goals = home_goals + home_goals_remaining
                away_final_goals = away_goals + away_goals_remaining

                prob = self.zero_inflated_poisson_probability(lambda_home, home_goals_remaining) * \
                       self.zero_inflated_poisson_probability(lambda_away, away_goals_remaining)

                if home_final_goals > away_final_goals:
                    home_win_probability += prob
                elif home_final_goals < away_final_goals:
                    away_win_probability += prob
                else:
                    draw_probability += prob

        total_prob = home_win_probability + away_win_probability + draw_probability
        home_win_probability /= total_prob
        away_win_probability /= total_prob
        draw_probability /= total_prob

        fair_home_odds = 1 / home_win_probability
        fair_away_odds = 1 / away_win_probability
        fair_draw_odds = 1 / draw_probability

        best_lay_recommendation = "No value lay bet found."
        for outcome, fair_odds, live_odds in [("Home", fair_home_odds, live_home_odds), 
                                              ("Away", fair_away_odds, live_away_odds), 
                                              ("Draw", fair_draw_odds, live_draw_odds)]:
            if live_odds < fair_odds and live_odds <= 12:
                edge = (fair_odds - live_odds) / fair_odds
                stake = account_balance * self.dynamic_kelly(edge, live_odds)
                liability = stake * (live_odds - 1)
                best_lay_recommendation = f"Lay {outcome} at {live_odds:.2f}, Stake: {stake:.2f}, Liability: {liability:.2f}"

        result_text = f"Fair Odds:\nHome: {fair_home_odds:.2f}, Away: {fair_away_odds:.2f}, Draw: {fair_draw_odds:.2f}\n{best_lay_recommendation}"
        self.result_label.config(text=result_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = FootballBettingModel(root)
    root.mainloop()
