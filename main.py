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

    def poisson_probability(self, lam, k):
        return (lam**k * exp(-lam)) / factorial(k)

    def calculate_fair_odds(self):
        # Extract inputs
        home_goals_scored = self.fields["Home Avg Goals Scored"].get()
        home_goals_conceded = self.fields["Home Avg Goals Conceded"].get()
        away_goals_scored = self.fields["Away Avg Goals Scored"].get()
        away_goals_conceded = self.fields["Away Avg Goals Conceded"].get()
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

        # Calculate probabilities for possible match outcomes
        home_win_probability = 0
        away_win_probability = 0
        draw_probability = 0

        for home_goals_remaining in range(0, 6):  # Considering 0 to 5 goals for remaining match
            for away_goals_remaining in range(0, 6):
                home_final_goals = home_goals + home_goals_remaining
                away_final_goals = away_goals + away_goals_remaining

                prob = self.poisson_probability(lambda_home, home_goals_remaining) * self.poisson_probability(lambda_away, away_goals_remaining)

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

        kelly_criterion = lambda p, q, b: (p * (b + 1) - 1) / b

        # Calculate Kelly Criterion for back or lay bet
        margin = 0.05  # Margin for error
        edge_lay_home = (fair_home_odds - live_home_odds) / fair_home_odds
        edge_lay_away = (fair_away_odds - live_away_odds) / fair_away_odds
        edge_lay_draw = (fair_draw_odds - live_draw_odds) / fair_draw_odds

        edge_back_home = (live_home_odds - fair_home_odds) / fair_home_odds
        edge_back_away = (live_away_odds - fair_away_odds) / fair_away_odds
        edge_back_draw = (live_draw_odds - fair_draw_odds) / fair_draw_odds

        kelly_lay_home = kelly_criterion(1 / fair_home_odds, 1 - 1 / fair_home_odds, live_home_odds - 1) * 0.25
        kelly_lay_away = kelly_criterion(1 / fair_away_odds, 1 - 1 / fair_away_odds, live_away_odds - 1) * 0.25
        kelly_lay_draw = kelly_criterion(1 / fair_draw_odds, 1 - 1 / fair_draw_odds, live_draw_odds - 1) * 0.25

        kelly_back_home = kelly_criterion(1 / live_home_odds, 1 - 1 / live_home_odds, fair_home_odds - 1) * 0.25
        kelly_back_away = kelly_criterion(1 / live_away_odds, 1 - 1 / live_away_odds, fair_away_odds - 1) * 0.25
        kelly_back_draw = kelly_criterion(1 / live_draw_odds, 1 - 1 / live_draw_odds, fair_draw_odds - 1) * 0.25

        stake_lay_home = account_balance * kelly_lay_home
        stake_lay_away = account_balance * kelly_lay_away
        stake_lay_draw = account_balance * kelly_lay_draw

        stake_back_home = account_balance * kelly_back_home
        stake_back_away = account_balance * kelly_back_away
        stake_back_draw = account_balance * kelly_back_draw

        # Debugging output to console
        debug_text = f"Debugging Information:\n"
        debug_text += f"Home Goals Scored: {home_goals_scored}\n"
        debug_text += f"Home Goals Conceded: {home_goals_conceded}\n"
        debug_text += f"Away Goals Scored: {away_goals_scored}\n"
        debug_text += f"Away Goals Conceded: {away_goals_conceded}\n"
        debug_text += f"Home Xg: {home_xg}\n"
        debug_text += f"Away Xg: {away_xg}\n"
        debug_text += f"Elapsed Minutes: {elapsed_minutes}\n"
        debug_text += f"Remaining Minutes: {remaining_minutes}\n"
        debug_text += f"In-Game Home Xg: {in_game_home_xg}\n"
        debug_text += f"In-Game Away Xg: {in_game_away_xg}\n"
        debug_text += f"Home Possession: {home_possession}\n"
        debug_text += f"Away Possession: {away_possession}\n"
        debug_text += f"Lambda Home: {lambda_home}\n"
        debug_text += f"Lambda Away: {lambda_away}\n"
        debug_text += f"Home Win Probability: {home_win_probability}\n"
        debug_text += f"Away Win Probability: {away_win_probability}\n"
        debug_text += f"Draw Probability: {draw_probability}\n"
        debug_text += f"Fair Home Odds: {fair_home_odds}\n"
        debug_text += f"Fair Away Odds: {fair_away_odds}\n"
        debug_text += f"Fair Draw Odds: {fair_draw_odds}\n"
        debug_text += f"Edge Lay Home: {edge_lay_home}\n"
        debug_text += f"Edge Lay Away: {edge_lay_away}\n"
        debug_text += f"Edge Lay Draw: {edge_lay_draw}\n"
        debug_text += f"Edge Back Home: {edge_back_home}\n"
        debug_text += f"Edge Back Away: {edge_back_away}\n"
        debug_text += f"Edge Back Draw: {edge_back_draw}\n"
        debug_text += f"Kelly Lay Home: {kelly_lay_home}\n"
        debug_text += f"Kelly Lay Away: {kelly_lay_away}\n"
        debug_text += f"Kelly Lay Draw: {kelly_lay_draw}\n"
        debug_text += f"Kelly Back Home: {kelly_back_home}\n"
        debug_text += f"Kelly Back Away: {kelly_back_away}\n"
        debug_text += f"Kelly Back Draw: {kelly_back_draw}\n"
        debug_text += f"Stake Lay Home: {stake_lay_home}\n"
        debug_text += f"Stake Lay Away: {stake_lay_away}\n"
        debug_text += f"Stake Lay Draw: {stake_lay_draw}\n"
        debug_text += f"Stake Back Home: {stake_back_home}\n"
        debug_text += f"Stake Back Away: {stake_back_away}\n"
        debug_text += f"Stake Back Draw: {stake_back_draw}\n"
        print(debug_text)  # Print debug information to the console

        # Determine the best bet based on the highest edge and fair odds being higher than live odds
        result_text = "No recommended bet."
        if fair_home_odds > live_home_odds * (1 + margin) and live_home_odds <= 6 and edge_lay_home > 0:
            result_text = f"Recommended Lay Bet on Home\nFair Home Odds: {fair_home_odds:.2f}\nLiability: {stake_lay_home:.2f}\n"
        elif fair_away_odds > live_away_odds * (1 + margin) and live_away_odds <= 6 and edge_lay_away > 0:
            result_text = f"Recommended Lay Bet on Away\nFair Away Odds: {fair_away_odds:.2f}\nLiability: {stake_lay_away:.2f}\n"
        elif fair_draw_odds > live_draw_odds * (1 + margin) and live_draw_odds <= 6 and edge_lay_draw > 0:
            result_text = f"Recommended Lay Bet on Draw\nFair Draw Odds: {fair_draw_odds:.2f}\nLiability: {stake_lay_draw:.2f}\n"
        elif live_home_odds > fair_home_odds * (1 + margin) and edge_back_home > 0:
            result_text = f"Recommended Back Bet on Home\nFair Home Odds: {fair_home_odds:.2f}\nStake: {stake_back_home:.2f}\n"
        elif live_away_odds > fair_away_odds * (1 + margin) and edge_back_away > 0:
            result_text = f"Recommended Back Bet on Away\nFair Away Odds: {fair_away_odds:.2f}\nStake: {stake_back_away:.2f}\n"
        elif live_draw_odds > fair_draw_odds * (1 + margin) and edge_back_draw > 0:
            result_text = f"Recommended Back Bet on Draw\nFair Draw Odds: {fair_draw_odds:.2f}\nStake: {stake_back_draw:.2f}\n"

        # Output all fair odds
        result_text += f"\nAll Fair Odds:\nHome: {fair_home_odds:.2f}\nAway: {fair_away_odds:.2f}\nDraw: {fair_draw_odds:.2f}"

        self.result_label.config(text=result_text)

def main():
    root = tk.Tk()
    app = FootballBettingModel(root)
    root.mainloop()

if __name__ == "__main__":
    main()
