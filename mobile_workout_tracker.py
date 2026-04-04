import streamlit as st
import pandas as pd
import os
from datetime import date

# --- SETTINGS ---
DATA_FILE = "workout_log.csv"

# --- WORKOUT PLAN (full exercises) ---
workout_plan = {
    "Day 1": [
        "Flat Bench Press", "Incline Bench Press", "Cable Flies",
        "Cable Tricep Extensions", "Skull Crushers", "Dips", "Push Ups",
        "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
        "Russian Twists", "Mountain Climber Twists", "Flutter Kicks"
    ],
    "Day 2": [
        "Straight Bar Deadlift", "Seated Rows", "Lat Pull Downs",
        "One Arm Dumbbell Rows", "DB Bicep Curl", "Hammer Curls",
        "Concentration Curls", "Leg Drops", "Reverse Leg Crunches",
        "Sit-Up Twists", "Russian Twists", "Mountain Climber Twists",
        "Flutter Kicks"
    ],
    "Day 3": [
        "Squat", "Leg Extensions", "Leg Curls", "Calf Raises",
        "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
        "Russian Twists", "Mountain Climber Twists", "Flutter Kicks"
    ],
    "Day 4": [
        "Shoulder Press", "Lateral Raises", "Front Raises", "Shrugs",
        "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
        "Russian Twists", "Mountain Climber Twists", "Flutter Kicks"
    ],
    "Day 5": [
        "Deadlift", "Romanian Deadlift", "Hamstring Curls", "Calf Raises",
        "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
        "Russian Twists", "Mountain Climber Twists", "Flutter Kicks"
    ],
    "Day 6": [
        "Chest Dips", "Push-ups", "Tricep Dips", "Cable Flies",
        "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
        "Russian Twists", "Mountain Climber Twists", "Flutter Kicks"
    ],
    "Day 7": [
        "Abs Crunches", "Plank", "Leg Raises", "Russian Twists",
        "Mountain Climber Twists", "Flutter Kicks"
    ]
}

# --- Identify Abs Exercises ---
abs_exercises = [
    "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
    "Russian Twists", "Mountain Climber Twists", "Flutter Kicks",
    "Abs Crunches", "Plank", "Leg Raises"
]

# --- LOAD LOG ---
if os.path.exists(DATA_FILE):
    log_df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
else:
    log_df = pd.DataFrame(columns=["Week", "Day", "Date", "Exercise", "Set", "Weight", "DurationSec", "Done"])

st.set_page_config(page_title="🏋️‍♂️ Workout Tracker", layout="centered")
st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")

# --- SELECT WEEK & DAY ---
week = st.selectbox("Select Week", [1, 2, 3, 4])
day = st.selectbox("Select Day", list(workout_plan.keys()))

# --- AUTO-FILL DATE ---
existing_dates = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]["Date"]
default_date = existing_dates.max().date() if not existing_dates.empty else date.today()
day_date = st.date_input("Date for this Day", value=default_date, key=f"{week}_{day}_date")

# --- SHOW EXERCISES ---
st.subheader(f"Week {week} - {day} ({day_date})")

# Separate abs and normal exercises
normal_exercises = [ex for ex in workout_plan[day] if ex not in abs_exercises]
todays_abs = [ex for ex in workout_plan[day] if ex in abs_exercises]

# --- Normal exercises (sets & weight) ---
for ex in normal_exercises:
    with st.expander(ex):
        sets = st.number_input(f"Number of sets for {ex}", min_value=1, max_value=10, value=4, key=f"{week}_{day}_{ex}_sets")
        for s in range(1, sets + 1):
            weight_key = f"{week}_{day}_{ex}_{s}_weight"
            weight = st.number_input(f"Set {s} weight (lbs)", min_value=0, step=1, key=weight_key)
            if st.button(f"Save {ex} Set {s}", key=f"save_{week}_{day}_{ex}_{s}"):
                log_df = pd.concat([log_df, pd.DataFrame({
                    "Week": [week],
                    "Day": [day],
                    "Date": [day_date],
                    "Exercise": [ex],
                    "Set": [s],
                    "Weight": [weight],
                    "DurationSec": [0],
                    "Done": [True]
                })], ignore_index=True)
                log_df.to_csv(DATA_FILE, index=False)
                st.success(f"Saved {ex} Set {s} ({weight} lbs)")

# --- Abs exercises (checkboxes + duration + 2 sets) ---
if todays_abs:
    with st.expander("Abs"):
        for ex in todays_abs:
            done = st.checkbox(ex, key=f"{week}_{day}_abs_{ex}")
            duration = st.selectbox(f"Duration for {ex} (seconds)", options=list(range(1,61)), index=29, key=f"{week}_{day}_abs_{ex}_duration")
            if done:
                # Save 2 sets if not already saved
                for s in range(1, 3):
                    if log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == ex) & (log_df["Set"] == s)].empty:
                        log_df = pd.concat([log_df, pd.DataFrame({
                            "Week": [week],
                            "Day": [day],
                            "Date": [day_date],
                            "Exercise": [ex],
                            "Set": [s],
                            "Weight": [0],
                            "DurationSec": [duration],
                            "Done": [True]
                        })], ignore_index=True)
                log_df.to_csv(DATA_FILE, index=False)

# --- VIEW LOG ---
st.subheader("📊 Your Progress")
week_day_log = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
st.dataframe(week_day_log)

# --- WEEKLY COMPARISON ---
st.subheader("📈 Previous Weeks Comparison")
compare_ex = st.selectbox("Select Exercise to Compare", normal_exercises + (["Abs"] if todays_abs else []))

if compare_ex == "Abs":
    compare_df = log_df[log_df["Exercise"].isin(todays_abs)]
else:
    compare_df = log_df[log_df["Exercise"] == compare_ex]

if not compare_df.empty:
    if compare_ex == "Abs":
        comparison = compare_df.groupby("Week")["Done"].sum().reset_index()
        comparison = comparison.sort_values("Week")
        st.line_chart(comparison.rename(columns={"Week": "Week", "Done": "Completed Exercises"}).set_index("Week"))
    else:
        comparison = compare_df.groupby("Week")["Weight"].mean().reset_index()
        comparison = comparison.sort_values("Week")
        st.line_chart(comparison.rename(columns={"Week": "Week", "Weight": "Avg Weight"}).set_index("Week"))
else:
    st.info("No data yet for this exercise across weeks.")