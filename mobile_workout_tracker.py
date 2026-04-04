import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"

# ---------------- WORKOUT PLAN ----------------
workout_plan = {
    "Day 1": ["Flat Bench Press","Incline Bench Press","Cable Flies","Cable Tricep Extensions","Skull Crushers","Dips","Push Ups","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 2": ["Straight Bar Deadlift","Seated Rows","Lat Pull Downs","One Arm Dumbbell Rows","DB Bicep Curl","Hammer Curls","Concentration Curls","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 3": ["Squat","Leg Extensions","Leg Curls","Calf Raises","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 4": ["Shoulder Press","Lateral Raises","Front Raises","Shrugs","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 5": ["Deadlift","Romanian Deadlift","Hamstring Curls","Calf Raises","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 6": ["Chest Dips","Push-ups","Tricep Dips","Cable Flies","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
    "Day 7": ["Abs Crunches","Plank","Leg Raises","Russian Twists","Mountain Climber Twists","Flutter Kicks"]
}

ABS_MASTER_LIST = ["Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks","Abs Crunches","Plank","Leg Raises"]

# ---------------- DATA ENGINE ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])
    try:
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
        return df
    except Exception:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def on_weight_change(week, day, date_val, exercise, set_num, key):
    new_weight = st.session_state[key]
    df = load_data()
    df = df[~((df["Week"] == week) & (df["Day"] == day) & (df["Exercise"] == exercise) & (df["Set"] == set_num))]
    new_row = pd.DataFrame([{"Week": week, "Day": day, "Date": date_val, "Exercise": exercise, "Set": set_num, "Weight": float(new_weight), "Duration": 0}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    # RESET TIMER on weight change
    st.session_state["timer_start"] = time.time()

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

# Initialize Timer State
if "timer_start" not in st.session_state:
    st.session_state["timer_start"] = time.time()

col_ref, col_stat = st.columns([1, 2])
with col_ref:
    if st.button("🔄 Refresh"): st.rerun()
with col_stat:
    st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")

password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

log_df = load_data()
c_w, c_d = st.columns(2)
with c_w: week = st.selectbox("Week", [1, 2, 3, 4])
with c_d: day = st.selectbox("Day", list(workout_plan.keys()))

# --- DATE CALCULATION ---
current_day_num = int(day.split()[-1])
saved_marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]

if not saved_marker.empty:
    calculated_date = saved_marker.iloc[0]["Date"]
else:
    if not log_df.empty:
        log_copy = log_df.copy()
        log_copy["DayNum"] = log_copy["Day"].str.extract('(\d+)').astype(int)
        log_copy["AbsPos"] = ((log_copy["Week"] - 1) * 7) + log_copy["DayNum"]
        current_abs_pos = ((week - 1) * 7) + current_day_num
        log_copy = log_copy.sort_values("AbsPos", ascending=False)
        prev_anchors = log_copy[log_copy["AbsPos"] < current_abs_pos]
        anchor = prev_anchors.iloc[0] if not prev_anchors.empty else log_copy.sort_values("AbsPos").iloc[0]
        calculated_date = anchor["Date"] + timedelta(days=int(current_abs_pos - anchor["AbsPos"]))
    else:
        calculated_date = date.today()

day_date = st.date_input("Workout Date", value=calculated_date, key=f"date_picker_{week}_{day}", disabled=not can_edit)

already_synced = not saved_marker.empty and saved_marker.iloc[0]["Date"] == day_date
button_label = "✅ Schedule Synced" if already_synced else "💾 Lock & Sync ALL Future"

if st.button(button_label, disabled=not can_edit or already_synced):
    current_abs_pos = ((week - 1) * 7) + current_day_num
    for w_idx in range(1, 5):
        for d_idx in range(1, 8):
            this_abs_pos = ((w_idx - 1) * 7) + d_idx
            if this_abs_pos >= current_abs_pos:
                d_name = f"Day {d_idx}"
                new_d = day_date + timedelta(days=int(this_abs_pos - current_abs_pos))
                log_df.loc[(log_df["Week"] == w_idx) & (log_df["Day"] == d_name), "Date"] = new_d
                if log_df[(log_df["Week"] == w_idx) & (log_df["Day"] == d_name) & (log_df["Exercise"] == "DAY MARKER")].empty:
                    marker = pd.DataFrame([{"Week": w_idx, "Day": d_name, "Date": new_d, "Exercise": "DAY MARKER", "Set": 0, "Weight": 0.0, "Duration": 0}])
                    log_df = pd.concat([log_df, marker], ignore_index=True)
    save_data(log_df)
    st.rerun()

st.divider()

# ---------------- REST TIMER UI ----------------
t_col1, t_col2 = st.columns([3, 1])
with t_col1:
    rest_time = int(time.time() - st.session_state["timer_start"])
    st.subheader(f"⏱️ Rest Lapse: `{rest_time}s`")
with t_col2:
    if st.button("Reset Timer", use_container_width=True):
        st.session_state["timer_start"] = time.time()
        st.rerun()

# --- DATA LOADING ---
today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
today_exercises = workout_plan[day]
gym_ex = [e for e in today_exercises if e not in ABS_MASTER_LIST]
abs_ex = [e for e in today_exercises if e in ABS_MASTER_LIST]

# ---------------- GYM EXERCISES ----------------
for ex in gym_ex:
    with st.expander(ex):
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        last_val = 5.0
        for s in range(1, sets_count + 1):
            key = f"input_{week}_{day}_{ex}_{s}"
            saved = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
            val = float(saved["Weight"].iloc[0]) if not saved.empty else (st.session_state[key] if key in st.session_state else last_val)
            st.selectbox(f"Set {s} (lb) {'✅' if not saved.empty else ''}", [i*2.5 for i in range(1, 61)], index=max(0, min(int(val / 2.5) - 1, 59)), key=key, 
                         disabled=not can_edit, on_change=on_weight_change, args=(week, day, day_date, ex, s, key))
            last_val = st.session_state[key]

# ---------------- ABS SECTION ----------------
if abs_ex:
    with st.expander("💪 Abs Section", expanded=True):
        for set_num in [1, 2]:
            st.caption(f"SET {set_num}")
            for ex in abs_ex:
                saved_abs = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == set_num)]
                is_done = not saved_abs.empty
                dur_key = f"abs_{week}_{day}_{ex}_{set_num}"
                
                c1, c2 = st.columns([4, 1]) 
                with c1:
                    st.selectbox(f"{ex} (sec)", list(range(0, 125, 5)), index=6, key=dur_key, disabled=not can_edit)
                with c2:
                    if st.button("✅" if is_done else "💾", key=f"btn_{dur_key}", disabled=not can_edit, use_container_width=True):
                        df_save = load_data()
                        df_save = df_save[~((df_save["Week"]==week) & (df_save["Day"]==day) & (df_save["Exercise"]==ex) & (df_save["Set"]==set_num))]
                        new_row = pd.DataFrame([{"Week":week, "Day":day, "Date":day_date, "Exercise":ex, "Set":set_num, "Weight":0.0, "Duration":st.session_state[dur_key]}])
                        save_data(pd.concat([df_save, new_row], ignore_index=True))
                        st.session_state["timer_start"] = time.time() # RESET TIMER
                        st.rerun()
            st.divider()

# ---------------- SUMMARY ----------------
st.subheader("📊 Summary")
summary_view = today_data[today_data["Exercise"] != "DAY MARKER"]
if not summary_view.empty:
    display_df = summary_view.sort_values(by=["Exercise", "Set"]).copy()
    display_df["Performance"] = display_df.apply(lambda r: f"{r['Weight']} lb" if r["Weight"] > 0 else f"{r['Duration']} sec", axis=1)
    st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)
