# VERSION: 2026-04-04 09:00 PM
# STATUS: Phase 2 - Persist UI State + Independent Save
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- DATA ENGINE ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])
    try:
        df = pd.read_csv(DATA_FILE)
        df["Week"] = pd.to_numeric(df["Week"], errors='coerce').fillna(0).astype(int)
        df["Set"] = pd.to_numeric(df["Set"], errors='coerce').fillna(0).astype(int)
        df["Weight"] = pd.to_numeric(df["Weight"], errors='coerce').fillna(0.0).astype(float)
        df["Reps"] = pd.to_numeric(df["Reps"], errors='coerce').fillna(0).astype(int)
        return df
    except:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------- APP SETUP ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

if "timer_start" not in st.session_state: st.session_state["timer_start"] = None
if "timer_running" not in st.session_state: st.session_state["timer_running"] = False

password = st.text_input("Password", type="password")
can_edit = password == EDIT_PASSWORD

log_df = load_data()
col_w, col_d = st.columns(2)
with col_w: week = st.selectbox("Week", [1, 2, 3, 4])
with col_d: 
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

# Date Selection
marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]
day_date = st.date_input("Date", value=pd.to_datetime(marker.iloc[0]["Date"]).date() if not marker.empty else date.today())

st.divider()

# ---------------- GYM EXERCISES ----------------
gym_ex = [e for e in workout_plan[day] if e not in ["Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks","Abs Crunches","Plank","Leg Raises"]]

for ex in gym_ex:
    with st.expander(ex):
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sc_{week}_{day}_{ex}")
        
        # Copy Button
        if st.button("📋 Copy Set 1 to All", key=f"cp_{ex}"):
            for s_idx in range(2, sets_count + 1):
                st.session_state[f"w_{week}_{day}_{ex}_{s_idx}"] = st.session_state[f"w_{week}_{day}_{ex}_1"]
                st.session_state[f"r_{week}_{day}_{ex}_{s_idx}"] = st.session_state[f"r_{week}_{day}_{ex}_1"]
            st.rerun()

        for s in range(1, sets_count + 1):
            w_key, r_key = f"w_{week}_{day}_{ex}_{s}", f"r_{week}_{day}_{ex}_{s}"
            
            # Fetch from DB for initialization ONLY if not already in session state
            db_row = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == ex) & (log_df["Set"] == s)]
            
            if w_key not in st.session_state:
                st.session_state[w_key] = float(db_row["Weight"].iloc[0]) if not db_row.empty else 5.0
            if r_key not in st.session_state:
                st.session_state[r_key] = int(db_row["Reps"].iloc[0]) if not db_row.empty else 8

            c1, c2, c3, c4 = st.columns([0.5, 1.5, 1.5, 0.8])
            c1.write(f"**{s}**")
            # Using index=None or explicit state ensures the UI stays where you put it
            c2.selectbox("Weight", [i*2.5 for i in range(1, 61)], key=w_key, label_visibility="collapsed")
            c3.selectbox("Reps", list(range(0, 21)), key=r_key, label_visibility="collapsed")
            
            # Independent Sync Check (Does DB match the current UI?)
            is_synced = False
            if not db_row.empty:
                if (float(st.session_state[w_key]) == float(db_row["Weight"].iloc[0]) and 
                    int(st.session_state[r_key]) == int(db_row["Reps"].iloc[0])):
                    is_synced = True
            
            if c4.button("✅" if is_synced else "💾", key=f"btn_{w_key}"):
                df_curr = load_data()
                # Remove specific row
                df_curr = df_curr[~((df_curr["Week"] == week) & (df_curr["Day"] == day) & (df_curr["Exercise"] == ex) & (df_curr["Set"] == s))]
                # Add new row
                new_row = pd.DataFrame([{
                    "Week": int(week), "Day": day, "Date": day_date, "Exercise": ex, 
                    "Set": int(s), "Weight": float(st.session_state[w_key]), 
                    "Reps": int(st.session_state[r_key]), "Duration": 0
                }])
                save_data(pd.concat([df_curr, new_row], ignore_index=True))
                st.rerun()

# ---------------- ABS SECTION ----------------
abs_ex = [e for e in workout_plan[day] if e in ["Leg Drops","Reverse Leg Crunches","Sit-Up Twists","Russian Twists","Mountain Climber Twists","Flutter Kicks","Abs Crunches","Plank","Leg Raises"]]
if abs_ex:
    with st.expander("💪 Abs"):
        for s_idx in [1, 2]:
            st.write(f"Set {s_idx}")
            for ex in abs_ex:
                dur_key = f"abs_{week}_{day}_{ex}_{s_idx}"
                db_abs = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == ex) & (log_df["Set"] == s_idx)]
                
                if dur_key not in st.session_state:
                    st.session_state[dur_key] = int(db_abs["Duration"].iloc[0]) if not db_abs.empty else 30
                
                ac1, ac2 = st.columns([4, 1])
                ac1.selectbox(ex, list(range(0, 125, 5)), key=dur_key)
                
                is_a_saved = not db_abs.empty and int(st.session_state[dur_key]) == int(db_abs["Duration"].iloc[0])
                if ac2.button("✅" if is_a_saved else "💾", key=f"abtn_{dur_key}"):
                    df_a = load_data()
                    df_a = df_a[~((df_a["Week"]==week) & (df_a["Day"]==day) & (df_a["Exercise"]==ex) & (df_a["Set"]==s_idx))]
                    new_a = pd.DataFrame([{"Week":week, "Day":day, "Date":day_date, "Exercise":ex, "Set":s_idx, "Weight":0.0, "Reps":0, "Duration":st.session_state[dur_key]}])
                    save_data(pd.concat([df_a, new_a], ignore_index=True))
                    st.rerun()

if st.session_state.get("timer_running"):
    time.sleep(1)
    st.rerun()
