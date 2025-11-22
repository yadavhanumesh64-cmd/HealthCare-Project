# T20 World Cup Data Analysis Project
# -----------------------------------
# Requirements:
# pip install pandas matplotlib seaborn streamlit

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set(style="darkgrid")

# ---------------------------
# Load datasets
# ---------------------------
def load_data():
    if not os.path.exists("matches.csv"):
        raise FileNotFoundError("Error: matches.csv not found in working directory")

    matches = pd.read_csv("matches.csv")

    if os.path.exists("deliveries.csv"):
        deliveries = pd.read_csv("deliveries.csv")
    else:
        deliveries = None
        print("⚠ deliveries.csv not found. Ball-by-ball analysis will be skipped.")

    return matches, deliveries


# ---------------------------
# Exploratory Data Analysis
# ---------------------------
def analyze_matches(matches):
    os.makedirs("output_plots", exist_ok=True)

    # 1. Most winning teams
    plt.figure(figsize=(10,6))
    matches['winner'].value_counts().plot(kind='bar', color='skyblue')
    plt.title("Most Winning Teams")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output_plots/winning_teams.png")
    plt.close()

    # 2. Toss decision analysis
    plt.figure(figsize=(6,6))
    matches['toss_decision'].value_counts().plot(kind='pie', autopct='%1.1f%%')
    plt.title("Toss Decision Distribution")
    plt.ylabel("")
    plt.savefig("output_plots/toss_decision.png")
    plt.close()

    # 3. Toss vs Match outcome
    toss_match = (matches['toss_winner'] == matches['winner']).value_counts()
    plt.figure(figsize=(6,6))
    toss_match.plot(kind='pie', autopct='%1.1f%%', labels=['Won Toss & Match', 'Lost Match'])
    plt.title("Impact of Toss on Match Outcome")
    plt.ylabel("")
    plt.savefig("output_plots/toss_vs_match.png")
    plt.close()

    # 4. Player of the match awards
    plt.figure(figsize=(10,6))
    matches['player_of_match'].value_counts().head(10).plot(kind='bar', color='orange')
    plt.title("Top 10 Players with Most 'Player of the Match' Awards")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output_plots/top_players.png")
    plt.close()

    print("✅ Match-level analysis plots saved in output_plots/")


# ---------------------------
# Ball-by-ball analysis
# ---------------------------
def analyze_deliveries(deliveries):
    if deliveries is None:
        return

    os.makedirs("output_plots", exist_ok=True)

    # 1. Boundary distribution
    boundaries = deliveries[deliveries['batsman_runs'].isin([4,6])]
    plt.figure(figsize=(6,6))
    boundaries['batsman_runs'].value_counts().plot(kind='pie', autopct='%1.1f%%', labels=['Four', 'Six'])
    plt.title("Boundary Distribution (4s vs 6s)")
    plt.ylabel("")
    plt.savefig("output_plots/boundaries.png")
    plt.close()

    # 2. Average runs per over
    runs_per_over = deliveries.groupby('over')['total_runs'].mean()
    plt.figure(figsize=(10,6))
    runs_per_over.plot(marker='o')
    plt.title("Average Runs per Over")
    plt.xlabel("Over")
    plt.ylabel("Avg Runs")
    plt.savefig("output_plots/runs_per_over.png")
    plt.close()

    print("✅ Ball-by-ball analysis plots saved in output_plots/")


# ---------------------------
# Streamlit Dashboard
# ---------------------------
def create_streamlit_app():
    import streamlit as st

    st.title("🏏 T20 World Cup Data Analysis")
    matches, deliveries = load_data()

    st.subheader("Dataset Preview")
    st.dataframe(matches.head())

    st.subheader("Top Winning Teams")
    win_counts = matches['winner'].value_counts().reset_index()
    win_counts.columns = ["Team", "Wins"]
    st.bar_chart(win_counts.set_index("Team"))

    st.subheader("Toss Decision")
    toss_counts = matches['toss_decision'].value_counts()
    st.write(toss_counts)

    if deliveries is not None:
        st.subheader("Average Runs per Over")
        runs_per_over = deliveries.groupby('over')['total_runs'].mean()
        st.line_chart(runs_per_over)


# ---------------------------
# Main function
# ---------------------------
def main():
    matches, deliveries = load_data()
    analyze_matches(matches)
    analyze_deliveries(deliveries)


if __name__ == "__main__":
    main()
