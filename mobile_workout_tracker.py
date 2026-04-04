import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"

# ---------------- WORKOUT PLAN ----------------
workout_plan = {
    "Day 1": ["Flat Bench Press","Incline Bench Press","Cable Flies",
              "Cable Tricep Extensions","Skull Crushers","Dips","Push Ups",
              "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
              "Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 2": ["Straight Bar Deadlift","Seated Rows","Lat Pull Downs",
              "One Arm Dumbbell Rows","DB Bicep Curl","Hammer Curls",
              "Concentration Curls","Leg Drops","Reverse Leg Crunches",
              "Sit-Up Twists","Russian Twists","Mountain Climber Twists",
              "Flutter Kicks"],
    "Day 3": ["Squat","Leg Extensions","Leg Curls","Calf Raises",
              "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
              "Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 4": ["Shoulder Press","Lateral Raises","Front Raises","Shrugs",
              "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
              "Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 5": ["Deadlift","Romanian Deadlift","Hamstring Curls","Calf Raises",
              "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
              "Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 6": ["Chest Dips","Push-ups","Tricep Dips","Cable Flies",
              "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
              "Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 7": ["Abs Crunches","Plank","Leg Raises","Russian Twists",
              "Mountain Climber Twists","Flutter Kicks"]
}

abs_exercises = [
    "Leg Drops","Reverse Leg Crunches","Sit-Up Twists",
    "Russian Twists","Mountain Climber Twists",
    "Flutter Kicks","Abs Crunches","Plank","Leg Raises"
]

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date # Keep as date objects
        return df
    return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])

log_df = load_data()

# ---------------- APP HEADER ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")
st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")
st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- PASSWORD ----------------
password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

if not can_edit:
    st.info("🔒 View mode")

# ---------------- SELECT WEEK/DAY ----------------
week = st.selectbox("Week", [1,2,3,4])
day = st.selectbox("Day", list(workout_plan.keys()))

# ---------------- DATE HANDLING ----------------
# Find if a date already exists for this specific week and day
existing_entry = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]

if not existing_entry.empty:
    default_date = existing_entry["Date"].iloc[0]
else:
    default_date = date.today()

day_date = st.date_input(
    "Workout Date",
    value=default_date,
    key=f"date_input_{week}_{day}",
    disabled=not can_edit
)

# ---------------- SAVE DAY BUTTON ----------------
if st.button("💾 Set/Update Date for this Session", disabled=not can_edit):
    # Update existing entries for this week/day to the new date
    if not existing_entry.empty:
        log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"] = day_date
    else:
        # Add a marker if no data exists yet
        new_row = pd.DataFrame({
            "Week":[week], "Day":[day], "Date":[day_date],
            "Exercise":["DAY MARKER"], "Set":[0], "Weight":[0], "Duration":[0]
        })
        log_df = pd.concat([log_df, new_row], ignore_index=True)
    
    log_df.to_csv(DATA_FILE, index=False)
    st.success(f"Date set to {day_date}")
    st.rerun()

st.divider()

# ---------------- EXERCISE SECTIONS ----------------
st.subheader(f"Exercises for {day}")

for ex in workout_plan[day]:
    if ex in abs_exercises:
        continue

    with st.expander(ex):
        sets = st.number_input(f"Sets", 1, 10, 4, key=f"{week}_{day}_{ex}_sets", disabled=not can_edit)

        for s in range(1, sets + 1):
            key = f"{week}_{day}_{ex}_{s}"
            
            # Find previous weight
            prev = log_df[(log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"]==ex) & (log_df["Set"]==s)]
            default_val = float(prev["Weight"].iloc[0]) if not prev.empty else 10.0

            weight = st.selectbox(f"Set {s} weight", [i*2.5 for i in range(1, 61)], 
                                 index=int(default_val/2.5)-1 if default_val <= 150 else 0,
                                 key=key, disabled=not can_edit)

            if st.button(f"Save Set {s}", key=f"btn_{key}", disabled=not can_edit):
                # Remove old entry
                log_df = log_df[~((log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"]==ex) & (log_df["Set"]==s))]
                # Add new entry
                new_data = pd.DataFrame({
                    "Week":[week], "Day":[day], "Date":[day_date],
                    "Exercise":[ex], "Set":[s], "Weight":[weight], "Duration":[0]
                })
                log_df = pd.concat([log_df, new_data], ignore_index=True)
                log_df.to_csv(DATA_FILE, index=False)
                st.toast(f"Saved {ex} Set {s}!")

# ---------------- ABS SECTION ----------------
if any(ex in abs_exercises for ex in workout_plan[day]):
    with st.expander("💪 Abs & Core"):
        for set_num in range(1, 3):
            st.write(f"**Set {set_num}**")
            for ex in workout_plan[day]:
                if ex not in abs_exercises: continue
                
                col1, col2 = st.columns([3, 1])
                dur_key = f"{week}_{day}_{ex}_abs_{set_num}"
                
                with col1:
                    duration = st.selectbox(ex, list(range(0, 121, 5)), key=dur_key, disabled=not can_edit)
                with col2:
                    if st.button("Save", key=f"save_abs_{dur_key}"):
                        log_df = log_df[~((log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"]==ex) & (log_df["Set"]==set_num))]
                        new_abs = pd.DataFrame({
                            "Week":[week], "Day":[day], "Date":[day_date],
                            "Exercise":[ex], "Set":[set_num], "Weight":[0], "Duration":[duration]
                        })
                        log_df = pd.concat([log_df, new_abs], ignore_index=True)
                        log_df.to_csv(DATA_FILE, index=False)
                        st.rerun()

# ---------------- VIEW LOG ----------------
st.divider()
st.subheader("📊 Summary for Today")
view = log_df[(log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"] != "DAY MARKER")]
st.table(view[["Exercise", "Set", "Weight", "Duration"]])
