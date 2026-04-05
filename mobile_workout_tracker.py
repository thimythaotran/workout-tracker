# VERSION: 2.06
# STATUS: Phase 2 - High-Visibility Red Timer
# ----------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime, timedelta

# ---------------- SETTINGS ----------------
DATA_FILE = "workout_log.csv"
EDIT_PASSWORD = "1"
VERSION = "2.06" 

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
    raw_weight = st.session_state[weight_key]
    weight_val = 0.0 if raw_weight == "Bodyweight" else float(raw_weight)
    new_row = pd.DataFrame([{
        "Week": week, "Day": day, "Date": date_val, "Exercise": exercise, 
        "Set": set_num, "Weight": weight_val, "Reps": int(st.session_state[reps_key]), "Duration": 0
    }])
    save_data(pd.concat([df, new_row], ignore_index=True))

def duplicate_set_one(week, day, date_val, exercise, total_sets):
    w1_key = f"weight_{week}_{day}_{exercise}_1"
    r1_key = f"reps_{week}_{day}_{exercise}_1"
    if w1_key in st.session_state and r1_key in st.session_state:
        raw_w = st.session_state[w1_key]
        val_w = 0.0 if raw_w == "Bodyweight" else float(raw_w)
        val_r = int(st.session_state[r1_key])
        df = load_data()
        df = df[~((df["Week"] == week) & (df["Day"] == day) & (df["Exercise"] == exercise) & (df["Set"] > 0))]
        new_rows = []
        for s in range(1, total_sets + 1):
            new_rows.append({"Week": week, "Day": day, "Date": date_val, "Exercise": exercise, "Set": s, "Weight": val_w, "Reps": val_r, "Duration": 0})
            st.session_state[f"weight_{week}_{day}_{exercise}_{s}"] = raw_w
            st.session_state[f"reps_{week}_{day}_{exercise}_{s}"] = val_r
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df)

# ---------------- APP UI ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

if "timer_start" not in st.session_state: st.session_state["timer_start"] = None
if "timer_running" not in st.session_state: st.session_state["timer_running"] = False

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

st.divider()
today_data = log_df[(log_df["Week"] == week) & (log_df["Day"] == day)]
gym_ex = [e for e in workout_plan[day] if e not in ABS_MASTER_LIST]
abs_ex = [e for e in workout_plan[day] if e in ABS_MASTER_LIST]

def show_timer(key_suffix):
    t_c1, t_c2 = st.columns([3, 1.2])
    with t_c1:
        elapsed = int(time.time() - st.session_state["timer_start"]) if (st.session_state["timer_running"] and st.session_state["timer_start"]) else 0
        # High Visibility Red Timer Logic
        st.markdown(f"<h1 style='color: #FF0000; text-align: left; font-size: 50px; margin-bottom: 0px;'>⏱️ {elapsed}s</h1>", unsafe_allow_html=True)
        st.caption("RESTING")
    with t_c2:
        st.write("") # Spacer
        if st.button("RESET", key=f"reset_{key_suffix}", use_container_width=True):
            st.session_state["timer_start"] = time.time()
            st.session_state["timer_running"] = True
            st.rerun()

# ---------------- GYM EXERCISES ----------------
weight_options = ["Bodyweight"] + [float(i*2.5) for i in range(1, 121)]

for ex in gym_ex:
    with st.expander(ex):
        show_timer(f"gym_{ex}") 
        st.divider()
        c_sets, c_copy = st.columns([1, 1.5])
        with c_sets:
            sets_count = st.number_input(f"Sets", 1, 10, 4, key=f"sets_{week}_{day}_{ex}", disabled=not can_edit)
        with c_copy:
            st.write("") 
            if st.button("👯 Copy Set 1 to All", key=f"copy_{week}_{day}_{ex}", disabled=not can_edit, use_container_width=True):
                duplicate_set_one(week, day, day_date, ex, sets_count)
                st.rerun()

        h1, h2, h3 = st.columns([1, 2, 2])
        h1.caption("Set")
        h2.caption("Weight")
        h3.caption("Reps")

        for s in range(1, sets_count + 1):
            w_key, r_key = f"weight_{week}_{day}_{ex}_{s}", f"reps_{week}_{day}_{ex}_{s}"
            saved = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
            s_weight = saved["Weight"].iloc[0] if not saved.empty else 5.0
            s_reps = int(saved["Reps"].iloc[0]) if not saved.empty else 8
            
            if s_weight == 0.0: w_idx = 0
            else:
                try: w_idx = weight_options.index(float(s_weight))
                except: w_idx = 2 
            
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1: st.write(f"**{s}** {'✅' if not saved.empty else ''}")
            with c2:
                st.selectbox("W", weight_options, index=w_idx, key=w_key, disabled=not can_edit, label_visibility="collapsed", on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key))
            with c3:
                st.selectbox("R", list(range(0, 51)), index=s_reps, key=r_key, disabled=not can_edit, label_visibility="collapsed", on_change=on_data_change, args=(week, day, day_date, ex, s, w_key, r_key))

# ---------------- ABS SECTION ----------------
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
                    if st.button("💾", key=f"btn_{dur_key}", disabled=not can_edit, use_container_width=True):
                        df_s = load_data()
                        df_s = df_s[~((df_s["Week"]==week) & (df_s["Day"]==day) & (df_s["Exercise"]==ex) & (df_s["Set"]==set_num))]
                        new_r = pd.DataFrame([{"Week": week, "Day": day, "Date": day_date, "Exercise": ex, "Set": set_num, "Weight": 0.0, "Reps": st.session_state[reps_key], "Duration": st.session_state[dur_key]}])
                        save_data(pd.concat([df_s, new_r], ignore_index=True))
                        st.rerun()
            st.divider()

# ---------------- SUMMARY ----------------
st.subheader("📊 Summary")
summary_view = today_data[today_data["Exercise"] != "DAY MARKER"]
if not summary_view.empty:
    display_df = summary_view.sort_values(by=["Exercise", "Set"]).copy()
    def format_perf(r):
        if r['Weight'] > 0 and r['Reps'] > 0: return f"{r['Weight']} lb x {r['Reps']}"
        elif r['Weight'] == 0 and r['Duration'] == 0 and r['Reps'] > 0: return f"BW x {r['Reps']}"
        elif r['Weight'] == 0 and r['Duration'] > 0: return f"{r['Duration']}s | {r['Reps']}R"
        else: return "—"
    display_df["Performance"] = display_df.apply(format_perf, axis=1)
    st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)

if st.session_state["timer_running"]:
    time.sleep(1)
    st.rerun()
