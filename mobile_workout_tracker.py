# VERSION: 2.01
# STATUS: Phase 2 - Instant Purge Logic + Versioning Update
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"
VERSION = "2.01" 

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
    except:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def on_data_change(week, day, date_val, exercise, set_num, weight_key, reps_key):
    df = load_data()
    df = df[~((df["Week"] == week) & (df["Day"] == day) & (df["Exercise"] == exercise) & (df["Set"] == set_num))]
    new_row = pd.DataFrame([{
        "Week": week, "Day": day, "Date": date_val, "Exercise": exercise, 
        "Set": set_num, "Weight": float(st.session_state[weight_key]), "Reps": int(st.session_state[reps_key]), "Duration": 0
    }])
    save_data(pd.concat([df, new_row], ignore_index=True))

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

if "timer_start" not in st.session_state: st.session_state["timer_start"] = None
if "timer_running" not in st.session_state: st.session_state["timer_running"] = False

# UI Header
col_ref, col_ver = st.columns([1, 2])
with col_ref:
    if st.button("🔄 Refresh"): st.rerun()
with col_ver:
    st.caption(f"Ver: {VERSION}")

password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

log_df = load_data()
c_w, c_d = st.columns(2)
with c_w: week = st.selectbox("Week", [1, 2, 3, 4])
with c_d: day = st.selectbox("Day", list(workout_plan.keys()))

saved_marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]
day_date = st.date_input("Workout Date", value=saved_marker.iloc[0]["Date"] if not saved_marker.empty else date.today(), disabled=not can_edit)

# ---------------- PRE-RENDER PURGE ----------------
current_workout_exercises = workout_plan[day]
gym_ex = [e for e in current_workout_exercises if e not in ABS_MASTER_LIST]
abs_ex = [e for e in current_workout_exercises if e in ABS_MASTER_LIST]

purge_needed = False
for ex in gym_ex:
    s_key = f"sets_{week}_{day}_{ex}"
    if s_key in st.session_state:
        current_ui_limit = st.session_state[s_key]
        # Check if DB has sets higher than what the UI says
        over_sets = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == ex) & (log_df["Set"] > current_ui_limit)]
        if not over_sets.empty:
            log_df = log_df[~((log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == ex) & (log_df["Set"] > current_ui_limit))]
            purge_needed = True
            # Clear internal memory for those ghost sets
            for s_clear in range(current_ui_limit + 1, 11):
                st.session_state.pop(f"weight_{week}_{day}_{ex}_{s_clear}", None)
                st.session_state.pop(f"reps_{week}_{day}_{ex}_{s_clear}", None)

if purge_needed:
    save_data(log_df)
    st.rerun() # Force a clean state before showing summary

# ---------------- RENDER ----------------
st.divider()
today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]

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
                             on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key))
            with c3:
                st.selectbox("R", list(range(0, 51)), index=s_reps, 
                             key=r_key, disabled=not can_edit, label_visibility="collapsed",
                             on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key))

if abs_ex:
    with st.expander("💪 Abs Section", expanded=False):
        for set_num in [1, 2]:
            st.markdown(f"#### SET {set_num}")
            for ex in abs_ex:
                saved_abs = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == set_num)]
                dur_key, reps_key = f"abs_dur_{week}_{day}_{ex}_{set_num}", f"abs_reps_{week}_{day}_{ex}_{set_num}"
                
                s_dur = int(saved_abs["Duration"].iloc[0]) if not saved_abs.empty else 30
                s_reps = int(saved_abs["Reps"].iloc[0]) if not saved_abs.empty else 10
                
                st.write(f"**{ex}** {'✅' if not saved_abs.empty else ''}")
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1: st.selectbox(f"Secs", list(range(0, 125, 5)), index=int(s_dur/5), key=dur_key, disabled=not can_edit)
                with c2: st.selectbox(f"Reps", list(range(0, 51)), index=s_reps, key=reps_key, disabled=not can_edit)
                with c3:
                    st.write("")
                    if st.button("💾", key=f"btn_{dur_key}", disabled=not can_edit, use_container_width=True):
                        df_s = load_data()
                        df_s = df_s[~((df_s["Week"]==week) & (df_s["Day"]==day) & (df_s["Exercise"]==ex) & (df_s["Set"]==set_num))]
                        new_r = pd.DataFrame([{"Week": week, "Day": day, "Date": day_date, "Exercise": ex, "Set": set_num, "Weight": 0.0, "Reps": st.session_state[reps_key], "Duration": st.session_state[dur_key]}])
                        save_data(pd.concat([df_s, new_r], ignore_index=True))
                        st.rerun()
            st.divider()

st.subheader("📊 Summary")
summary_view = today_data[today_data["Exercise"] != "DAY MARKER"]
if not summary_view.empty:
    display_df = summary_view.sort_values(by=["Exercise", "Set"]).copy()
    display_df["Performance"] = display_df.apply(lambda r: f"{r['Weight']} lb x {r['Reps']}" if r["Weight"] > 0 else f"{r['Duration']}s | {r['Reps']}R", axis=1)
    st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)

if st.session_state["timer_running"]:
    time.sleep(1)
    st.rerun()
