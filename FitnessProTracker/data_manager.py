import json
import os
from datetime import datetime, timedelta
from utils import load_data, save_data

def add_workout(workout_data):
    """Add a workout to the workout history."""
    workouts = load_data('workout_history.json', [])
    workouts.append(workout_data)
    return save_data('workout_history.json', workouts)

def get_workout_history(days=None):
    """
    Get workout history, optionally filtered to last N days.
    
    Args:
        days: Number of days to filter to, or None for all history
    
    Returns:
        List of workout dictionaries
    """
    workouts = load_data('workout_history.json', [])
    
    if days is None:
        return workouts
    
    # Filter to last N days
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return [w for w in workouts if w['date'] >= cutoff_date]

def add_goal(goal_data):
    """Add a goal to the goals list."""
    goals = load_data('goals.json', [])
    goals.append(goal_data)
    return save_data('goals.json', goals)

def get_goals():
    """Get all goals."""
    return load_data('goals.json', [])

def update_goal_progress(goal_type, amount):
    """
    Update progress for all active goals of a specific type.
    
    Args:
        goal_type: Type of goal to update (e.g., 'workout_count', 'calories_burned')
        amount: Amount to add to the current progress
    """
    goals = load_data('goals.json', [])
    updated = False
    
    for goal in goals:
        if goal['status'] == 'active' and goal['type'] == goal_type:
            goal['current'] += amount
            
            # Check if goal has been completed
            if goal['current'] >= goal['target']:
                goal['status'] = 'completed'
                goal['completion_date'] = datetime.now().strftime("%Y-%m-%d")
            
            updated = True
    
    if updated:
        save_data('goals.json', goals)
    
    return updated

def delete_goal(goal_name, target_date):
    """Delete a goal by name and target date."""
    goals = load_data('goals.json', [])
    
    for i, goal in enumerate(goals):
        if goal['name'] == goal_name and goal['target_date'] == target_date:
            del goals[i]
            save_data('goals.json', goals)
            return True
    
    return False
