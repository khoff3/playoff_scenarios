
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import itertools

# Define your standings data, matchups, and status mapping here
# Convert standings data to a DataFrame
standings_data = [
    ["Hydro Hitsquad", "9-4-0", 1457.12, "sweatmasterdelux", "Playoffs (Bye)"],
    ["Bijan De Replay", "8-5-0", 1293.66, "nobodypickjulio", "Playoffs (Bye)"],
    ["Life of Brian", "7-6-0", 1458.88, "FunGuy95", "Playoffs"],
    ["Ekelers? I Hardly Know Her", "7-6-0", 1404.96, "benjyam125", "Playoffs"],
    ["The Autoberts", "7-6-0", 1330.60, "JimDurango", "Playoffs"],
    ["Attila Ja Han", "7-6-0", 1288.06, "Zuce", "Playoffs"],
    ["I'm Joshin', I'm Joshin'!", "7-6-0", 1233.78, "rafaelbung", "Mediocre Bowl"],
    ["Team VoodooFerrari", "7-6-0", 1173.4, "VoodooFerrari", "Mediocre Bowl"],
    ["Big Tua-na", "6-7-0", 1342.20, "teamteza", "The Fisto"],
    ["Here Comes the Sun God", "5-8-0", 1301.86, "RufusAngelo", "The Fisto"],
    ["Fundmntls of Fields Ecology", "5-8-0", 1076.88, "mangycat", "The Fisto"],
    ["Sharpest in the Shaheed", "3-10-0", 1057.76, "ryan carroll09", "The Fisto"]
]

standings_df = pd.DataFrame(standings_data, columns=['Team', 'Record', 'Points', 'Owner', 'Status'])

# Define the matchups for the final game
matchups = [
    ('Here Comes the Sun God', 'Fundmntls of Fields Ecology'),
    ('The Autoberts', 'Ekelers? I Hardly Know Her'),
    ('Sharpest in the Shaheed', 'Life of Brian'),
    ('Big Tua-na', 'Attila Ja Han'),
    ('Hydro Hitsquad', 'Team VoodooFerrari'),
    ("I'm Joshin', I'm Joshin'!", 'Bijan De Replay')
]

# Define a mapping from status to numerical values
status_mapping = {'Playoffs (Bye)': 3, 'Playoffs': 2, 'Mediocre Bowl': 1, 'The Fisto': 0}

def update_record(record, win):
    wins, losses, ties = map(int, record.split('-'))
    return f"{wins+win}-{losses+int(not win)}-{ties}"
def simulate_outcomes(matchups, standings_df):
    outcomes = list(itertools.product([0, 1], repeat=len(matchups)))
    outcome_results = []

    for sim_number, outcome in enumerate(outcomes, start=1):
        temp_df = standings_df.copy()
        for i, result in enumerate(outcome):
            winner, loser = matchups[i][result], matchups[i][1 - result]
            temp_df.loc[temp_df['Team'] == winner, 'Record'] = update_record(temp_df.loc[temp_df['Team'] == winner, 'Record'].iloc[0], win=True)
            temp_df.loc[temp_df['Team'] == loser, 'Record'] = update_record(temp_df.loc[temp_df['Team'] == loser, 'Record'].iloc[0], win=False)

        # Split 'Record' into 'Wins', 'Losses', 'Ties'
        temp_df[['Wins', 'Losses', 'Ties']] = temp_df['Record'].str.split('-', expand=True).astype(int)
        # Sort by Wins first, then Points
        sorted_df = temp_df.sort_values(by=['Wins', 'Points', 'Team'], ascending=[False, False, True])

        # Assign new statuses
        sorted_df['New Status'] = None  # Initialize with None
        sorted_df.iloc[0:2, sorted_df.columns.get_loc('New Status')] = 'Playoffs (Bye)'
        sorted_df.iloc[2:6, sorted_df.columns.get_loc('New Status')] = 'Playoffs'
        sorted_df.iloc[6:8, sorted_df.columns.get_loc('New Status')] = 'Mediocre Bowl'
        sorted_df['New Status'].fillna('The Fisto', inplace=True)  # Assign 'The Fisto' to all remaining teams

        # Check if more than two teams have 'Playoffs (Bye)'
        byes = sorted_df['New Status'].value_counts().get('Playoffs (Bye)', 0)
        if byes > 2:
            print(f"Error in Simulation {sim_number}: More than two teams have 'Playoffs (Bye)'")
            print(sorted_df[['Team', 'Record', 'Points', 'Wins', 'New Status']])
            print()

        outcome_dict = sorted_df.set_index('Team')['New Status'].to_dict()
        outcome_results.append(outcome_dict)

    return outcomes, outcome_results


# Now we simulate the outcomes
outcomes, outcome_results = simulate_outcomes(matchups, standings_df)

# Print details of first few simulations
for i, outcome in enumerate(outcome_results[:5], start=1):
    print(f"Simulation {i}:")
    for team, status in outcome.items():
        print(f" - {team}: {status}")
    print()

# Convert simulation outcomes to numerical values
numerical_outcomes_dicts = []
for outcome in outcome_results:
    numerical_outcome_dict = {team: status_mapping[status] for team, status in outcome.items()}
    numerical_outcomes_dicts.append(numerical_outcome_dict)

# Now convert this list of dictionaries to a DataFrame
simulation_df = pd.DataFrame(numerical_outcomes_dicts)

# Transpose the DataFrame for the heatmap
heatmap_data = simulation_df.T  # Transpose: now rows are teams, columns are simulations

# Create a color map for the heatmap
color_map = ListedColormap(['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4'])
# Define a DataFrame to hold the standings order
standings_order_df = pd.DataFrame(standings_data, columns=['Team', 'Record', 'Points', 'Owner', 'Status'])

# Sort the heatmap data to match the order of teams in the standings
heatmap_data = heatmap_data.reindex(standings_order_df['Team'].values)

# Now when you plot the heatmap, the y-axis will reflect the standings order
plt.figure(figsize=(20, 10))
sns.heatmap(heatmap_data, cmap=color_map, cbar=False, annot=False)

# Add the legend and labels as before
status_labels = ['The Fisto', 'Mediocre Bowl', 'Playoffs', 'Playoffs (Bye)']
colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4']
patches = [plt.Rectangle((0,0),1,1, color=color, label=label) for color, label in zip(colors, status_labels)]
plt.legend(handles=patches, loc='upper left', bbox_to_anchor=(1, 1))
plt.title('Playoff Scenarios Based on Final Game Outcomes')
plt.xlabel('Simulation Outcomes')
plt.ylabel('Teams')
plt.xticks(rotation=45)
# Ensure the y-ticks are horizontal for better readability
plt.yticks(rotation=0)

# Finally, display the plot
plt.show()
