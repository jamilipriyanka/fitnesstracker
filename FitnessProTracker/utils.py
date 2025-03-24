import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data(filename, default_value=None):
    """Load data from a JSON file or return default value if file doesn't exist."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return default_value
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return default_value

def save_data(filename, data):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {str(e)}")
        return False

def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI from height in cm and weight in kg."""
    if height_cm <= 0 or weight_kg <= 0:
        return 0
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Return the BMI category based on BMI value."""
    if bmi <= 0:
        return "Unknown"
    elif bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def date_range(start_date, end_date):
    """Generate a list of date strings between start_date and end_date."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    date_list = []
    current = start
    
    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    return date_list

def moving_average(data, window=3):
    """Calculate moving average for a list of values."""
    return np.convolve(data, np.ones(window)/window, mode='valid')

def format_duration(minutes):
    """Format duration in minutes to a readable string."""
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"

def calories_to_weight(calories, direction="loss"):
    """Convert calories to weight change (kg) using 7700 kcal ≈ 1 kg."""
    if direction == "loss":
        return abs(calories) / 7700
    else:
        return calories / 7700
