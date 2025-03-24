import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os
import pickle

def train_model():
    """Train the calorie prediction model and save it."""
    try:
        # Check if both files exist
        if not (os.path.exists("calories.csv") and os.path.exists("exercise.csv")):
            return False
        
        # Load data
        calories = pd.read_csv("calories.csv")
        exercise = pd.read_csv("exercise.csv")
        
        # Merge datasets
        exercise_df = exercise.merge(calories, on="User_ID")
        exercise_df.drop(columns="User_ID", inplace=True)
        
        # Add BMI column
        exercise_df["BMI"] = exercise_df["Weight"] / ((exercise_df["Height"] / 100) ** 2)
        exercise_df["BMI"] = round(exercise_df["BMI"], 2)
        
        # Prepare the data
        exercise_df = exercise_df[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
        exercise_df = pd.get_dummies(exercise_df, drop_first=True)
        
        # Separate features and labels
        X = exercise_df.drop("Calories", axis=1)
        y = exercise_df["Calories"]
        
        # Train model
        model = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6, random_state=42)
        model.fit(X, y)
        
        # Save model
        with open("calorie_prediction_model.pkl", "wb") as f:
            pickle.dump(model, f)
        
        return True
    except Exception as e:
        print(f"Error training model: {str(e)}")
        return False

def predict_calories(input_data):
    """
    Predict calories burned based on input features.
    
    Args:
        input_data: DataFrame with the following columns:
            - Age
            - BMI
            - Duration
            - Heart_Rate
            - Body_Temp
            - Gender_male (1 for male, 0 for female)
    
    Returns:
        Predicted calories burned
    """
    # Check if model exists, otherwise train
    if not os.path.exists("calorie_prediction_model.pkl"):
        success = train_model()
        if not success:
            # Fallback to a simple linear model
            return fallback_prediction(input_data)
    
    try:
        # Load model
        with open("calorie_prediction_model.pkl", "rb") as f:
            model = pickle.load(f)
        
        # Align column order with training data
        expected_columns = ['Age', 'BMI', 'Duration', 'Heart_Rate', 'Body_Temp', 'Gender_male']
        for col in expected_columns:
            if col not in input_data.columns:
                input_data[col] = 0  # Default to 0 if missing
        
        # Ensure only expected columns are used
        input_data = input_data[expected_columns]
        
        # Make prediction
        prediction = model.predict(input_data)
        return float(prediction[0])
    
    except Exception as e:
        print(f"Error predicting calories: {str(e)}")
        return fallback_prediction(input_data)

def fallback_prediction(input_data):
    """Simple fallback prediction when model is unavailable."""
    # Very basic calorie estimation formula
    age = input_data["Age"].values[0]
    duration = input_data["Duration"].values[0]
    heart_rate = input_data["Heart_Rate"].values[0]
    gender_male = input_data["Gender_male"].values[0]
    
    # Simple formula: higher calories for higher heart rate, longer duration,
    # males, and decreasing with age
    gender_factor = 1.2 if gender_male == 1 else 1.0
    age_factor = 1.0 - (age - 20) * 0.005 if age > 20 else 1.0
    
    calories = duration * (heart_rate - 60) * 0.0175 * gender_factor * age_factor
    
    return max(0, calories)
