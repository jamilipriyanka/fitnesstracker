import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def plot_workout_history(workout_history, metric="calories_burned", days=None):
    """
    Create a line plot of workout history for a specific metric.
    
    Args:
        workout_history: List of workout dictionaries
        metric: The metric to plot (calories_burned, duration, heart_rate)
        days: Number of days to include, or None for all history
    
    Returns:
        Plotly figure object
    """
    if not workout_history:
        return go.Figure()
    
    # Sort workouts by date
    sorted_workouts = sorted(workout_history, key=lambda x: x["date"])
    
    if days:
        # Filter to last N days
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        sorted_workouts = [w for w in sorted_workouts if w["date"] >= cutoff_date]
    
    if not sorted_workouts:
        return go.Figure()
    
    # Extract dates and metric values
    dates = [w["date"] for w in sorted_workouts]
    values = [w[metric] for w in sorted_workouts]
    
    # Create dataframe for plotly
    df = pd.DataFrame({
        "date": dates,
        "value": values,
        "type": [w.get("workout_type", "Unknown") for w in sorted_workouts]
    })
    
    # Map metric name to display name
    metric_names = {
        "calories": "Calories Burned",
        "duration": "Duration (minutes)",
        "heart_rate": "Heart Rate (bpm)",
        "body_temp": "Body Temperature (°C)"
    }
    
    metric_display = metric_names.get(metric, metric.capitalize())
    
    # Create figure
    fig = px.line(
        df, 
        x="date", 
        y="value", 
        title=f"{metric_display} Over Time",
        markers=True,
        color_discrete_sequence=["#985E6D"]
    )
    
    # Add hover data
    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>" + metric_display + ":</b> %{y}<extra></extra>"
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric_display,
        template="plotly_dark"
    )
    
    return fig

def plot_goal_progress(goals):
    """
    Create a progress chart for active goals.
    
    Args:
        goals: List of goal dictionaries
    
    Returns:
        Plotly figure object
    """
    if not goals:
        return go.Figure()
    
    # Extract goal names and progress percentages
    goal_names = [g["name"] for g in goals]
    progress_pcts = [(g["current"] / g["target"]) * 100 for g in goals]
    remaining_pcts = [100 - p for p in progress_pcts]
    
    # Create figure
    fig = go.Figure()
    
    # Add progress bars
    fig.add_trace(go.Bar(
        y=goal_names,
        x=progress_pcts,
        name="Progress",
        orientation="h",
        marker=dict(color="#985E6D")
    ))
    
    # Add remaining bars
    fig.add_trace(go.Bar(
        y=goal_names,
        x=remaining_pcts,
        name="Remaining",
        orientation="h",
        marker=dict(color="#494E6B")
    ))
    
    # Update layout
    fig.update_layout(
        title="Goal Progress",
        barmode="stack",
        xaxis_title="Progress (%)",
        yaxis_title="Goal",
        template="plotly_dark",
        showlegend=True
    )
    
    # Add goal completion percentages as text
    for i, (name, pct) in enumerate(zip(goal_names, progress_pcts)):
        fig.add_annotation(
            x=max(pct - 5, 0),
            y=i,
            text=f"{pct:.1f}%",
            showarrow=False,
            font=dict(color="white")
        )
    
    return fig

def create_comparison_chart(your_data, others_data, metric="calories_burned"):
    """
    Create a chart comparing your data with others.
    
    Args:
        your_data: Your metric value
        others_data: List of others' metric values
        metric: Metric name for display purposes
    
    Returns:
        Plotly figure object
    """
    # Calculate percentile
    percentile = sum(1 for x in others_data if x < your_data) / len(others_data) * 100
    
    # Create histogram
    fig = go.Figure()
    
    # Add histogram of others' data
    fig.add_trace(go.Histogram(
        x=others_data,
        name="Others",
        marker_color="#494E6B"
    ))
    
    # Add vertical line for your data
    fig.add_trace(go.Scatter(
        x=[your_data, your_data],
        y=[0, fig.data[0]['y'].max() if len(fig.data) > 0 and hasattr(fig.data[0], 'y') else 10],
        mode="lines",
        name="Your Value",
        line=dict(color="#985E6D", width=3, dash="solid")
    ))
    
    # Map metric name to display name
    metric_names = {
        "calories": "Calories Burned",
        "duration": "Duration (minutes)",
        "heart_rate": "Heart Rate (bpm)",
        "body_temp": "Body Temperature (°C)"
    }
    
    metric_display = metric_names.get(metric, metric.capitalize())
    
    # Update layout
    fig.update_layout(
        title=f"Your {metric_display} Compared to Others (Percentile: {percentile:.1f}%)",
        xaxis_title=metric_display,
        yaxis_title="Frequency",
        template="plotly_dark"
    )
    
    return fig

def plot_weekly_activity(df):
    """
    Create a heatmap showing weekly workout activity pattern.
    
    Args:
        df: DataFrame with workout data including 'date' column
    
    Returns:
        Plotly figure object
    """
    if df is None or df.empty:
        return go.Figure()
    
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract day of week and hour
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Count workouts by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['day_of_week'].value_counts().reindex(day_order, fill_value=0)
    
    # Create bar chart
    fig = px.bar(
        x=day_counts.index,
        y=day_counts.values,
        labels={'x': 'Day of Week', 'y': 'Number of Workouts'},
        title='Weekly Workout Activity',
        color=day_counts.values,
        color_continuous_scale=px.colors.sequential.Sunset,
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Number of Workouts",
        template="plotly_dark"
    )
    
    return fig

def create_workout_distribution_chart(df):
    """
    Create a pie chart showing the distribution of workout types.
    
    Args:
        df: DataFrame with workout data including 'workout_type' column
    
    Returns:
        Plotly figure object
    """
    if df is None or df.empty:
        return go.Figure()
    
    # Count workouts by type
    type_counts = df['workout_type'].value_counts()
    
    # Create pie chart
    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title='Workout Type Distribution',
        color_discrete_sequence=["#494E6B", "#98878F", "#985E6D", "#92B6B1", "#B2C9AB"],
    )
    
    # Update layout
    fig.update_layout(
        template="plotly_dark"
    )
    
    return fig
