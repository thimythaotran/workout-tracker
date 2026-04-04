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
    log_df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
else:
    log_df = pd.DataFrame(columns=["Week", "Day", "Date", "Exercise", "Set", "Weight", "Seconds", "Done"])

st.set_page_config(page_title="🏋️‍♂️ Workout Tracker", layout="centered")
st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")

# --- SELECT WEEK & DAY ---
week = st.selectbox("Select Week", [1, 2, 3, 4])
day = st.selectbox("Select Day", list(workout_plan.keys()))

# --- AUTO-FILL DATE (safe) ---
existing_dates = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]["Date"]
if not existing_dates.empty and pd.notna(existing_dates.max()):
    default_date = pd.to_datetime(existing_dates.max()).date()
else:
    default_date = date.today()
day_date = st.date_input("Date for this Day", value=default_date, key=f"{week}_{day}_date")

st.subheader(f"Week {week} - {day} ({day_date})")

# --- DEFINE ABS EXERCISES ---
abs_exercises = [
    "Abs Crunches", "Plank", "Leg Raises", "Russian Twists",
    "Mountain Climber Twists", "Flutter Kicks"
]

# --- ABS GROUPED SECTION ---
if any(ex in abs_exercises for ex in workout_plan[day]):
    with st.expander("💪 Abs Exercises"):
        for set_num in range(1, 3):  # 2 sets for all abs
            st.markdown(f"**Set {set_num}**")
            for ex in workout_plan[day]:
                if ex in abs_exercises:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        done = st.checkbox(f"{ex} done", key=f"{week}_{day}_{ex}_set{set_num}_done")
                    with col2:
                        seconds = st.selectbox(
                            f"Duration (sec) {ex}",
                            list(range(1, 61)),
                            index=29,
                            key=f"{week}_{day}_{ex}_set{set_num}_seconds"
                        )
                    if st.button(f"Save {ex} Set {set_num}", key=f"save_{week}_{day}_{ex}_set{set_num}"):
                        log_df = pd.concat([log_df, pd.DataFrame({
                            "Week": [week],
                            "Day": [day],
                            "Date": [day_date],
                            "Exercise": [ex],
                            "Set": [set_num],
                            "Weight": [None],
                            "Seconds": [seconds],
                            "Done": [done]
                        })], ignore_index=True)
                        log_df.to_csv(DATA_FILE, index=False)
                        st.success(f"Saved {ex} Set {set_num} ({seconds}s, done={done})")

# --- SHOW REGULAR EXERCISES ---
for ex in workout_plan[day]:
    if ex in abs_exercises:
        continue  # skip abs, already handled
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
                    "Seconds": [None],
                    "Done": [None]
                })], ignore_index=True)
                log_df.to_csv(DATA_FILE, index=False)
                st.success(f"Saved {ex} Set {s} ({weight} lbs)")

# --- VIEW LOG ---
st.subheader("📊 Your Progress")
week_day_log = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
st.dataframe(week_day_log)

# --- WEEKLY COMPARISON ---
st.subheader("📈 Previous Weeks Comparison")
compare_ex = st.selectbox("Select Exercise to Compare", workout_plan[day])
compare_df = log_df[(log_df["Day"] == day) & (log_df["Exercise"] == compare_ex)]

if not compare_df.empty:
    if compare_ex in abs_exercises:
        comparison = compare_df.groupby("Week")["Seconds"].mean().reset_index()
        comparison = comparison.sort_values("Week")
        st.line_chart(comparison.rename(columns={"Week": "Week", "Seconds": "Avg Seconds"}).set_index("Week"))
    else:
        comparison = compare_df.groupby("Week")["Weight"].mean().reset_index()
        comparison = comparison.sort_values("Week")
        st.line_chart(comparison.rename(columns={"Week": "Week", "Weight": "Avg Weight"}).set_index("Week"))
else:
    st.info("No data yet for this exercise across weeks.")