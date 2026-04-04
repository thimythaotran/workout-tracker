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
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df = df.dropna(subset=["Date"])
                df["Date"] = df["Date"].dt.date
            return df
        except Exception:
            return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])
    return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])

# ---------------- AUTO-SAVE FUNCTION ----------------
def auto_save_weight(week, day, date_val, exercise, set_num, weight, total_sets):
    # Global load to get current state
    df = load_data()
    
    # 1. Update the current set
    df = df[~((df["Week"] == week) & (df["Day"] == day) & 
              (df["Exercise"] == exercise) & (df["Set"] == set_num))]
    
    new_row = pd.DataFrame({
        "Week": [week], "Day": [day], "Date": [date_val],
        "Exercise": [exercise], "Set": [set_num], "Weight": [weight], "Duration": [0]
    })
    df = pd.concat([df, new_row], ignore_index=True)

    # 2. Cascade to future unsaved sets in session state
    for next_s in range(set_num + 1, total_sets + 1):
        next_key = f"input_{week}_{day}_{exercise}_{next_s}"
        # Only update session state if not already saved in the file
        next_exists = df[(df["Week"] == week) & (df["Day"] == day) & 
                         (df["Exercise"] == exercise) & (df["Set"] == next_s)]
        if next_exists.empty:
            st.session_state[next_key] = weight

    df.to_csv(DATA_FILE, index=False)

# ---------------- APP SETUP ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")
log_df = load_data()

st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")
st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- PASSWORD ----------------
password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

if not can_edit:
    st.info("🔒 View mode")

# ---------------- SELECT WEEK/DAY ----------------
week = st.selectbox("Week", [1, 2, 3, 4])
day = st.selectbox("Day", list(workout_plan.keys()))

# ---------------- DATE HANDLING ----------------
existing_dates = log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"]
default_date = existing_dates.iloc[0] if not existing_dates.empty else date.today()

day_date = st.date_input("Workout Date", value=default_date, key=f"date_widget_{week}_{day}", disabled=not can_edit)

if st.button("💾 Save/Update Date", disabled=not can_edit):
    marker = pd.DataFrame({"Week": [week], "Day": [day], "Date": [day_date], "Exercise": ["DAY MARKER"], "Set": [0], "Weight": [0.0], "Duration": [0]})
    log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"] = day_date
    log_df = pd.concat([log_df, marker], ignore_index=True).drop_duplicates(subset=["Week", "Day", "Exercise", "Set"], keep="last")
    log_df.to_csv(DATA_FILE, index=False)
    st.rerun()

st.divider()

# ---------------- NORMAL EXERCISES ----------------
st.subheader(f"Exercises: {day}")

for ex in workout_plan[day]:
    if ex in abs_exercises:
        continue

    with st.expander(ex):
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        last_weight_seen = None

        for s in range(1, sets_count + 1):
            key = f"input_{week}_{day}_{ex}_{s}"
            
            # Find existing data
            prev_in_log = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & 
                                 (log_df["Exercise"] == ex) & (log_df["Set"] == s)]
            
            if not prev_in_log.empty:
                current_val = float(prev_in_log["Weight"].iloc[0])
            elif key in st.session_state:
                current_val = st.session_state[key]
            elif last_weight_seen is not None:
                current_val = last_weight_seen
            else:
                current_val = 5.0

            val_idx = int(current_val / 2.5) - 1
            val_idx = max(0, min(val_idx, 59))

            # AUTO-SAVE ON CHANGE
            weight = st.selectbox(
                f"Set {s} weight (lb) {'✅' if not prev_in_log.empty else ''}", 
                [i*2.5 for i in range(1, 61)], 
                index=val_idx, 
                key=key, 
                disabled=not can_edit,
                on_change=auto_save_weight,
                args=(week, day, day_date, ex, s, st.session_state.get(key, current_val), sets_count)
            )
            
            last_weight_seen = weight

# ---------------- ABS SECTION (Manual Save) ----------------
if any(ex in abs_exercises for ex in workout_plan[day]):
    with st.expander("💪 Abs Section"):
        for set_num in [1, 2]:
            st.markdown(f"**Set {set_num}**")
            for ex in workout_plan[day]:
                if ex not in abs_exercises: continue
                
                is_done = not log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & 
                                    (log_df["Exercise"] == ex) & (log_df["Set"] == set_num)].empty

                c1, c2 = st.columns([3, 1])
                dur_key = f"abs_{week}_{day}_{ex}_{set_num}"
                
                with c1:
                    duration = st.selectbox(f"{ex} (sec)", list(range(0, 121, 5)), index=6, key=dur_key, disabled=not can_edit)
                with c2:
                    if st.button("✅" if is_done else "Save", key=f"save_abs_{dur_key}", disabled=not can_edit):
                        log_df = log_df[~((log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"]==ex) & (log_df["Set"]==set_num))]
                        new_abs = pd.DataFrame({"Week":[week], "Day":[day], "Date":[day_date], "Exercise":[ex], "Set":[set_num], "Weight":[0.0], "Duration":[duration]})
                        pd.concat([log_df, new_abs], ignore_index=True).to_csv(DATA_FILE, index=False)
                        st.rerun()

# ---------------- SUMMARY ----------------
st.divider()
st.subheader("📊 Today's Progress")
current_view = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] != "DAY MARKER")]
if not current_view.empty:
    st.dataframe(current_view.sort_values(by=["Exercise", "Set"])[["Exercise", "Set", "Weight", "Duration"]], 
                 use_container_width=True, hide_index=True)
