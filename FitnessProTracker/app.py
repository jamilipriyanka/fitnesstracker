import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json

# Import custom modules
from utils import load_data, save_data, calculate_bmi, get_bmi_category
from data_manager import add_workout, get_workout_history, add_goal, get_goals, update_goal_progress
from visualization import plot_workout_history, plot_goal_progress, create_comparison_chart
from nutrition import calculate_nutrition_needs, log_meal, get_nutrition_history
from models import predict_calories, train_model

# Set page configuration
st.set_page_config(
    page_title="Advanced Fitness Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for maintaining data across reruns
if 'workout_history' not in st.session_state:
    st.session_state.workout_history = load_data('workout_history.json', [])
if 'goals' not in st.session_state:
    st.session_state.goals = load_data('goals.json', [])
if 'nutrition_logs' not in st.session_state:
    st.session_state.nutrition_logs = load_data('nutrition_logs.json', [])
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = load_data('user_profile.json', {
        'name': '',
        'age': 30,
        'gender': 'Male',
        'height': 170,
        'weight': 70,
        'fitness_level': 'Beginner'
    })
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Dashboard'

# App header
st.title("Advanced Fitness Tracker")

# Display logo
st.markdown("""
<div style='text-align: center;'>
    <svg width="100" height="100" viewBox="0 0 100 100">
        <rect width="100" height="100" fill="#494E6B" rx="10" ry="10"/>
        <circle cx="50" cy="30" r="15" fill="#98878F"/>
        <rect x="35" y="50" width="30" height="40" fill="#985E6D" rx="5" ry="5"/>
        <text x="50" y="80" font-size="12" text-anchor="middle" fill="#FFFFFF">FITNESS</text>
    </svg>
</div>
""", unsafe_allow_html=True)

# Create tab navigation
tabs = ["Dashboard", "Workout Tracker", "Goal Setting", "Nutrition", "Profile", "Analysis"]
cols = st.columns(len(tabs))

for i, tab in enumerate(tabs):
    if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
        st.session_state.active_tab = tab

st.write("---")

# Dashboard Tab
if st.session_state.active_tab == "Dashboard":
    st.header("Your Fitness Dashboard")
    
    # User stats summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Profile Summary")
        profile = st.session_state.user_profile
        st.write(f"Name: {profile['name'] if profile['name'] else 'Not set'}")
        st.write(f"Age: {profile['age']}")
        st.write(f"Gender: {profile['gender']}")
        height = profile['height']
        weight = profile['weight']
        
        bmi = calculate_bmi(height, weight)
        bmi_category = get_bmi_category(bmi)
        
        st.write(f"BMI: {bmi:.1f} ({bmi_category})")
        st.write(f"Fitness Level: {profile['fitness_level']}")
    
    with col2:
        st.subheader("Recent Workouts")
        workout_history = st.session_state.workout_history
        
        if workout_history:
            recent_workouts = sorted(workout_history, key=lambda x: x['date'], reverse=True)[:3]
            for workout in recent_workouts:
                st.write(f"📅 {workout['date']}: {workout['workout_type']} - {workout['duration']} min, {workout['calories_burned']} kcal")
        else:
            st.write("No workouts recorded yet.")
    
    with col3:
        st.subheader("Goals Progress")
        goals = st.session_state.goals
        active_goals = [goal for goal in goals if goal['status'] == 'active']
        
        if active_goals:
            for goal in active_goals[:2]:
                progress = goal['current'] / goal['target'] * 100
                st.write(f"🎯 {goal['name']}: {progress:.1f}%")
                st.progress(min(progress/100, 1.0))
        else:
            st.write("No active goals set.")
    
    # Calorie prediction widget
    st.subheader("Predict Calories Burned")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Age", 10, 100, profile['age'])
        bmi = st.slider("BMI", 15.0, 40.0, float(bmi), 0.1)
        duration = st.slider("Duration (min)", 0, 120, 30)
    
    with col2:
        heart_rate = st.slider("Heart Rate (bpm)", 60, 200, 120)
        body_temp = st.slider("Body Temperature (°C)", 36.0, 42.0, 37.5, 0.1)
        gender = st.radio("Gender", ["Male", "Female"], 0 if profile['gender'] == "Male" else 1)
    
    # Prepare prediction input
    gender_male = 1 if gender == "Male" else 0
    
    prediction_data = pd.DataFrame({
        "Age": [age],
        "BMI": [bmi],
        "Duration": [duration],
        "Heart_Rate": [heart_rate],
        "Body_Temp": [body_temp],
        "Gender_male": [gender_male]
    })
    
    # Make prediction and display
    if st.button("Calculate Calories Burned"):
        with st.spinner("Calculating..."):
            # Add a slight delay for better UX
            time.sleep(0.5)
            
            try:
                calories = predict_calories(prediction_data)
                st.success(f"Estimated calories burned: {calories:.2f} kcal")
                
                # Option to save this workout
                if st.button("Save this workout"):
                    workout_data = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "type": "Custom Workout",
                        "duration": duration,
                        "calories": round(calories, 2),
                        "heart_rate": heart_rate,
                        "body_temp": body_temp
                    }
                    add_workout(workout_data)
                    st.success("Workout saved successfully!")
                    st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Error in prediction: {str(e)}")
    
    # Quick statistics and visualizations
    st.subheader("Your Fitness Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Recent Activity Trends")
        
        if len(st.session_state.workout_history) > 0:
            fig = plot_workout_history(st.session_state.workout_history, metric="calories_burned", days=14)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start tracking your workouts to see trends here.")
    
    with col2:
        st.write("Nutrition Overview")
        
        if len(st.session_state.nutrition_logs) > 0:
            nutrition_data = get_nutrition_history(days=7)
            # Create a stacked bar chart of macronutrients
            dates = [entry['date'] for entry in nutrition_data]
            proteins = [entry['protein'] for entry in nutrition_data]
            carbs = [entry['carbs'] for entry in nutrition_data]
            fats = [entry['fat'] for entry in nutrition_data]
            
            fig = go.Figure(data=[
                go.Bar(name='Protein', x=dates, y=proteins, marker_color='#494E6B'),
                go.Bar(name='Carbs', x=dates, y=carbs, marker_color='#98878F'),
                go.Bar(name='Fats', x=dates, y=fats, marker_color='#985E6D')
            ])
            
            fig.update_layout(
                barmode='stack',
                title='Macronutrient Intake',
                xaxis_title='Date',
                yaxis_title='Grams',
                legend_title='Nutrient',
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start logging your meals to see nutrition data here.")

# Workout Tracker Tab
elif st.session_state.active_tab == "Workout Tracker":
    st.header("Workout Tracker")
    
    # Two columns: Log workout and history
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Log New Workout")
        
        workout_type = st.selectbox(
            "Workout Type",
            ["Running", "Cycling", "Swimming", "Weight Training", "Yoga", "HIIT", "Walking", "Other"]
        )
        
        workout_date = st.date_input("Date", datetime.now())
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        
        intensity = st.select_slider(
            "Intensity",
            options=["Very Light", "Light", "Moderate", "Vigorous", "Maximum"],
            value="Moderate"
        )
        
        heart_rate = st.number_input("Average Heart Rate (bpm)", min_value=40, max_value=220, value=120)
        body_temp = st.number_input("Body Temperature (°C)", min_value=36.0, max_value=42.0, value=37.0, step=0.1)
        
        # Optional notes
        notes = st.text_area("Notes (optional)", height=100)
        
        if st.button("Log Workout", key="log_workout_btn"):
            # Calculate estimated calories burned based on model
            profile = st.session_state.user_profile
            
            # Prepare prediction data
            gender_male = 1 if profile['gender'] == "Male" else 0
            bmi = calculate_bmi(profile['height'], profile['weight'])
            
            prediction_data = pd.DataFrame({
                "Age": [profile['age']],
                "BMI": [bmi],
                "Duration": [duration],
                "Heart_Rate": [heart_rate],
                "Body_Temp": [body_temp],
                "Gender_male": [gender_male]
            })
            
            # Make prediction
            try:
                calories = predict_calories(prediction_data)
                
                # Create workout entry
                workout_data = {
                    "date": workout_date.strftime("%Y-%m-%d"),
                    "workout_type": workout_type,
                    "duration": duration,
                    "intensity": intensity,
                    "heart_rate": heart_rate,
                    "body_temp": body_temp,
                    "calories_burned": round(calories, 2),
                    "notes": notes
                }
                
                # Add to history
                add_workout(workout_data)
                
                # Update any relevant goals
                update_goal_progress("workout_count", 1)  # Increment workout count goals
                update_goal_progress("workout_duration", duration)  # Add to duration goals
                update_goal_progress("calories_burned", calories)  # Add to calorie goals
                
                st.success("Workout logged successfully!")
                time.sleep(1)
                st.rerun()
            
            except Exception as e:
                st.error(f"Error logging workout: {str(e)}")
    
    with col2:
        st.subheader("Workout History")
        
        workout_history = get_workout_history()
        
        if not workout_history:
            st.info("No workout history yet. Log your first workout!")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_days = st.selectbox(
                    "Time Period",
                    [7, 14, 30, 90, "All"],
                    format_func=lambda x: f"Last {x} days" if isinstance(x, int) else x,
                    index=2
                )
            
            with col2:
                filter_type = st.multiselect(
                    "Workout Type",
                    ["All"] + list(set(w["type"] for w in workout_history)),
                    default=["All"]
                )
            
            # Apply filters
            filtered_history = workout_history
            
            if isinstance(filter_days, int):
                cutoff_date = (datetime.now() - timedelta(days=filter_days)).strftime("%Y-%m-%d")
                filtered_history = [w for w in filtered_history if w["date"] >= cutoff_date]
            
            if "All" not in filter_type:
                filtered_history = [w for w in filtered_history if w["type"] in filter_type]
            
            # Sort by date (newest first)
            filtered_history = sorted(filtered_history, key=lambda x: x["date"], reverse=True)
            
            # Display statistics
            if filtered_history:
                total_duration = sum(w["duration"] for w in filtered_history)
                total_calories = sum(w["calories_burned"] for w in filtered_history)
                avg_heart_rate = np.mean([w["heart_rate"] for w in filtered_history])
                
                st.write(f"Total Workouts: {len(filtered_history)}")
                st.write(f"Total Duration: {total_duration} minutes")
                st.write(f"Total Calories Burned: {total_calories:.2f} kcal")
                st.write(f"Average Heart Rate: {avg_heart_rate:.1f} bpm")
                
                # Visualizations
                tab1, tab2 = st.tabs(["Table View", "Charts"])
                
                with tab1:
                    # Prepare table data
                    table_data = []
                    for workout in filtered_history:
                        table_data.append({
                            "Date": workout["date"],
                            "Type": workout["workout_type"],
                            "Duration (min)": workout["duration"],
                            "Intensity": workout.get("intensity", "N/A"),
                            "Calories": f"{workout['calories_burned']:.1f}",
                            "Heart Rate": workout["heart_rate"]
                        })
                    
                    st.dataframe(pd.DataFrame(table_data), use_container_width=True)
                
                with tab2:
                    # Calorie burn over time
                    st.write("Calories Burned Over Time")
                    fig = plot_workout_history(filtered_history, metric="calories_burned")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Workout duration by type
                    st.write("Workout Duration by Type")
                    type_duration = {}
                    for workout in filtered_history:
                        t = workout["type"]
                        if t not in type_duration:
                            type_duration[t] = 0
                        type_duration[t] += workout["duration"]
                    
                    fig = px.pie(
                        values=list(type_duration.values()),
                        names=list(type_duration.keys()),
                        title="Time Spent by Workout Type",
                        color_discrete_sequence=px.colors.sequential.Sunset
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No workouts match your filter criteria.")

# Goal Setting Tab
elif st.session_state.active_tab == "Goal Setting":
    st.header("Goal Setting")
    
    # Two columns: Set goals and view goals
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Set New Goal")
        
        goal_type = st.selectbox(
            "Goal Type",
            ["Workout Count", "Weight", "Workout Duration", "Calories Burned", "Custom"]
        )
        
        goal_name = st.text_input("Goal Name", f"{goal_type} Goal")
        
        if goal_type == "Workout Count":
            target = st.number_input("Target Workouts", min_value=1, max_value=1000, value=20)
            current = st.number_input("Current Workouts", min_value=0, max_value=int(target), value=0)
            unit = "workouts"
        elif goal_type == "Weight":
            target = st.number_input("Target Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
            current = st.number_input("Current Weight (kg)", min_value=1.0, max_value=500.0, value=st.session_state.user_profile['weight'], step=0.1)
            unit = "kg"
        elif goal_type == "Workout Duration":
            target = st.number_input("Target Duration (minutes)", min_value=1, max_value=10000, value=500)
            current = st.number_input("Current Duration (minutes)", min_value=0, max_value=int(target), value=0)
            unit = "minutes"
        elif goal_type == "Calories Burned":
            target = st.number_input("Target Calories", min_value=1, max_value=1000000, value=5000)
            current = st.number_input("Current Calories", min_value=0, max_value=int(target), value=0)
            unit = "kcal"
        else:  # Custom
            target = st.number_input("Target Value", min_value=1, max_value=1000000, value=100)
            current = st.number_input("Current Value", min_value=0, max_value=int(target), value=0)
            unit = st.text_input("Unit", "units")
        
        target_date = st.date_input("Target Date", datetime.now() + timedelta(days=30))
        
        if st.button("Set Goal"):
            goal_data = {
                "name": goal_name,
                "type": goal_type.lower().replace(" ", "_"),
                "target": float(target),
                "current": float(current),
                "unit": unit,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "target_date": target_date.strftime("%Y-%m-%d"),
                "status": "active"
            }
            
            add_goal(goal_data)
            st.success("Goal set successfully!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.subheader("Your Goals")
        
        goals = get_goals()
        
        if not goals:
            st.info("No goals set yet. Set your first goal!")
        else:
            # Display goals by status
            tabs = st.tabs(["Active Goals", "Completed Goals"])
            
            with tabs[0]:
                active_goals = [g for g in goals if g['status'] == 'active']
                
                if not active_goals:
                    st.info("No active goals.")
                else:
                    for i, goal in enumerate(active_goals):
                        col1, col2 = st.columns([3, 1])
                        
                        # Calculate progress
                        progress = (goal['current'] / goal['target']) * 100
                        days_left = (datetime.strptime(goal['target_date'], "%Y-%m-%d") - datetime.now()).days
                        
                        with col1:
                            st.write(f"**{goal['name']}**")
                            st.write(f"Progress: {goal['current']}/{goal['target']} {goal['unit']} ({progress:.1f}%)")
                            st.progress(min(progress/100, 1.0))
                            st.write(f"Target Date: {goal['target_date']} ({max(0, days_left)} days left)")
                        
                        with col2:
                            # Update button
                            if st.button("Update", key=f"update_goal_{i}"):
                                st.session_state.goal_to_update = goal
                            
                            # Mark as complete button
                            if st.button("Complete", key=f"complete_goal_{i}"):
                                # Update the goal status
                                goals[goals.index(goal)]['status'] = 'completed'
                                goals[goals.index(goal)]['completion_date'] = datetime.now().strftime("%Y-%m-%d")
                                
                                # Save updated goals
                                save_data('goals.json', goals)
                                st.success(f"Goal '{goal['name']}' marked as complete!")
                                time.sleep(1)
                                st.rerun()
                        
                        st.write("---")
                    
                    # Goal progress visualization
                    st.subheader("Goal Progress Visualization")
                    
                    if len(active_goals) > 0:
                        fig = plot_goal_progress(active_goals)
                        st.plotly_chart(fig, use_container_width=True)
            
            with tabs[1]:
                completed_goals = [g for g in goals if g['status'] == 'completed']
                
                if not completed_goals:
                    st.info("No completed goals yet.")
                else:
                    for goal in completed_goals:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{goal['name']}**")
                            st.write(f"Achieved: {goal['current']}/{goal['target']} {goal['unit']}")
                            
                            # Calculate if completed early or late
                            if 'completion_date' in goal:
                                completion_date = datetime.strptime(goal['completion_date'], "%Y-%m-%d")
                                target_date = datetime.strptime(goal['target_date'], "%Y-%m-%d")
                                
                                days_diff = (completion_date - target_date).days
                                
                                if days_diff < 0:
                                    st.write(f"✅ Completed {abs(days_diff)} days early!")
                                elif days_diff == 0:
                                    st.write("✅ Completed exactly on time!")
                                else:
                                    st.write(f"✅ Completed {days_diff} days after target date")
                        
                        with col2:
                            # Delete button
                            if st.button("Delete", key=f"delete_goal_{goal['name']}"):
                                goals.remove(goal)
                                save_data('goals.json', goals)
                                st.success(f"Goal '{goal['name']}' deleted!")
                                time.sleep(1)
                                st.rerun()
                        
                        st.write("---")
        
        # Goal update form (appears when update button is clicked)
        if hasattr(st.session_state, 'goal_to_update'):
            st.subheader("Update Goal Progress")
            
            goal = st.session_state.goal_to_update
            
            st.write(f"Updating: **{goal['name']}**")
            st.write(f"Current progress: {goal['current']}/{goal['target']} {goal['unit']}")
            
            # Options for update
            update_method = st.radio(
                "Update Method",
                ["Set New Value", "Add to Current Value"]
            )
            
            if update_method == "Set New Value":
                new_value = st.number_input(
                    "New Value",
                    min_value=0.0,
                    max_value=float(goal['target']),
                    value=float(goal['current']),
                    step=0.1
                )
                
                if st.button("Update Progress"):
                    # Find goal in the list and update
                    goals = get_goals()
                    for g in goals:
                        if g['name'] == goal['name'] and g['target_date'] == goal['target_date']:
                            g['current'] = new_value
                            break
                    
                    # Save updated goals
                    save_data('goals.json', goals)
                    
                    # Check if goal is now complete
                    if new_value >= goal['target']:
                        st.balloons()
                        st.success(f"Congratulations! You've completed your goal: {goal['name']}!")
                        
                        # Mark as complete
                        for g in goals:
                            if g['name'] == goal['name'] and g['target_date'] == goal['target_date']:
                                g['status'] = 'completed'
                                g['completion_date'] = datetime.now().strftime("%Y-%m-%d")
                                break
                        
                        # Save updated goals
                        save_data('goals.json', goals)
                    else:
                        st.success("Goal progress updated!")
                    
                    # Remove update state and refresh
                    del st.session_state.goal_to_update
                    time.sleep(1)
                    st.rerun()
            
            else:  # Add to Current Value
                add_value = st.number_input(
                    f"Add to Current ({goal['current']})",
                    min_value=0.0,
                    max_value=float(goal['target'] - goal['current']),
                    value=0.0,
                    step=0.1
                )
                
                if st.button("Update Progress"):
                    # Find goal in the list and update
                    goals = get_goals()
                    for g in goals:
                        if g['name'] == goal['name'] and g['target_date'] == goal['target_date']:
                            g['current'] += add_value
                            break
                    
                    # Save updated goals
                    save_data('goals.json', goals)
                    
                    # Check if goal is now complete
                    if goal['current'] + add_value >= goal['target']:
                        st.balloons()
                        st.success(f"Congratulations! You've completed your goal: {goal['name']}!")
                        
                        # Mark as complete
                        for g in goals:
                            if g['name'] == goal['name'] and g['target_date'] == goal['target_date']:
                                g['status'] = 'completed'
                                g['completion_date'] = datetime.now().strftime("%Y-%m-%d")
                                break
                        
                        # Save updated goals
                        save_data('goals.json', goals)
                    else:
                        st.success("Goal progress updated!")
                    
                    # Remove update state and refresh
                    del st.session_state.goal_to_update
                    time.sleep(1)
                    st.rerun()
            
            # Cancel button
            if st.button("Cancel"):
                del st.session_state.goal_to_update
                st.rerun()

# Nutrition Tab
elif st.session_state.active_tab == "Nutrition":
    st.header("Nutrition Tracker")
    
    # Calculate daily calorie needs
    profile = st.session_state.user_profile
    
    if profile['height'] > 0 and profile['weight'] > 0 and profile['age'] > 0:
        daily_needs = calculate_nutrition_needs(
            age=profile['age'],
            gender=profile['gender'],
            weight=profile['weight'],
            height=profile['height'],
            activity_level=profile.get('activity_level', 'Moderate')
        )
        
        # Two columns: Log food and View nutrition
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Log Food Intake")
            
            meal_date = st.date_input("Date", datetime.now())
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack"]
            )
            
            food_name = st.text_input("Food Name")
            
            calories = st.number_input("Calories (kcal)", min_value=0, value=0)
            protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            carbs = st.number_input("Carbohydrates (g)", min_value=0.0, value=0.0, step=0.1)
            fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=0.1)
            
            serving_size = st.number_input("Serving Size", min_value=0.1, value=1.0, step=0.1)
            
            # Optional notes
            notes = st.text_area("Notes (optional)", height=70)
            
            if st.button("Log Food"):
                meal_data = {
                    "date": meal_date.strftime("%Y-%m-%d"),
                    "meal_type": meal_type,
                    "food_name": food_name,
                    "calories": calories * serving_size,
                    "protein": protein * serving_size,
                    "carbs": carbs * serving_size,
                    "fat": fat * serving_size,
                    "serving_size": serving_size,
                    "notes": notes
                }
                
                log_meal(meal_data)
                st.success("Meal logged successfully!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            st.subheader("Daily Nutrition Summary")
            
            # Date selector
            selected_date = st.date_input("Select Date", datetime.now(), key="nutrition_date")
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            
            # Get nutrition logs for the selected date
            nutrition_logs = st.session_state.nutrition_logs
            day_logs = [log for log in nutrition_logs if log['date'] == selected_date_str]
            
            if not day_logs:
                st.info(f"No nutrition data for {selected_date_str}. Log your meals to see summary.")
            else:
                # Calculate totals
                total_calories = sum(log['calories'] for log in day_logs)
                total_protein = sum(log['protein'] for log in day_logs)
                total_carbs = sum(log['carbs'] for log in day_logs)
                total_fat = sum(log['fat'] for log in day_logs)
                
                # Display daily targets vs. actual
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Calories",
                        f"{total_calories:.0f} kcal",
                        f"{total_calories - daily_needs['calories']:.0f} kcal"
                    )
                
                with col2:
                    st.metric(
                        "Protein",
                        f"{total_protein:.1f} g",
                        f"{total_protein - daily_needs['protein']:.1f} g"
                    )
                
                with col3:
                    carbs_target = daily_needs.get('carbs', 0)
                    fat_target = daily_needs.get('fat', 0)
                    
                    st.metric(
                        "Carbs",
                        f"{total_carbs:.1f} g",
                        f"{total_carbs - carbs_target:.1f} g"
                    )
                    
                    st.metric(
                        "Fat",
                        f"{total_fat:.1f} g",
                        f"{total_fat - fat_target:.1f} g"
                    )
                
                # Macronutrient breakdown pie chart
                st.subheader("Macronutrient Breakdown")
                
                protein_cals = total_protein * 4
                carbs_cals = total_carbs * 4
                fat_cals = total_fat * 9
                
                fig = px.pie(
                    values=[protein_cals, carbs_cals, fat_cals],
                    names=["Protein", "Carbs", "Fat"],
                    title="Calories by Macronutrient",
                    color_discrete_sequence=["#494E6B", "#98878F", "#985E6D"]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Meal breakdown
                st.subheader("Meals")
                
                # Group by meal type
                meals_by_type = {}
                for log in day_logs:
                    meal_type = log['meal_type']
                    if meal_type not in meals_by_type:
                        meals_by_type[meal_type] = []
                    meals_by_type[meal_type].append(log)
                
                for meal_type, logs in meals_by_type.items():
                    with st.expander(f"{meal_type} ({sum(log['calories'] for log in logs):.0f} kcal)"):
                        for log in logs:
                            st.write(f"**{log['food_name']}** - {log['calories']:.0f} kcal")
                            st.write(f"Protein: {log['protein']:.1f}g, Carbs: {log['carbs']:.1f}g, Fat: {log['fat']:.1f}g")
                            if log['notes']:
                                st.write(f"Notes: {log['notes']}")
                            st.write("---")
    else:
        st.warning("Please complete your profile with height, weight, and age information to use the nutrition tracker.")

# Profile Tab
elif st.session_state.active_tab == "Profile":
    st.header("User Profile")
    
    profile = st.session_state.user_profile
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        
        name = st.text_input("Name", profile.get('name', ''))
        age = st.number_input("Age", min_value=1, max_value=120, value=profile.get('age', 30))
        gender = st.radio("Gender", ["Male", "Female"], 0 if profile.get('gender', 'Male') == "Male" else 1)
        
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=profile.get('height', 170))
        weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=profile.get('weight', 70))
        
        fitness_level = st.select_slider(
            "Fitness Level",
            options=["Beginner", "Intermediate", "Advanced", "Elite"],
            value=profile.get('fitness_level', 'Beginner')
        )
        
        activity_level = st.select_slider(
            "Daily Activity Level",
            options=["Sedentary", "Light", "Moderate", "Active", "Very Active"],
            value=profile.get('activity_level', 'Moderate')
        )
    
    with col2:
        st.subheader("Fitness Goals")
        
        weight_goal = st.radio(
            "Weight Goal",
            ["Lose Weight", "Maintain Weight", "Gain Weight"],
            0 if profile.get('weight_goal', 'Maintain Weight') == "Lose Weight" else
            1 if profile.get('weight_goal', 'Maintain Weight') == "Maintain Weight" else 2
        )
        
        fitness_goal = st.multiselect(
            "Fitness Goals",
            ["Improve Cardiovascular Health", "Build Muscle", "Increase Flexibility", "Improve Endurance", "Reduce Stress"],
            default=profile.get('fitness_goal', ["Improve Cardiovascular Health"])
        )
        
        preferred_workouts = st.multiselect(
            "Preferred Workout Types",
            ["Running", "Cycling", "Swimming", "Weight Training", "Yoga", "HIIT", "Walking", "Other"],
            default=profile.get('preferred_workouts', ["Running", "Weight Training"])
        )
        
        workout_frequency = st.number_input(
            "Target Weekly Workout Sessions",
            min_value=0,
            max_value=21,
            value=profile.get('workout_frequency', 3)
        )
        
        sleep_hours = st.slider(
            "Average Sleep Hours",
            min_value=4.0,
            max_value=12.0,
            value=float(profile.get('sleep_hours', 7)),
            step=0.5
        )
    
    if st.button("Save Profile"):
        # Calculate BMI
        bmi = calculate_bmi(height, weight)
        
        # Update profile
        updated_profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "fitness_level": fitness_level,
            "activity_level": activity_level,
            "weight_goal": weight_goal,
            "fitness_goal": fitness_goal,
            "preferred_workouts": preferred_workouts,
            "workout_frequency": workout_frequency,
            "sleep_hours": sleep_hours
        }
        
        # Save profile
        save_data('user_profile.json', updated_profile)
        st.session_state.user_profile = updated_profile
        
        st.success("Profile updated successfully!")
    
    # Display current statistics if height and weight are set
    if height > 0 and weight > 0:
        st.subheader("Your Current Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bmi = calculate_bmi(height, weight)
            bmi_category = get_bmi_category(bmi)
            
            st.metric("BMI", f"{bmi:.1f}", bmi_category)
        
        with col2:
            # Calculate ideal weight range (BMI 18.5-24.9)
            min_weight = 18.5 * ((height / 100) ** 2)
            max_weight = 24.9 * ((height / 100) ** 2)
            
            weight_diff = weight - (min_weight + max_weight) / 2
            
            st.metric(
                "Healthy Weight Range",
                f"{min_weight:.1f} - {max_weight:.1f} kg",
                f"{weight_diff:.1f} kg from midpoint"
            )
        
        with col3:
            if age > 0 and gender:
                # Calculate daily calorie needs
                bmr = 0
                if gender == "Male":
                    bmr = 10 * weight + 6.25 * height - 5 * age + 5
                else:
                    bmr = 10 * weight + 6.25 * height - 5 * age - 161
                
                activity_multiplier = {
                    "Sedentary": 1.2,
                    "Light": 1.375,
                    "Moderate": 1.55,
                    "Active": 1.725,
                    "Very Active": 1.9
                }
                
                daily_calories = bmr * activity_multiplier.get(activity_level, 1.55)
                
                st.metric("Daily Calorie Needs", f"{daily_calories:.0f} kcal")

# Analysis Tab
elif st.session_state.active_tab == "Analysis":
    st.header("Fitness Analysis & Insights")
    
    # Ensure we have workout history
    workout_history = get_workout_history()
    
    if not workout_history or len(workout_history) < 3:
        st.warning("You need at least 3 workout entries to view analysis. Log more workouts to unlock insights.")
    else:
        # Create tabs for different analysis views
        analysis_tabs = st.tabs([
            "Performance Trends", 
            "Workout Patterns", 
            "Calories & Nutrition",
            "Recommendations"
        ])
        
        # Performance Trends
        with analysis_tabs[0]:
            st.subheader("Your Performance Over Time")
            
            # Time frame selector
            time_frame = st.selectbox(
                "Time Frame",
                ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
                index=1
            )
            
            days_lookup = {
                "Last 7 Days": 7,
                "Last 30 Days": 30,
                "Last 90 Days": 90,
                "All Time": 9999  # Effectively all time
            }
            
            days = days_lookup[time_frame]
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            filtered_workouts = [w for w in workout_history if w["date"] >= cutoff_date]
            
            if not filtered_workouts:
                st.info(f"No workout data available for the selected time frame ({time_frame}).")
            else:
                # Metric selection
                metric = st.selectbox(
                    "Performance Metric",
                    ["Calories Burned", "Duration", "Heart Rate"],
                    index=0
                )
                
                metric_key = {
                    "Calories Burned": "calories",
                    "Duration": "duration",
                    "Heart Rate": "heart_rate"
                }[metric]
                
                # Plot trend
                fig = plot_workout_history(filtered_workouts, metric=metric_key)
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate statistics
                metric_values = [float(w[metric_key]) for w in filtered_workouts]
                avg_value = np.mean(metric_values)
                min_value = np.min(metric_values)
                max_value = np.max(metric_values)
                
                # Progress tracker
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average", f"{avg_value:.1f}")
                
                with col2:
                    st.metric("Minimum", f"{min_value:.1f}")
                
                with col3:
                    st.metric("Maximum", f"{max_value:.1f}")
                
                # Detect trends
                if len(filtered_workouts) >= 5:
                    st.subheader("Trend Analysis")
                    
                    # Sort workouts by date
                    sorted_workouts = sorted(filtered_workouts, key=lambda x: x["date"])
                    
                    # Extract dates and values
                    dates = [w["date"] for w in sorted_workouts]
                    values = [float(w[metric_key]) for w in sorted_workouts]
                    
                    # Linear regression to detect trend
                    from scipy import stats
                    
                    x = np.arange(len(dates))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                    
                    trend_strength = abs(r_value)
                    
                    if trend_strength < 0.3:
                        trend_description = "No significant trend detected"
                    else:
                        if slope > 0:
                            trend_description = f"Positive trend detected (Increasing over time, r={r_value:.2f})"
                        else:
                            trend_description = f"Negative trend detected (Decreasing over time, r={r_value:.2f})"
                    
                    st.write(trend_description)
                    
                    # Predict future performance if trend is significant
                    if trend_strength >= 0.3:
                        # Predict next 5 values
                        next_x = np.arange(len(dates), len(dates) + 5)
                        predicted_values = slope * next_x + intercept
                        
                        st.write("Projected performance (next 5 workouts):")
                        
                        for i, val in enumerate(predicted_values):
                            st.write(f"Workout {i+1}: {max(0, val):.1f}")
                        
                        st.write("*Note: These projections are based on your recent trend and may vary.*")
        
        # Workout Patterns
        with analysis_tabs[1]:
            st.subheader("Your Workout Patterns")
            
            # Count workouts by type
            workout_types = {}
            for workout in workout_history:
                w_type = workout["type"]
                if w_type not in workout_types:
                    workout_types[w_type] = 0
                workout_types[w_type] += 1
            
            # Create bar chart
            fig = px.bar(
                x=list(workout_types.keys()),
                y=list(workout_types.values()),
                title="Workout Types Frequency",
                labels={"x": "Workout Type", "y": "Count"},
                color=list(workout_types.keys()),
                color_discrete_sequence=px.colors.sequential.Sunset
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Workout day of week analysis
            st.subheader("Workout Days")
            
            # Count workouts by day of week
            day_counts = [0] * 7
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for workout in workout_history:
                try:
                    workout_date = datetime.strptime(workout["date"], "%Y-%m-%d")
                    day_of_week = workout_date.weekday()
                    day_counts[day_of_week] += 1
                except:
                    pass
            
            # Create day of week chart
            fig = px.bar(
                x=day_names,
                y=day_counts,
                title="Workouts by Day of Week",
                labels={"x": "Day", "y": "Count"},
                color=day_names,
                color_discrete_sequence=px.colors.sequential.Sunset
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Consistency analysis
            consistency_score = 0
            workout_dates = [datetime.strptime(w["date"], "%Y-%m-%d") for w in workout_history]
            
            if workout_dates:
                # Sort dates
                workout_dates.sort()
                
                # Calculate date ranges
                date_range = (workout_dates[-1] - workout_dates[0]).days + 1
                
                # Calculate ideal workout count based on profile frequency
                profile = st.session_state.user_profile
                ideal_frequency = profile.get('workout_frequency', 3)
                ideal_count = (date_range / 7) * ideal_frequency
                
                # Calculate actual count
                actual_count = len(workout_history)
                
                # Calculate consistency score (0-100)
                consistency_score = min(100, (actual_count / ideal_count) * 100) if ideal_count > 0 else 0
                
                # Display consistency gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = consistency_score,
                    title = {'text': "Workout Consistency Score"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#985E6D"},
                        'steps': [
                            {'range': [0, 30], 'color': "#192231"},
                            {'range': [30, 70], 'color': "#494E6B"},
                            {'range': [70, 100], 'color': "#98878F"}
                        ]
                    }
                ))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Consistency insights
                if consistency_score < 30:
                    st.warning("Your workout consistency is low. Try to establish a more regular routine.")
                elif consistency_score < 70:
                    st.info("You have moderate workout consistency. Keep working on your routine!")
                else:
                    st.success("Great job! You have excellent workout consistency.")
        
        # Calories & Nutrition Analysis
        with analysis_tabs[2]:
            st.subheader("Calories & Nutrition Analysis")
            
            # Get workout data
            workout_calories = [(w["date"], w["calories"]) for w in workout_history]
            workout_calories.sort(key=lambda x: x[0])
            
            # Get nutrition data if available
            nutrition_logs = st.session_state.nutrition_logs
            
            if nutrition_logs:
                nutrition_data = [(n["date"], n["calories"]) for n in nutrition_logs]
                nutrition_data.sort(key=lambda x: x[0])
                
                # Merge data by date
                date_data = {}
                
                # Add workout data
                for date, calories in workout_calories:
                    if date not in date_data:
                        date_data[date] = {"date": date, "burned": 0, "consumed": 0}
                    date_data[date]["burned"] += calories
                
                # Add nutrition data
                for date, calories in nutrition_data:
                    if date not in date_data:
                        date_data[date] = {"date": date, "burned": 0, "consumed": 0}
                    date_data[date]["consumed"] += calories
                
                # Convert to list and sort
                combined_data = list(date_data.values())
                combined_data.sort(key=lambda x: x["date"])
                
                # Filter to last 14 days for clarity
                cutoff_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
                recent_data = [d for d in combined_data if d["date"] >= cutoff_date]
                
                if recent_data:
                    # Plot calories in vs. out
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=[d["date"] for d in recent_data],
                        y=[d["consumed"] for d in recent_data],
                        name="Calories Consumed",
                        marker_color="#494E6B"
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=[d["date"] for d in recent_data],
                        y=[d["burned"] for d in recent_data],
                        name="Calories Burned",
                        marker_color="#985E6D"
                    ))
                    
                    fig.update_layout(
                        title="Calories In vs. Calories Out",
                        xaxis_title="Date",
                        yaxis_title="Calories",
                        barmode="group",
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate net calories
                    net_calories = []
                    for d in recent_data:
                        net_calories.append({
                            "date": d["date"],
                            "net": d["consumed"] - d["burned"]
                        })
                    
                    # Plot net calories
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=[d["date"] for d in net_calories],
                        y=[d["net"] for d in net_calories],
                        mode="lines+markers",
                        name="Net Calories",
                        line=dict(color="#98878F", width=3),
                        marker=dict(size=8)
                    ))
                    
                    # Add zero line
                    fig.add_shape(
                        type="line",
                        x0=net_calories[0]["date"],
                        y0=0,
                        x1=net_calories[-1]["date"],
                        y1=0,
                        line=dict(color="white", width=1, dash="dash")
                    )
                    
                    fig.update_layout(
                        title="Net Calories (Consumed - Burned)",
                        xaxis_title="Date",
                        yaxis_title="Net Calories",
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate calories stats
                    avg_net = np.mean([d["net"] for d in net_calories])
                    total_net = sum([d["net"] for d in net_calories])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Average Daily Net Calories", f"{avg_net:.0f} kcal")
                    
                    with col2:
                        # Convert calories to estimated weight change (7700 kcal ≈ 1 kg)
                        weight_change = total_net / 7700
                        st.metric(
                            "Estimated Weight Change",
                            f"{abs(weight_change):.2f} kg",
                            f"{'Gain' if weight_change > 0 else 'Loss'}"
                        )
                else:
                    st.info("Not enough combined workout and nutrition data for analysis.")
            else:
                st.info("Start tracking your nutrition to see calories in vs. calories out analysis.")
                
                # Just show workout calories
                workout_dates = [w[0] for w in workout_calories[-14:]]  # Last 14 entries
                workout_cals = [w[1] for w in workout_calories[-14:]]
                
                fig = px.bar(
                    x=workout_dates,
                    y=workout_cals,
                    title="Calories Burned in Workouts",
                    labels={"x": "Date", "y": "Calories"},
                    color_discrete_sequence=["#985E6D"]
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        with analysis_tabs[3]:
            st.subheader("Personalized Recommendations")
            
            profile = st.session_state.user_profile
            
            # Check if profile is complete
            profile_complete = (
                profile.get('height', 0) > 0 and
                profile.get('weight', 0) > 0 and
                profile.get('age', 0) > 0
            )
            
            if not profile_complete:
                st.warning("Please complete your profile to get personalized recommendations.")
            else:
                # Analyze workout data
                workout_types = {}
                for workout in workout_history:
                    w_type = workout["type"]
                    if w_type not in workout_types:
                        workout_types[w_type] = []
                    workout_types[w_type].append(workout)
                
                # Generate recommendations based on profile and workout history
                st.write("Based on your profile and workout history, here are some personalized recommendations:")
                
                # Recommendation cards
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("#### Workout Recommendations")
                    
                    # Fitness level based recommendations
                    fitness_level = profile.get('fitness_level', 'Beginner')
                    
                    if fitness_level == "Beginner":
                        st.write("🏃‍♂️ **Start with consistent, low-intensity workouts**")
                        st.write("Focus on building a routine with 3-4 sessions per week of moderate activity like walking, light jogging, or beginner strength training.")
                    elif fitness_level == "Intermediate":
                        st.write("🏋️ **Increase workout intensity and variety**")
                        st.write("Add interval training and increase resistance in strength workouts. Aim for 4-5 sessions per week with a mix of cardio and strength.")
                    else:  # Advanced or Elite
                        st.write("🏆 **Optimize for performance and recovery**")
                        st.write("Incorporate periodization, advanced training techniques, and ensure adequate recovery between intense sessions.")
                    
                    # Missing workout types
                    preferred_workouts = profile.get('preferred_workouts', [])
                    missing_workout_types = [w for w in preferred_workouts if w not in workout_types]
                    
                    if missing_workout_types:
                        st.write(f"**Try adding these workouts you're interested in:**")
                        for w_type in missing_workout_types[:3]:  # Show top 3
                            st.write(f"- {w_type}")
                    
                    # Consistency recommendation
                    workout_dates = [datetime.strptime(w["date"], "%Y-%m-%d") for w in workout_history]
                    if workout_dates:
                        workout_dates.sort()
                        last_workout = workout_dates[-1]
                        days_since = (datetime.now() - last_workout).days
                        
                        if days_since > 3:
                            st.write(f"⚠️ **It's been {days_since} days since your last workout**")
                            st.write("Try to maintain a consistent schedule for best results.")
                
                with col2:
                    st.write("#### Nutrition Recommendations")
                    
                    # Calculate BMI and give nutrition advice
                    bmi = calculate_bmi(profile['height'], profile['weight'])
                    weight_goal = profile.get('weight_goal', 'Maintain Weight')
                    
                    # Daily calorie recommendation
                    gender = profile['gender']
                    age = profile['age']
                    weight = profile['weight']
                    height = profile['height']
                    activity = profile.get('activity_level', 'Moderate')
                    
                    # Base Metabolic Rate calculation
                    if gender == "Male":
                        bmr = 10 * weight + 6.25 * height - 5 * age + 5
                    else:
                        bmr = 10 * weight + 6.25 * height - 5 * age - 161
                    
                    # Activity multiplier
                    activity_mult = {
                        "Sedentary": 1.2,
                        "Light": 1.375,
                        "Moderate": 1.55,
                        "Active": 1.725,
                        "Very Active": 1.9
                    }
                    
                    maintenance_calories = bmr * activity_mult.get(activity, 1.55)
                    
                    # Adjust based on goal
                    if weight_goal == "Lose Weight":
                        target_calories = maintenance_calories - 500  # 500 calorie deficit
                        st.write(f"🥗 **Target: {target_calories:.0f} calories per day for weight loss**")
                        st.write("Focus on high protein foods, plenty of vegetables, and controlled portions.")
                    elif weight_goal == "Gain Weight":
                        target_calories = maintenance_calories + 500  # 500 calorie surplus
                        st.write(f"🍲 **Target: {target_calories:.0f} calories per day for weight gain**")
                        st.write("Prioritize protein-rich foods and nutritious, calorie-dense options like nuts, avocados, and whole grains.")
                    else:  # Maintain
                        st.write(f"🍽️ **Target: {maintenance_calories:.0f} calories per day to maintain weight**")
                        st.write("Focus on balanced macronutrients and a variety of whole foods.")
                    
                    # Protein recommendation
                    if "Build Muscle" in profile.get('fitness_goal', []):
                        protein_target = weight * 1.8  # 1.8g per kg for muscle building
                    else:
                        protein_target = weight * 1.2  # 1.2g per kg for general health
                    
                    st.write(f"**Protein target: {protein_target:.0f}g per day**")
                
                # Overall health recommendations
                st.write("#### Overall Health Recommendations")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Sleep & Recovery**")
                    sleep_hours = profile.get('sleep_hours', 7)
                    
                    if sleep_hours < 7:
                        st.write("⚠️ Consider increasing your sleep to 7-9 hours for optimal recovery and performance.")
                    else:
                        st.write("✅ Your target sleep of 7-9 hours is ideal for recovery.")
                    
                    st.write("Schedule regular rest days and consider active recovery like walking or yoga.")
                
                with col2:
                    st.write("**Hydration**")
                    weight_kg = profile.get('weight', 70)
                    water_target = weight_kg * 0.033  # 33ml per kg
                    
                    st.write(f"Aim for {water_target:.1f} liters of water daily.")
                    st.write("Increase intake on workout days and in hot weather.")
                
                with col3:
                    st.write("**Consistency**")
                    st.write("Set a regular workout schedule that fits your lifestyle.")
                    st.write("Track your progress and adjust your goals regularly.")
                    st.write("Even short workouts are better than skipping entirely.")
