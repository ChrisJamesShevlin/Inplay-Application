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
            "Home Win Odds": tk.DoubleVar(),
            "Away Win Odds": tk.DoubleVar(),
            "Draw Odds": tk.DoubleVar(),
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

    def zero_inflated_poisson_probability(self, lam, k, p_zero=0.15):
        """ Implements a Zero-Inflated Poisson (ZIP) model for better goal predictions """
        if k == 0:
            return p_zero + (1 - p_zero) * exp(-lam)
        else:
            return (1 - p_zero) * (lam**k * exp(-lam)) / factorial(k)

    def time_decay_adjustment(self, lambda_xg, elapsed_minutes):
        """ Adjusts expected goals based on time decay (more goals late in the game) """
        decay_factor = 1 - exp(-elapsed_minutes / 30)  
        return lambda_xg * decay_factor

    def calculate_fair_odds(self):
        # Extract inputs
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

        # Calculate lambda (expected goals) for the remainder of the match
        remaining_minutes = 90 - elapsed_minutes
        lambda_home = in_game_home_xg + (home_xg * remaining_minutes / 90)
        lambda_away = in_game_away_xg + (away_xg * remaining_minutes / 90)

        # Apply possession-based adjustment
        lambda_home *= 1 + ((home_possession - 50) / 100)
        lambda_away *= 1 + ((away_possession - 50) / 100)

        # Apply time decay adjustment
        lambda_home = self.time_decay_adjustment(lambda_home, elapsed_minutes)
        lambda_away = self.time_decay_adjustment(lambda_away, elapsed_minutes)

        # Calculate probabilities for possible match outcomes
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

        # Fair odds calculations
        fair_home_odds = 1 / home_win_probability if home_win_probability != 0 else float('inf')
        fair_away_odds = 1 / away_win_probability if away_win_probability != 0 else float('inf')
        fair_draw_odds = 1 / draw_probability if draw_probability != 0 else float('inf')

        # Dynamic Kelly Criterion (scales based on confidence)
        def dynamic_kelly(edge, confidence=0.5):
            return ((edge * confidence) / 2)

        edge_lay_home = (fair_home_odds - live_home_odds) / fair_home_odds
        stake_lay_home = account_balance * dynamic_kelly(edge_lay_home, 0.75)

        # Display result
        result_text = f"Fair Odds:\nHome: {fair_home_odds:.2f}, Away: {fair_away_odds:.2f}, Draw: {fair_draw_odds:.2f}\n"
        if fair_home_odds > live_home_odds:
            result_text += f"Recommended Lay Bet on Home, Stake: {stake_lay_home:.2f}\n"

        self.result_label.config(text=result_text)

def main():
    root = tk.Tk()
    app = FootballBettingModel(root)
    root.mainloop()

if __name__ == "__main__":
    main()
