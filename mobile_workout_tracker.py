# VERSION: 2026-04-04 06:10 PM
# STATUS: Phase 2 - Reactive Save Buttons + Mobile Optimized + Manual Save
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"
GEN_TIMESTAMP = "2026-04-04 06:10 PM" 

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
            if "Reps" not in df.columns: df["Reps"] = 8
        return df
    except Exception:
        return pd.DataFrame(columns=["Week","Day","Date","Exercise","Set","Weight","Reps","Duration"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

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

current_day_num = int(day.split()[-1])
saved_marker = log_df[(log_df["Week"] == week) & (log_df["Day"] == day) & (log_df["Exercise"] == "DAY MARKER")]
calculated_date = saved_marker.iloc[0]["Date"] if not saved_marker.empty else date.today()
day_date = st.date_input("Workout Date", value=calculated_date, key=f"date_picker_{week}_{day}", disabled=not can_edit)

if st.button("💾 Lock & Sync ALL Future", disabled=not can_edit):
    current_abs_pos = ((week - 1) * 7) + current_day_num
    for w_idx in range(1, 5):
        for d_idx in range(1, 8):
            this_abs_pos = ((w_idx - 1) * 7) + d_idx
            if this_abs_pos >= current_abs_pos:
                d_name = f"Day {d_idx}"
                new_d = day_date + timedelta(days=int(this_abs_pos - current_abs_pos))
                log_df.loc[(log_df["Week"] == w_idx) & (log_df["Day"] == d_name), "Date"] = new_d
                if log_df[(log_df["Week"] == w_idx) & (log_df["Day"] == d_name) & (log_df["Exercise"] == "DAY MARKER")].empty:
                    marker = pd.DataFrame([{"Week": w_idx, "Day": d_name, "Date": new_d, "Exercise": "DAY MARKER", "Set": 0, "Weight": 0.0, "Reps": 0, "Duration": 0}])
                    log_df = pd.concat([log_df, marker], ignore_index=True)
    save_data(log_df)
    st.rerun()

st.divider()

def show_timer(key_suffix):
    t_c1, t_c2 = st.columns([3, 1.2])
    with t_c1:
        elapsed = int(time.time() - st.session_state["timer_start"]) if (st.session_state["timer_running"] and st.session_state["timer_start"]) else 0
        st.markdown(f"## ⏱️ `{elapsed}s` Rest")
    with t_c2:
        st.write("")
        if st.button("Reset Timer", key=f"reset_{key_suffix}", use_container_width=True):
            st.session_state["timer_start"] = time.time()
            st.session_state["timer_running"] = True
            st.rerun()

today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
today_exercises = workout_plan[day]
gym_ex = [e for e in today_exercises if e not in ABS_MASTER_LIST]
abs_ex = [e for e in today_exercises if e in ABS_MASTER_LIST]

# ---------------- GYM EXERCISES ----------------
for ex in gym_ex:
    with st.expander(ex):
        show_timer(f"gym_{ex}") 
        st.divider()
        sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        
        h1, h2, h3, h4 = st.columns([0.7, 1.5, 1.5, 0.8])
        h1.caption("Set")
        h2.caption("Weight")
        h3.caption("Reps")
        h4.caption("Save")

        for s in range(1, sets_count + 1):
            w_key = f"w_{week}_{day}_{ex}_{s}"
            r_key = f"r_{week}_{day}_{ex}_{s}"
            
            # Get existing data for this specific set
            row_match = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
            
            # Determine initial values for selectboxes
            db_w = float(row_match["Weight"].iloc[0]) if not row_match.empty else 5.0
            db_r = int(row_match["Reps"].iloc[0]) if not row_match.empty else 8
            
            c1, c2, c3, c4 = st.columns([0.7, 1.5, 1.5, 0.8])
            with c1:
                st.write(f"**{s}**")
            with c2:
                # Use db value if key not in session state yet
                w_val = st.selectbox("W", [i*2.5 for i in range(1, 61)], index=max(0, min(int(db_w / 2.5) - 1, 59)), 
                                     key=w_key, disabled=not can_edit, label_visibility="collapsed")
            with c3:
                r_val = st.selectbox("R", list(range(0, 21)), index=db_r, 
                                     key=r_key, disabled=not can_edit, label_visibility="collapsed")
            with c4:
                # REACTIVE LOGIC: Show Check only if session state values match the DB exactly
                is_synced = (not row_match.empty and 
                             float(st.session_state[w_key]) == db_w and 
                             int(st.session_state[r_key]) == db_r)
                
                btn_icon = "✅" if is_synced else "💾"
                
                if st.button(btn_icon, key=f"btn_{w_key}", disabled=not can_edit):
                    df_s = load_data()
                    df_s = df_s[~((df_s["Week"]==week) & (df_s["Day"]==day) & (df_s["Exercise"]==ex) & (df_s["Set"]==s))]
                    new_r = pd.DataFrame([{
                        "Week": week, "Day": day, "Date": day_date, "Exercise": ex, 
                        "Set": s, "Weight": float(st.session_state[w_key]), 
                        "Reps": int(st.session_state[r_key]), "Duration": 0
                    }])
                    save_data(pd.concat([df_s, new_r], ignore_index=True))
                    st.rerun()

# ---------------- ABS SECTION ----------------
if abs_ex:
    with st.expander("💪 Abs Section", expanded=False):
        show_timer("abs_section") 
        st.divider()
        for set_num in [1, 2]:
            st.caption(f"SET {set_num}")
            for ex in abs_ex:
                dur_key = f"abs_{week}_{day}_{ex}_{set_num}"
                row_abs = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == set_num)]
                db_dur = int(row_abs["Duration"].iloc[0]) if not row_abs.empty else 30
                
                c1, c2 = st.columns([4, 1]) 
                with c1:
                    st.selectbox(f"{ex} (sec)", list(range(0, 125, 5)), index=max(0, db_dur // 5), 
                                 key=dur_key, disabled=not can_edit, label_visibility="collapsed")
                with c2:
                    # Reactive logic for Abs
                    abs_synced = (not row_abs.empty and int(st.session_state[dur_key]) == db_dur)
                    if st.button("✅" if abs_synced else "💾", key=f"btn_{dur_key}", disabled=not can_edit, use_container_width=True):
                        df_save = load_data()
                        df_save = df_save[~((df_save["Week"]==week) & (df_save["Day"]==day) & (df_save["Exercise"]==ex) & (df_save["Set"]==set_num))]
                        new_row = pd.DataFrame([{"Week":week, "Day":day, "Date":day_date, "Exercise":ex, "Set":set_num, "Weight":0.0, "Reps":0, "Duration":st.session_state[dur_key]}])
                        save_data(pd.concat([df_save, new_row], ignore_index=True))
                        st.rerun()
            st.divider()

# ---------------- SUMMARY ----------------
st.subheader("📊 Summary")
summary_view = today_data[today_data["Exercise"] != "DAY MARKER"]
if not summary_view.empty:
    display_df = summary_view.sort_values(by=["Exercise", "Set"]).copy()
    display_df["Performance"] = display_df.apply(lambda r: f"{r['Weight']} lb x {r['Reps']}" if r["Weight"] > 0 else f"{r['Duration']} sec", axis=1)
    st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)

if st.session_state["timer_running"]:
    time.sleep(1)
    st.rerun()
