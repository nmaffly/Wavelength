# data_visualization.py
import plotly.graph_objects as go

def create_graph_json(median_values, attributes):
    # Create the figure
    fig = go.Figure()

    # Add the line with a different color for each marker
    fig.add_trace(go.Scatter(x=attributes, y=median_values, mode='lines+markers',
                             marker=dict(color=['red', 'green', 'blue', 'orange', 'purple', 'yellow', 'cyan', 'magenta', 'lime'], size=10),
                             line=dict(color='lightblue', width=3)))

    # Customize the layout with color illumination effect
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent area around the graph
        margin=dict(l=20, r=20, t=20, b=20),  # Reduce margins to minimize the white box effect
        xaxis=dict(showgrid=False, title='Attributes', tickangle=-45),
        yaxis=dict(showgrid=False, zeroline=False, autorange=True, title='%'),
        font=dict(color='white'),  # Change font color to white for better contrast
        xaxis_showspikes=True,  # Show spike lines for x-axis (can give an illuminated effect)
        yaxis_showspikes=True,  # Show spike lines for y-axis
    )

    # Remove the white box by setting the layout's width and height
    fig.update_layout(width=700, height=500, background='rgba(0,0,0,0)')

    # Convert the figure to JSON
    graph_json = fig.to_json()
    return graph_json
