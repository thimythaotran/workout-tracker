import streamlit as st
import pandas as pd
import os
from datetime import date

# --- SETTINGS ---
DATA_FILE = "workout_log.csv"

# --- WORKOUT PLAN ---
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

# --- LOAD LOG ---
if os.path.exists(DATA_FILE):
    log_df = pd.read_csv(DATA_FILE)
    if not log_df.empty:
        log_df["Date"] = pd.to_datetime(log_df["Date"], errors="coerce")
else:
    log_df = pd.DataFrame(columns=["Week", "Day", "Date", "Exercise", "Set", "Weight", "Duration", "Completed"])

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

abs_exercises = [
    "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
    "Russian Twists", "Mountain Climber Twists", "Flutter Kicks",
    "Abs Crunches", "Plank", "Leg Raises"
]

# Non-abs exercises first
for ex in workout_plan[day]:
    if ex not in abs_exercises:
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
                        "Duration": [0],
                        "Completed": [True]
                    })], ignore_index=True)
                    log_df.to_csv(DATA_FILE, index=False)
                    st.success(f"Saved {ex} Set {s} ({weight} lbs)")

# --- Abs exercises grouped ---
if any(ex in workout_plan[day] for ex in abs_exercises):
    with st.expander("💪 Abs Exercises"):
        # 2 sets
        for set_num in range(1, 3):
            st.markdown(f"### Set {set_num}")
            for ex in workout_plan[day]:
                if ex in abs_exercises:
                    duration = st.selectbox(
                        f"{ex} duration (seconds)",
                        list(range(1, 61)),
                        index=29,  # default 30 seconds
                        key=f"{week}_{day}_{ex}_set{set_num}_duration"
                    )
                    completed = st.checkbox(f"Completed {ex}", key=f"{week}_{day}_{ex}_set{set_num}_completed")
                    if completed:
                        log_df = pd.concat([log_df, pd.DataFrame({
                            "Week": [week],
                            "Day": [day],
                            "Date": [day_date],
                            "Exercise": [ex],
                            "Set": [set_num],
                            "Weight": [0],
                            "Duration": [duration],
                            "Completed": [True]
                        })], ignore_index=True)
                        log_df.to_csv(DATA_FILE, index=False)
                        st.success(f"Saved {ex} Set {set_num} ({duration}s)")

# --- VIEW LOG ---
st.subheader("📊 Your Progress")
week_day_log = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
st.dataframe(week_day_log)

# --- WEEKLY COMPARISON ---
st.subheader("📈 Previous Weeks Comparison")
compare_ex = st.selectbox("Select Exercise to Compare", workout_plan[day])
compare_df = log_df[(log_df["Day"] == day) & (log_df["Exercise"] == compare_ex)]

if not compare_df.empty:
    comparison = compare_df.groupby("Week")["Weight"].mean().reset_index()
    comparison = comparison.sort_values("Week")
    st.line_chart(comparison.rename(columns={"Week": "Week", "Weight": "Avg Weight"}).set_index("Week"))
else:
    st.info("No data yet for this exercise across weeks.")