from datetime import datetime, timedelta
from utils import load_data, save_data

def calculate_nutrition_needs(age, gender, weight, height, activity_level="Moderate"):
    """
    Calculate recommended daily nutrition needs.
    
    Args:
        age: Age in years
        gender: "Male" or "Female"
        weight: Weight in kg
        height: Height in cm
        activity_level: Activity level (Sedentary, Light, Moderate, Active, Very Active)
    
    Returns:
        Dictionary with calorie and macronutrient recommendations
    """
    # Calculate basal metabolic rate (BMR)
    if gender == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Apply activity multiplier
    activity_multipliers = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    daily_calories = bmr * multiplier
    
    # Calculate macronutrient recommendations
    protein_calories = daily_calories * 0.25  # 25% from protein
    carb_calories = daily_calories * 0.50     # 50% from carbs
    fat_calories = daily_calories * 0.25      # 25% from fat
    
    # Convert to grams
    protein_grams = protein_calories / 4
    carb_grams = carb_calories / 4
    fat_grams = fat_calories / 9
    
    return {
        "calories": daily_calories,
        "protein": protein_grams,
        "carbs": carb_grams,
        "fat": fat_grams
    }

def log_meal(meal_data):
    """Add a meal to the nutrition logs."""
    nutrition_logs = load_data('nutrition_logs.json', [])
    nutrition_logs.append(meal_data)
    return save_data('nutrition_logs.json', nutrition_logs)

def get_nutrition_history(days=None):
    """
    Get nutrition history, optionally filtered to last N days.
    
    Args:
        days: Number of days to filter to, or None for all history
    
    Returns:
        List of meal dictionaries
    """
    nutrition_logs = load_data('nutrition_logs.json', [])
    
    if days is None:
        return nutrition_logs
    
    # Filter to last N days
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    filtered_logs = [log for log in nutrition_logs if log['date'] >= cutoff_date]
    
    # Aggregate by date
    aggregated_data = {}
    for log in filtered_logs:
        date = log['date']
        if date not in aggregated_data:
            aggregated_data[date] = {
                'date': date,
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0
            }
        
        aggregated_data[date]['calories'] += log['calories']
        aggregated_data[date]['protein'] += log['protein']
        aggregated_data[date]['carbs'] += log['carbs']
        aggregated_data[date]['fat'] += log['fat']
    
    # Convert to list and sort by date
    result = list(aggregated_data.values())
    result.sort(key=lambda x: x['date'])
    
    return result
