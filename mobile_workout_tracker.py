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
week = st.selectbox("Week", [1, 2, 3, 4])
day = st.selectbox("Day", list(workout_plan.keys()))

# ---------------- DATE HANDLING ----------------
existing_dates = log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"]
default_date = existing_dates.iloc[0] if not existing_dates.empty else date.today()

day_date = st.date_input(
    "Workout Date",
    value=default_date,
    key=f"date_widget_{week}_{day}",
    disabled=not can_edit
)

if st.button("💾 Save/Update Date", disabled=not can_edit):
    new_marker = pd.DataFrame({
        "Week": [week], "Day": [day], "Date": [day_date],
        "Exercise": ["DAY MARKER"], "Set": [0], "Weight": [0], "Duration": [0]
    })
    log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"] = day_date
    log_df = pd.concat([log_df, new_marker], ignore_index=True).drop_duplicates(
        subset=["Week", "Day", "Exercise", "Set"], keep="last"
    )
    log_df.to_csv(DATA_FILE, index=False)
    st.success(f"Date set for {day}")
    st.rerun()

st.divider()

# ---------------- NORMAL EXERCISES ----------------
st.subheader(f"Exercises: {day}")

for ex in workout_plan[day]:
    if ex in abs_exercises:
        continue

    with st.expander(ex):
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        
        # Track the weight from the previous set for cascading
        last_weight_seen = None

        for s in range(1, sets_count + 1):
            key = f"input_{week}_{day}_{ex}_{s}"
            
            # Find if there is a saved value in the CSV
            prev_in_log = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & 
                                 (log_df["Exercise"] == ex) & (log_df["Set"] == s)]
            
            # Determine the starting weight for the selectbox
            if not prev_in_log.empty:
                current_val = float(prev_in_log["Weight"].iloc[0])
            elif key in st.session_state:
                current_val = st.session_state[key]
            elif last_weight_seen is not None:
                current_val = last_weight_seen
            else:
                current_val = 10.0 # Standard fallback

            # Calculate dropdown index
            val_idx = int(current_val / 2.5) - 1
            val_idx = max(0, min(val_idx, 59))

            weight = st.selectbox(
                f"Set {s} weight (kg)", 
                [i*2.5 for i in range(1, 61)], 
                index=val_idx, 
                key=key, 
                disabled=not can_edit
            )
            
            # Update cascading variable for the next set
            last_weight_seen = weight

            if st.button(f"Save Set {s}", key=f"btn_{key}", disabled=not can_edit):
                log_df = log_df[~((log_df["Week"] == week) & (log_df["Day"] == day) & 
                                  (log_df["Exercise"] == ex) & (log_df["Set"] == s))]
                new_row = pd.DataFrame({
                    "Week": [week], "Day": [day], "Date": [day_date],
                    "Exercise": [ex], "Set": [s], "Weight": [weight], "Duration": [0]
                })
                log_df = pd.concat([log_df, new_row], ignore_index=True)
                log_df.to_csv(DATA_FILE, index=False)
                st.toast(f"Saved {ex} Set {s}")

# ---------------- ABS SECTION ----------------
if any(ex in abs_exercises for ex in workout_plan[day]):
    with st.expander("💪 Abs Section"):
        for set_num in [1, 2]:
            st.write(f"**Set {set_num}**")
            for ex in workout_plan[day]:
                if ex not in abs_exercises: continue
                
                c1, c2 = st.columns([3, 1])
                dur_key = f"abs_{week}_{day}_{ex}_{set_num}"
                
                with c1:
                    duration = st.selectbox(f"{ex} (sec)", list(range(0, 121, 5)), index=6, key=dur_key, disabled=not can_edit)
                with c2:
                    if st.button("Save", key=f"save_abs_{dur_key}", disabled=not can_edit):
                        log_df = log_df[~((log_df["Week"]==week) & (log_df["Day"]==day) & (log_df["Exercise"]==ex) & (log_df["Set"]==set_num))]
                        new_abs = pd.DataFrame({
                            "Week":[week], "Day":[day], "Date":[day_date],
                            "Exercise":[ex], "Set":[set_num], "Weight":[0], "Duration":[duration]
                        })
                        log_df = pd.concat([log_df, new_abs], ignore_index=True)
                        log_df.to_csv(DATA_FILE, index=False)
                        st.success(f"Saved {ex}")

# ---------------- SUMMARY ----------------
st.divider()
st.subheader("📊 Today's Progress")
current_view = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] != "DAY MARKER")]
if not current_view.empty:
    st.dataframe(current_view[["Exercise", "Set", "Weight", "Duration"]].sort_values(by=["Exercise", "Set"]), use_container_width=True)
