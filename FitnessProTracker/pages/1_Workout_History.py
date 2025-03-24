import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import calendar
import json

from utils import load_data, save_data
from visualization import plot_weekly_activity, create_workout_distribution_chart
from visualization import plot_workout_history
from data_manager import get_workout_history, add_workout

# Set page config
st.set_page_config(
    page_title="Workout History",
    page_icon="📋",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'workout_history' not in st.session_state:
    st.session_state.workout_history = load_data('workout_history.json', [])

# Page title
st.title("Workout History & Tracking")

# Add new workout form
st.sidebar.header("Add New Workout")

with st.sidebar:
    # Date and time inputs
    workout_date = st.date_input("Workout Date", datetime.now())
    workout_time = st.time_input("Workout Time", datetime.now().time())
    
    # Workout details
    workout_type = st.selectbox(
        "Workout Type",
        ["Running", "Walking", "Cycling", "Swimming", "Weight Training", "Yoga", "HIIT", "Other"]
    )
    
    duration = st.slider("Duration (minutes)", 5, 120, 30)
    calories_burned = st.number_input("Calories Burned", min_value=0, max_value=2000, value=300)
    heart_rate = st.slider("Average Heart Rate (bpm)", 60, 200, 130)
    body_temp = st.slider("Body Temperature (°C)", 36.0, 40.0, 37.5, step=0.1)
    
    # Optional notes
    notes = st.text_area("Workout Notes", "")
    
    # Save button
    if st.button("Add Workout"):
        new_workout = {
            "date": workout_date.strftime("%Y-%m-%d"),
            "time": workout_time.strftime("%H:%M"),
            "workout_type": workout_type,
            "duration": duration,
            "calories_burned": calories_burned,
            "heart_rate": heart_rate,
            "body_temp": body_temp,
            "notes": notes
        }
        
        st.session_state.workout_history.append(new_workout)
        save_data('workout_history.json', st.session_state.workout_history)
        st.success("Workout added to history!")
        st.info("Refresh the page to see the updated history")

# Main content area
tab1, tab2, tab3 = st.tabs(["Workout Log", "Analysis", "Calendar View"])

with tab1:
    st.header("Workout Log")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_date_range = st.date_input(
            "Filter by date range",
            [datetime.now() - timedelta(days=30), datetime.now()]
        )
    
    with col2:
        filter_workout_types = st.multiselect(
            "Filter by workout type",
            ["All"] + ["Running", "Walking", "Cycling", "Swimming", "Weight Training", "Yoga", "HIIT", "Other"],
            default="All"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (newest first)", "Date (oldest first)", "Duration", "Calories Burned"]
        )
    
    # Process workout history data
    if st.session_state.workout_history:
        # Convert to DataFrame for easier manipulation
        workout_df = pd.DataFrame(st.session_state.workout_history)
        workout_df['date_obj'] = pd.to_datetime(workout_df['date'])
        
        # Apply filters
        if len(filter_date_range) == 2:
            start_date, end_date = filter_date_range
            workout_df = workout_df[
                (workout_df['date_obj'].dt.date >= start_date) & 
                (workout_df['date_obj'].dt.date <= end_date)
            ]
        
        if "All" not in filter_workout_types and filter_workout_types:
            workout_df = workout_df[workout_df['workout_type'].isin(filter_workout_types)]
        
        # Apply sorting
        if sort_by == "Date (newest first)":
            workout_df = workout_df.sort_values(by='date_obj', ascending=False)
        elif sort_by == "Date (oldest first)":
            workout_df = workout_df.sort_values(by='date_obj', ascending=True)
        elif sort_by == "Duration":
            workout_df = workout_df.sort_values(by='duration', ascending=False)
        elif sort_by == "Calories Burned":
            workout_df = workout_df.sort_values(by='calories_burned', ascending=False)
        
        # Display workout records
        if not workout_df.empty:
            for _, workout in workout_df.iterrows():
                with st.expander(f"{workout['date']} - {workout['workout_type']} ({workout['duration']} min)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Time:** {workout['time']}")
                        st.write(f"**Duration:** {workout['duration']} minutes")
                        st.write(f"**Workout Type:** {workout['workout_type']}")
                    with col2:
                        st.write(f"**Calories Burned:** {workout['calories_burned']} kcal")
                        st.write(f"**Heart Rate:** {workout['heart_rate']} bpm")
                        st.write(f"**Body Temperature:** {workout['body_temp']} °C")
                    
                    if 'notes' in workout and workout['notes']:
                        st.write("**Notes:**")
                        st.write(workout['notes'])
                    
                    # Option to delete this workout
                    if st.button(f"Delete Workout", key=f"delete_{_}"):
                        st.session_state.workout_history.remove(workout.to_dict())
                        save_data('workout_history.json', st.session_state.workout_history)
                        st.success("Workout deleted!")
                        st.info("Refresh the page to see the updated history")
        else:
            st.info("No workouts match your filter criteria.")
    else:
        st.info("No workout data available. Add workouts using the form in the sidebar.")

with tab2:
    st.header("Workout Analysis")
    
    if st.session_state.workout_history:
        # Convert to DataFrame for analysis
        workout_df = pd.DataFrame(st.session_state.workout_history)
        workout_df['date_obj'] = pd.to_datetime(workout_df['date'])
        
        # Time period selector
        time_period = st.radio(
            "Select Time Period:",
            ["Last Week", "Last Month", "Last 3 Months", "All Time"],
            horizontal=True
        )
        
        # Filter based on time period
        today = datetime.now().date()
        if time_period == "Last Week":
            start_date = today - timedelta(days=7)
            filtered_df = workout_df[workout_df['date_obj'].dt.date >= start_date]
            period_title = "Last 7 Days"
        elif time_period == "Last Month":
            start_date = today - timedelta(days=30)
            filtered_df = workout_df[workout_df['date_obj'].dt.date >= start_date]
            period_title = "Last 30 Days"
        elif time_period == "Last 3 Months":
            start_date = today - timedelta(days=90)
            filtered_df = workout_df[workout_df['date_obj'].dt.date >= start_date]
            period_title = "Last 90 Days"
        else:
            filtered_df = workout_df
            period_title = "All Time"
        
        if not filtered_df.empty:
            # Summary stats
            total_workouts = len(filtered_df)
            total_calories = filtered_df['calories_burned'].sum()
            total_duration = filtered_df['duration'].sum()
            avg_heart_rate = filtered_df['heart_rate'].mean()
            
            # Display summary
            st.subheader(f"Summary ({period_title})")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Workouts", total_workouts)
            col2.metric("Total Calories", f"{int(total_calories)} kcal")
            col3.metric("Total Duration", f"{int(total_duration)} min")
            col4.metric("Avg Heart Rate", f"{int(avg_heart_rate)} bpm")
            
            # Weekly activity chart
            st.subheader("Weekly Activity")
            weekly_fig = plot_weekly_activity(filtered_df)
            st.plotly_chart(weekly_fig, use_container_width=True)
            
            # Workout distribution
            st.subheader("Workout Distribution")
            dist_fig = create_workout_distribution_chart(filtered_df)
            st.plotly_chart(dist_fig, use_container_width=True)
            
            # Calories vs Duration scatter plot
            st.subheader("Calories vs Duration")
            fig = px.scatter(
                filtered_df, 
                x="duration", 
                y="calories_burned",
                color="workout_type",
                size="heart_rate",
                hover_name="date",
                title="Calories Burned vs Workout Duration",
                labels={"duration": "Duration (minutes)", "calories_burned": "Calories Burned"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Heart rate over time
            st.subheader("Heart Rate Over Time")
            filtered_df = filtered_df.sort_values(by='date_obj')
            fig = px.line(
                filtered_df,
                x="date_obj",
                y="heart_rate",
                color="workout_type",
                markers=True,
                title="Heart Rate Trends",
                labels={"date_obj": "Date", "heart_rate": "Heart Rate (bpm)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No workout data available for the selected period ({period_title}).")
    else:
        st.info("No workout data available for analysis. Add workouts using the form in the sidebar.")

with tab3:
    st.header("Calendar View")
    
    if st.session_state.workout_history:
        # Convert to DataFrame for calendar
        workout_df = pd.DataFrame(st.session_state.workout_history)
        workout_df['date_obj'] = pd.to_datetime(workout_df['date'])
        
        # Month selector
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox(
                "Select Month",
                range(1, 13),
                index=current_month - 1
            )
        with col2:
            selected_year = st.selectbox(
                "Select Year",
                range(current_year - 5, current_year + 1),
                index=5
            )
        
        # Create calendar data
        cal = calendar.monthcalendar(selected_year, selected_month)
        month_name = calendar.month_name[selected_month]
        
        # Filter workouts for the selected month
        month_workouts = workout_df[
            (workout_df['date_obj'].dt.month == selected_month) & 
            (workout_df['date_obj'].dt.year == selected_year)
        ]
        
        # Group workouts by day
        workout_by_day = month_workouts.groupby(workout_df['date_obj'].dt.day)
        
        # Create calendar
        st.subheader(f"{month_name} {selected_year}")
        
        # Calendar headers
        cols = st.columns(7)
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            cols[i].markdown(f"**{day}**")
        
        # Calendar days
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    day_workouts = workout_by_day.get_group(day) if day in workout_by_day.groups else None
                    
                    if day_workouts is not None:
                        total_workouts = len(day_workouts)
                        total_calories = day_workouts['calories_burned'].sum()
                        
                        # Style for days with workouts
                        cols[i].markdown(f"""
                        <div style='padding:10px; border:1px solid #985E6D; border-radius:5px;'>
                            <strong>{day}</strong><br>
                            {total_workouts} workout{'s' if total_workouts > 1 else ''}<br>
                            {int(total_calories)} kcal
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show workouts when clicking on the day
                        with cols[i].expander("Details"):
                            for _, workout in day_workouts.iterrows():
                                st.write(f"{workout['time']} - {workout['workout_type']}")
                                st.write(f"Duration: {workout['duration']} min | {workout['calories_burned']} kcal")
                    else:
                        cols[i].markdown(f"""
                        <div style='padding:10px; border:1px solid #98878F; border-radius:5px; color:#98878F;'>
                            <strong>{day}</strong><br>
                            No workouts
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No workout data available for calendar view. Add workouts using the form in the sidebar.")
