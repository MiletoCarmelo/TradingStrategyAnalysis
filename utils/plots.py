import pandas as pd
import plotly.graph_objects as go
import json


# Define a custom list of 20 colors
custom_colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf', '#f7b733', '#00d2d3',
    '#ff3d00', '#00c853', '#c51162', '#6200ea',
    '#304ffe', '#ffd600', '#ffab40', '#aeea00'
]


def return_empty_plot():
    """
    Create an empty Plotly figure.

    Returns:
    - plot: The created Plotly figure
    """
    return go.Figure()

def create_plot(data, x_column, y_column, color_column, line_type_column, x_title=None, y_title=None, title=None, legend=True, to_json=False):
    """
    Create a line plot with lines colored by a specified column and styled based on line type.

    Parameters:
    - data: DataFrame containing the data to plot
    - x_column: Column name for the x-axis
    - y_column: Column name for the y-axis
    - color_column: Column name for line color differentiation
    - line_type_column: Column name for line type differentiation
    - x_title: Title for the x-axis
    - y_title: Title for the y-axis
    - title: Title for the plot

    Returns:
    - plot: The created Plotly figure
    """

    # Create an empty figure
    plot = go.Figure()

    # Get unique values for color and line type
    unique_colors = data[color_column].unique()

    if y_title is None:
        legend_group = "right side"
    else:
        legend_group = y_title

    for i, color in enumerate(unique_colors): 
        # Filter the data for the current color and line type
        subset = data[(data[color_column] == color)]
        line_style = subset[line_type_column].unique()[0]
        if not subset.empty:
            # Add line traces for the filtered subset
            plot.add_trace(
                go.Scatter(
                    x=subset[x_column],
                    y=subset[y_column],
                    mode='lines',  # Include markers for clarity
                    name=f"{color}",  # This name will appear in the legend
                    line=dict(
                        color=custom_colors[i % len(custom_colors)],  # Set the color
                        dash=line_style, 
                        width=1
                    ),
                    legendgroup=legend_group,  # Assign to a legend group
                    legendgrouptitle_text=legend_group  # Set the group title
                )
            )
    # Update layout with titles and ensure the legend is shown
    plot.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=legend,  # Ensure the legend is displayed
        margin=dict(
            l=30, 
            r=10, 
            t=10, 
            b=10),  # Marges gauche, droite, haut et bas
        paper_bgcolor='rgba(255, 255, 255, 0)',  # Transparent
        plot_bgcolor='rgba(255, 255, 255, 0)',    # Transparent
        xaxis_title_font=dict(size=13),  # X-axis title font size
        yaxis_title_font=dict(size=13),   # Y-axis title font size
        xaxis=dict(
            tickfont=dict(size=13), 
            linecolor='#1b2135',  # Color of x-axis line
            linewidth=0, 
            gridcolor='#1b2135',  # Couleur du cadrillage
            gridwidth=0, 
            zerolinecolor='#1b2135',    # Couleur de la ligne zéro
            zerolinewidth=0),   # Y-axis tick font size
        yaxis=dict(
            tickfont=dict(size=13), 
            linecolor='#1b2135',  # Color of x-axis line
            linewidth=0, 
            gridcolor='#1b2135',  # Couleur du cadrillage
            gridwidth=0, 
            zerolinecolor='#1b2135',    # Couleur de la ligne zéro
            zerolinewidth=0),   # Y-axis tick font size
        legend=dict(
            title=None, 
            font=dict(size=7), 
            bgcolor='rgba(255, 255, 255, 0)',  # Transparent
            orientation="h",  # Horizontal orientation
            yanchor="bottom",  # Anchor to bottom of the plot
            y=-0.2,  # Position below the plot area
            xanchor="center",  # Center horizontally
            x=0.5, # Center position
            traceorder="normal",
        )
    )
    if to_json:
        return plot.to_json()
    else:
        return plot

#
def add_secondary_y(plot, data, x_column, y_column, color_column, line_type_column, y_title=None, legend=True, to_json=False):
    """
    Add a secondary y-axis to a Plotly figure.

    Parameters:
    - plot: The Plotly figure to update
    - data: DataFrame containing the data to plot
    - x_column: Column name for the x-axis
    - y_column: Column name for the y-axis
    - color_column: Column name for line color differentiation
    - line_type_column: Column name for line type differentiation
    - x_title: Title for the x-axis
    - y_title: Title for the y-axis
    - title: Title for the plot

    Returns:
    - plot: The updated Plotly figure
    """

    if y_title is None:
        y_title = y_column

    # Get unique values for color and line type
    unique_colors = data[color_column].unique()

    if y_title is None:
        legend_group = "right side"
    else:
        legend_group = y_title

    for i, color in enumerate(unique_colors): 
        # Filter the data for the current color and line type
        subset = data[(data[color_column] == color)]
        line_style = subset[line_type_column].unique()[0]
        if not subset.empty:
            # Add line traces for the filtered subset
            plot.add_trace(
                go.Scatter(
                    x=subset[x_column],
                    y=subset[y_column],
                    mode='lines',  # Include markers for clarity
                    name=f"{color}",  # This name will appear in the legend
                    line=dict(
                        color=custom_colors[i % len(custom_colors)],  # Set the color
                        dash=line_style, 
                        width=1
                    ),
                    yaxis='y2',  # Use the secondary y-axis
                    legendgroup=legend_group,  # Assign to a legend group
                    legendgrouptitle_text=legend_group  # Set the group title
                )
            )

    # Update legenf to seconds y-axis : 
    plot.update_layout(
        yaxis2=dict(
            title=y_title,
            titlefont=dict(size=13),
            tickfont=dict(size=13),
            overlaying='y',
            side='right'
        ),
        showlegend=legend,  # Ensure the legend is displaye
    )

    if to_json:
        return plot.to_json()
    else:
        return plot




#  Function to add a vertical bar to the plot
def add_vertical_bar(plot, x_value, info, color_id_nb=0, legend=True, to_json=False):
    # Get min and max values of y axis
    y_min = float('inf')
    y_max = float('-inf')
    
    # Loop through plot data to find y min and max
    for trace in plot.data:
        # Filter out None values from y
        y_values = [y for y in trace.y if y is not None]
        
        if y_values:  # Check if the filtered list is not empty
            y_min = min(y_min, min(y_values))
            y_max = max(y_max, max(y_values))

    # set up the color
    color = custom_colors[color_id_nb]

    # Add a dummy trace for the vertical line to show in the legend
    plot.add_trace(
        go.Scatter(
            x=[None],  # Set x to None to avoid drawing a line
            y=[None],  # Set y to None to avoid drawing a line
            mode='lines',
            name=info,  # This name will appear in the legend
            line=dict(color=color, dash="dot"),  # Use the same color
            showlegend=legend  # Make sure the legend entry is shown
        )
    )

    # Add vertical line and annotation
    plot.add_shape(
        type="line",
        x0=x_value, x1=x_value,
        y0=y_min, y1=y_max,  # Adjust the y range based on your data
        line=dict(color=color, width=1, dash="dot"),
    )

    # plot.add_annotation(
    #     x=x_value,
    #     y=y_max,  # Place annotation at the top of the y range
    #     text=info,
    #     showarrow=True,
    #     arrowhead=2,
    #     ax=0,
    #     ay=-40,
    #     font=dict(color=color)  # Use the same color for the annotation
    # )
    if to_json:
        return plot.to_json()
    else:
        return plot