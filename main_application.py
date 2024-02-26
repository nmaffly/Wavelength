# main_application.py
from data_visualization import create_graph_json  # Ensure the correct function name is imported

# Your median values and attributes
median_values = [50, 75, 60, 85, 40, 70, 55, 65, 90]  # Example median values
attributes = ['Popularity', 'Tempo', 'Loudness', 'Acousticness', 'Danceability', 'Valence', 'Energy', 'Speechiness', 'Variance']  # Example attributes

# Create the graph JSON
graph_json = create_graph_json(median_values, attributes)
