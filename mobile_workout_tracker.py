# VERSION: 2026-04-04 06:45 PM
# STATUS: Phase 2 - Added Reps to Abs Section + Auto-save Logic
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"
GEN_TIMESTAMP = "2026-04-04 06:45 PM" 

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
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])
    try:
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.date
        return df
    except Exception:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def on_data_change(week, day, date_val, exercise, set_num, weight_key=None, reps_key=None, dur_key=None):
    df = load_data()
    # Remove existing record
    df = df[~((df["Week"] == week) & (df["Day"] == day) & (df["Exercise"] == exercise) & (df["Set"] == set_num))]
    
    # Get values from session state
    w_val = float(st.session_state[weight_key]) if weight_key else 0.0
    r_val = int(st.session_state[reps_key]) if reps_key else 0
    d_val = int(st.session_state[dur_key]) if dur_key else 0
    
    new_row = pd.DataFrame([{
        "Week": week, "Day": day, "Date": date_val, "Exercise": exercise, 
        "Set": set_num, "Weight": w_val, "Reps": r_val, "Duration": d_val
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

if "timer_start" not in st.session_state: st.session_state["timer_start"] = None
if "timer_running" not in st.session_state: st.session_state["timer_running"] = False

# UI Header
col_ref, col_ver = st.columns([1, 2])
with col_ref:
    if st.button("🔄 Refresh"): st.rerun()
with col_ver:
    st.caption(f"Ver: {GEN_TIMESTAMP}")

password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

log_df = load_data()
c_w, c_d = st.columns(2)
with c_w: week = st.selectbox("Week", [1, 2, 3, 4])
with c_d: day = st.selectbox("Day", list(workout_plan.keys()))

saved_marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]
calculated_date = saved_marker.iloc[0]["Date"] if not saved_marker.empty else date.today()
day_date = st.date_input("Workout Date", value=calculated_date, key=f"date_picker_{week}_{day}", disabled=not can_edit)

st.divider()

def show_timer(key_suffix):
    t_c1, t_c2 = st.columns([3, 1.2])
    with t_c1:
        elapsed = int(time.time() - st.session_state["timer_start"]) if (st.session_state["timer_running"] and st.session_state["timer_start"]) else 0
        st.markdown(f"## ⏱️ `{elapsed}s` Rest")
    with t_c2:
        if st.button("Reset Timer", key=f"reset_{key_suffix}", use_container_width=True):
            st.session_state["timer_start"] = time.time()
            st.session_state["timer_running"] = True
            st.rerun()

today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
gym_ex = [e for e in workout_plan[day] if e not in ABS_MASTER_LIST]
abs_ex = [e for e in workout_plan[day] if e in ABS_MASTER_LIST]

# ---------------- GYM EXERCISES ----------------
for ex in gym_ex:
    with st.expander(ex):
        show_timer(f"gym_{ex}") 
        st.divider()
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        
        h1, h2, h3 = st.columns([1, 2, 2])
        h1.caption("Set")
        h2.caption("Weight (lb)")
        h3.caption("Reps")

        for s in range(1, sets_count + 1):
            w_key, r_key = f"weight_{week}_{day}_{ex}_{s}", f"reps_{week}_{day}_{ex}_{s}"
            saved = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
            
            s_weight = float(saved["Weight"].iloc[0]) if not saved.empty else 5.0
            s_reps = int(saved["Reps"].iloc[0]) if not saved.empty else 8
            
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1: st.write(f"**{s}** {'✅' if not saved.empty else ''}")
            with c2:
                st.selectbox("W", [i*2.5 for i in range(1, 61)], index=max(0, min(int(s_weight / 2.5) - 1, 59)), 
                             key=w_key, disabled=not can_edit, label_visibility="collapsed",
                             on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key, None))
            with c3:
                st.selectbox("R", list(range(0, 51)), index=s_reps, 
                             key=r_key, disabled=not can_edit, label_visibility="collapsed",
                             on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key, None))

# ---------------- ABS SECTION ----------------
if abs_ex:
    with st.expander("💪 Abs Section", expanded=False):
        show_timer("abs_section") 
        st.divider()
        for set_num in [1, 2]:
            st.markdown(f"#### SET {set_num}")
            for ex in abs_ex:
                saved_abs = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == set_num)]
                is_done = not saved_abs.empty
                
                dur_key = f"abs_dur_{week}_{day}_{ex}_{set_num}"
                reps_key = f"abs_reps_{week}_{day}_{ex}_{set_num}"
                
                s_dur = int(saved_abs["Duration"].iloc[0]) if is_done else 30
                s_reps = int(saved_abs["Reps"].iloc[0]) if is_done else 10
                
                st.write(f"**{ex}** {'✅' if is_done else ''}")
                c1, c2 = st.columns(2)
                with c1:
                    st.selectbox(f"Seconds", list(range(0, 125, 5)), index=int(s_dur/5), 
                                 key=dur_key, disabled=not can_edit,
                                 on_change=on_data_change, args=(week, day, day_date, ex, set_num, None, reps_key, dur_key))
                with c2:
                    st.selectbox(f"Reps", list(range(0, 51)), index=s_reps, 
                                 key=reps_key, disabled=not can_edit,
                                 on_change=on_data_change, args=(week, day, day_date, ex, set_num, None, reps_key, dur_key))
            st.divider()

# ---------------- SUMMARY ----------------
st.subheader("📊 Summary")
summary_view = today_data[today_data["Exercise"] != "DAY MARKER"]
if not summary_view.empty:
    display_df = summary_view.sort_values(by=["Exercise", "Set"]).copy()
    display_df["Performance"] = display_df.apply(lambda r: f"{r['Weight']} lb x {r['Reps']}" if r["Weight"] > 0 else f"{r['Duration']}s | {r['Reps']} reps", axis=1)
    st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)

if st.session_state["timer_running"]:
    time.sleep(1)
    st.rerun()
