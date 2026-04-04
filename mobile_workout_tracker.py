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

# ---------------- DATA ENGINE ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])
    try:
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])
            df["Date"] = df["Date"].dt.date
        return df
    except:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------- AUTO-SAVE CALLBACK ----------------
def on_weight_change(week, day, date_val, exercise, set_num, total_sets, key):
    # 1. Get the new weight from session state
    new_weight = st.session_state[key]
    
    # 2. Load fresh data from disk to avoid overwriting other changes
    df = load_data()
    
    # 3. Remove old entry for this specific set
    df = df[~((df["Week"] == week) & 
              (df["Day"] == day) & 
              (df["Exercise"] == exercise) & 
              (df["Set"] == set_num))]
    
    # 4. Add new entry
    new_row = pd.DataFrame({
        "Week": [week], "Day": [day], "Date": [date_val],
        "Exercise": [exercise], "Set": [set_num], 
        "Weight": [float(new_weight)], "Duration": [0]
    })
    df = pd.concat([df, new_row], ignore_index=True)

    # 5. Cascade: Update future UNSAVED sets in session state
    for next_s in range(set_num + 1, total_sets + 1):
        next_key = f"input_{week}_{day}_{exercise}_{next_s}"
        # Check if next set is already saved in the dataframe
        next_exists = df[(df["Week"] == week) & (df["Day"] == day) & 
                         (df["Exercise"] == exercise) & (df["Set"] == next_s)]
        if next_exists.empty:
            st.session_state[next_key] = new_weight

    # 6. Save back to disk
    save_data(df)

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")
log_df = load_data()

st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")

# Password Logic
password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

if not can_edit:
    st.info("🔒 View mode")

# Selection
col_w, col_d = st.columns(2)
with col_w:
    week = st.selectbox("Week", [1, 2, 3, 4])
with col_d:
    day = st.selectbox("Day", list(workout_plan.keys()))

# Date Handling
existing_dates = log_df.loc[(log_df["Week"] == week) & (log_df["Day"] == day), "Date"]
default_date = existing_dates.iloc[0] if not existing_dates.empty else date.today()
day_date = st.date_input("Workout Date", value=default_date, key=f"dt_{week}_{day}", disabled=not can_edit)

if st.button("💾 Lock Date", disabled=not can_edit):
    marker = pd.DataFrame({"Week": [week], "Day": [day], "Date": [day_date], "Exercise": ["DAY MARKER"], "Set": [0], "Weight": [0.0], "Duration": [0]})
    temp_df = pd.concat([log_df, marker], ignore_index=True).drop_duplicates(subset=["Week", "Day", "Exercise", "Set"], keep="last")
    save_data(temp_df)
    st.rerun()

st.divider()

# ---------------- EXERCISES ----------------
st.subheader(f"Exercises: {day}")

for ex in workout_plan[day]:
    if ex in abs_exercises:
        continue

    with st.expander(ex):
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        last_weight_seen = None

        for s in range(1, sets_count + 1):
            key = f"input_{week}_{day}_{ex}_{s}"
            
            # Find if data exists for this set
            saved_row = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & 
                               (log_df["Exercise"] == ex) & (log_df["Set"] == s)]
            
            # Determine Value Logic
            if not saved_row.empty:
                val = float(saved_row["Weight"].iloc[0])
                label_suffix = "✅"
            elif key in st.session_state:
                val = st.session_state[key]
                label_suffix = "⏳"
            elif last_weight_seen is not None:
                val = last_weight_seen
                label_suffix = "👉"
            else:
                val = 5.0
                label_suffix = ""

            idx = int(val / 2.5) - 1
            idx = max(0, min(idx, 59))

            st.selectbox(
                f"Set {s} (lb) {label_suffix}", 
                [i*2.5 for i in range(1, 61)], 
                index=idx, 
                key=key, 
                disabled=not can_edit,
                on_change=on_weight_change,
                args=(week, day, day_date, ex, s, sets_count, key)
            )
            
            last_weight_seen = st.session_state[key] if key in st.session_state else val

# ---------------- ABS SECTION ----------------
if any(ex in abs_exercises for ex in workout_plan[day]):
    with st.expander("💪 Abs Section"):
        for set_num in [1, 2]:
            st.write(f"**Set {set_num}**")
            for ex in workout_plan[day]:
                if ex not in abs_exercises: continue
                
                is_done = not log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & 
                                    (log_df["Exercise"] == ex) & (log_df["Set"] == set_num)].empty

                c1, c2 = st.columns([3, 1])
                dur_key = f"abs_{week}_{day}_{ex}_{set_num}"
                
                with c1:
                    st.selectbox(f"{ex} (sec)", list(range(0, 121, 5)), index=6, key=dur_key, disabled=not can_edit)
                with c2:
                    if st.button("✅" if is_done else "Save", key=f"btn_abs_{dur_key}", disabled=not can_edit):
                        df_abs = load_data()
                        df_abs = df_abs[~((df_abs["Week"]==week) & (df_abs["Day"]==day) & (df_abs["Exercise"]==ex) & (df_abs["Set"]==set_num))]
                        new_abs = pd.DataFrame({"Week":[week], "Day":[day], "Date":[day_date], "Exercise":[ex], "Set":[set_num], "Weight":[0.0], "Duration":[st.session_state[dur_key]]})
                        save_data(pd.concat([df_abs, new_abs], ignore_index=True))
                        st.rerun()

# ---------------- SUMMARY ----------------
st.divider()
st.subheader("📊 Summary")
summary_view = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] != "DAY MARKER")]
if not summary_view.empty:
    st.dataframe(summary_view.sort_values(by=["Exercise", "Set"])[["Exercise", "Set", "Weight", "Duration"]], 
                 use_container_width=True, hide_index=True)
