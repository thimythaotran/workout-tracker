# VERSION: 2026-04-04 08:40 PM
# STATUS: Phase 2 - Force Save & Independent Row Logic
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- DATA ENGINE ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"
GEN_TIMESTAMP = "2026-04-04 08:40 PM" 

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])
    try:
        df = pd.read_csv(DATA_FILE)
        # Ensure correct types for matching
        df["Week"] = df["Week"].astype(int)
        df["Set"] = df["Set"].astype(int)
        df["Weight"] = df["Weight"].astype(float)
        df["Reps"] = df["Reps"].astype(int)
        return df
    except Exception:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

if "timer_start" not in st.session_state: st.session_state["timer_start"] = None
if "timer_running" not in st.session_state: st.session_state["timer_running"] = False

# Header
st.caption(f"System Version: {GEN_TIMESTAMP}")
password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

log_df = load_data()
c_w, c_d = st.columns(2)
with c_w: week = st.selectbox("Week", [1, 2, 3, 4])
with c_d: 
    workout_plan = {
        "Day 1": ["Flat Bench Press","Incline Bench Press","Cable Flies","Cable Tricep Extensions","Skull Crushers","Dips","Push Ups","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 2": ["Straight Bar Deadlift","Seated Rows","Lat Pull Downs","One Arm Dumbbell Rows","DB Bicep Curl","Hammer Curls","Concentration Curls","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 3": ["Squat","Leg Extensions","Leg Curls","Calf Raises","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 4": ["Shoulder Press","Lateral Raises","Front Raises","Shrugs","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 5": ["Deadlift","Romanian Deadlift","Hamstring Curls","Calf Raises","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 6": ["Chest Dips","Push-ups","Tricep Dips","Cable Flies","Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks"],
        "Day 7": ["Abs Crunches","Plank","Leg Raises","Russian Twists","Mountain Climber Twists","Flutter Kicks"]
    }
    day = st.selectbox("Day", list(workout_plan.keys()))

ABS_MASTER_LIST = ["Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks","Abs Crunches","Plank","Leg Raises"]

# Date Logic
current_day_num = int(day.split()[-1])
saved_marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]
calc_date = pd.to_datetime(saved_marker.iloc[0]["Date"]).date() if not saved_marker.empty else date.today()
day_date = st.date_input("Workout Date", value=calc_date, disabled=not can_edit)

st.divider()

def show_timer(key_suffix):
    t_c1, t_c2 = st.columns([3, 1.2])
    with t_c1:
        elapsed = int(time.time() - st.session_state["timer_start"]) if (st.session_state["timer_running"] and st.session_state["timer_start"]) else 0
        st.markdown(f"## ⏱️ `{elapsed}s` Rest")
    with t_c2:
        if st.button("Reset Timer", key=f"reset_{key_suffix}"):
            st.session_state["timer_start"] = time.time()
            st.session_state["timer_running"] = True
            st.rerun()

# ---------------- GYM EXERCISES ----------------
today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
gym_ex = [e for e in workout_plan[day] if e not in ABS_MASTER_LIST]

for ex in gym_ex:
    with st.expander(ex):
        show_timer(f"gym_{ex}") 
        
        # Action Bar
        act_c1, act_c2 = st.columns([2, 2])
        with act_c1:
            sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}")
        with act_c2:
            st.write("") # Spacer
            if st.button("📋 Copy Set 1", key=f"copy_{ex}", use_container_width=True):
                s1_w = st.session_state[f"w_{week}_{day}_{ex}_1"]
                s1_r = st.session_state[f"r_{week}_{day}_{ex}_1"]
                for s_idx in range(2, sets_count + 1):
                    st.session_state[f"w_{week}_{day}_{ex}_{s_idx}"] = s1_w
                    st.session_state[f"r_{week}_{day}_{ex}_{s_idx}"] = s1_r
                st.rerun()

        for s in range(1, sets_count + 1):
            w_key, r_key = f"w_{week}_{day}_{ex}_{s}", f"r_{week}_{day}_{ex}_{s}"
            
            # Fetch DB values for this specific set
            row = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
            
            # Init state
            if w_key not in st.session_state:
                st.session_state[w_key] = float(row["Weight"].iloc[0]) if not row.empty else 5.0
            if r_key not in st.session_state:
                st.session_state[r_key] = int(row["Reps"].iloc[0]) if not row.empty else 8
            
            c1, c2, c3, c4 = st.columns([0.5, 1.5, 1.5, 0.8])
            c1.write(f"**{s}**")
            c2.selectbox("Weight", [i*2.5 for i in range(1, 61)], key=w_key, label_visibility="collapsed")
            c3.selectbox("Reps", list(range(0, 21)), key=r_key, label_visibility="collapsed")
            
            # CHECKMARK LOGIC
            is_saved = False
            if not row.empty:
                if (float(st.session_state[w_key]) == float(row["Weight"].iloc[0]) and 
                    int(st.session_state[r_key]) == int(row["Reps"].iloc[0])):
                    is_saved = True
            
            if c4.button("✅" if is_saved else "💾", key=f"btn_{w_key}"):
                # FORCE SAVE
                df_save = load_data()
                # 1. Delete existing
                df_save = df_save[~((df_save["Week"] == week) & 
                                    (df_save["Day"] == day) & 
                                    (df_save["Exercise"] == ex) & 
                                    (df_save["Set"] == s))]
                # 2. Add new
                new_row = pd.DataFrame([{
                    "Week": int(week), "Day": day, "Date": day_date, "Exercise": ex, 
                    "Set": int(s), "Weight": float(st.session_state[w_key]), 
                    "Reps": int(st.session_state[r_key]), "Duration": 0
                }])
                save_data(pd.concat([df_save, new_row], ignore_index=True))
                st.rerun()

# ---------------- ABS SECTION ----------------
abs_ex = [e for e in workout_plan[day] if e in ABS_MASTER_LIST]
if abs_ex:
    with st.expander("💪 Abs Section"):
        for s_idx in [1, 2]:
            st.caption(f"SET {s_idx}")
            for ex in abs_ex:
                dur_key = f"abs_{week}_{day}_{ex}_{s_idx}"
                row_abs = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s_idx)]
                
                if dur_key not in st.session_state:
                    st.session_state[dur_key] = int(row_abs["Duration"].iloc[0]) if not row_abs.empty else 30
                
                ac1, ac2 = st.columns([4, 1])
                ac1.selectbox(ex, list(range(0, 125, 5)), key=dur_key)
                
                abs_saved = not row_abs.empty and int(st.session_state[dur_key]) == int(row_abs["Duration"].iloc[0])
                if ac2.button("✅" if abs_saved else "💾", key=f"btn_{dur_key}"):
                    df_a = load_data()
                    df_a = df_a[~((df_a["Week"]==week) & (df_a["Day"]==day) & (df_a["Exercise"]==ex) & (df_a["Set"]==s_idx))]
                    new_a = pd.DataFrame([{"Week":week, "Day":day, "Date":day_date, "Exercise":ex, "Set":s_idx, "Weight":0.0, "Reps":0, "Duration":st.session_state[dur_key]}])
                    save_data(pd.concat([df_a, new_a], ignore_index=True))
                    st.rerun()

if st.session_state["timer_running"]:
    time.sleep(1)
    st.rerun()
