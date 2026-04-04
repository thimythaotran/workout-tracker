import streamlit as st
import pandas as pd
import os
from datetime import date

# --- SETTINGS ---
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1234"  # set your password here

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

abs_exercises = [
    "Leg Drops", "Reverse Leg Crunches", "Sit-Up Twists",
    "Russian Twists", "Mountain Climber Twists", "Flutter Kicks",
    "Abs Crunches", "Plank", "Leg Raises"
]

# --- LOAD LOG ---
if os.path.exists(DATA_FILE):
    log_df = pd.read_csv(DATA_FILE)
    if not log_df.empty:
        log_df["Date"] = pd.to_datetime(log_df["Date"], errors="coerce")
else:
    log_df = pd.DataFrame(columns=["Week", "Day", "Date", "Exercise", "Set", "Weight", "Duration", "Completed"])

st.set_page_config(page_title="🏋️‍♂️ Workout Tracker", layout="centered")
st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")

# --- PASSWORD PROTECTION ---
user_password = st.text_input("Enter password to edit:", type="password")
can_edit = user_password == EDIT_PASSWORD
if not can_edit:
    st.info("🔒 You are in view-only mode. Enter the password to enable editing.")

# --- SELECT WEEK & DAY ---
week = st.selectbox("Select Week", [1, 2, 3, 4])
day = st.selectbox("Select Day", list(workout_plan.keys()))

# --- AUTO-FILL DATE ---
existing_dates = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]["Date"]
default_date = existing_dates.max().date() if not existing_dates.empty else date.today()
day_date = st.date_input("Date for this Day", value=default_date, key=f"{week}_{day}_date", disabled=not can_edit)

# --- NON-ABS EXERCISES ---
st.subheader(f"Week {week} - {day} ({day_date})")
for ex in workout_plan[day]:
    if ex not in abs_exercises:
        with st.expander(ex):
            sets = st.number_input(
                f"Number of sets for {ex}",
                min_value=1, max_value=10, value=4,
                key=f"{week}_{day}_{ex}_sets",
                disabled=not can_edit
            )

            # Initialize last_weight in session_state if not exists
            if f"{week}_{day}_{ex}_last_weight" not in st.session_state:
                st.session_state[f"{week}_{day}_{ex}_last_weight"] = 5.0

            for s in range(1, sets + 1):
                weight_key = f"{week}_{day}_{ex}_{s}_weight"

                # --- FIXED CASCADING WEIGHT ---
                if weight_key not in st.session_state:
                    # If not yet selected, use last_weight
                    st.session_state[weight_key] = st.session_state[f"{week}_{day}_{ex}_last_weight"]

                weight = st.selectbox(
                    f"Set {s} weight (lbs)",
                    [i * 2.5 for i in range(2, 41)],  # 5 to 100
                    index=[i*2.5 for i in range(2, 41)].index(st.session_state[weight_key]),
                    key=weight_key,
                    disabled=not can_edit
                )

                # Update last_weight only if this set hasn't been manually changed yet
                if st.session_state[weight_key] == st.session_state[f"{week}_{day}_{ex}_last_weight"]:
                    st.session_state[f"{week}_{day}_{ex}_last_weight"] = weight

                if st.button(f"Save {ex} Set {s}", key=f"save_{week}_{day}_{ex}_{s}", disabled=not can_edit):
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

# --- ABS EXERCISES GROUPED ---
if any(ex in workout_plan[day] for ex in abs_exercises):
    with st.expander("💪 Abs Exercises"):
        for set_num in range(1, 3):
            st.markdown(f"### Set {set_num}")
            for ex in workout_plan[day]:
                if ex in abs_exercises:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        duration = st.selectbox(
                            f"{ex} duration (seconds)",
                            list(range(1, 61)),
                            index=29,
                            key=f"{week}_{day}_{ex}_set{set_num}_duration",
                            disabled=not can_edit
                        )
                    with col2:
                        completed = st.checkbox(
                            "Done",
                            key=f"{week}_{day}_{ex}_set{set_num}_completed",
                            disabled=not can_edit
                        )
                    if completed and can_edit:
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