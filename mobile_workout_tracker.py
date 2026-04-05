# VERSION: 2.08

# STATUS: Phase 3 - Optimized & Robust

# ––––––––––––––––––––––––––––––––

import streamlit as st
import pandas as pd
import os
import time
from datetime import date

# –––––––– SETTINGS ––––––––

DATA_FILE = “workout_log.csv”
VERSION = “2.08”

# Password: set env var WORKOUT_PASSWORD for deployment, falls back to “1” locally

EDIT_PASSWORD = os.environ.get(“WORKOUT_PASSWORD”, “1”)

REQUIRED_COLUMNS = [“Week”, “Day”, “Date”, “Exercise”, “Set”, “Weight”, “Reps”, “Duration”]

workout_plan = {
“Day 1”: [“Flat Bench Press”, “Incline Bench Press”, “Cable Flies”, “Cable Tricep Extensions”, “Skull Crushers”, “Dips”, “Push Ups”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 2”: [“Straight Bar Deadlift”, “Seated Rows”, “Lat Pull Downs”, “One Arm Dumbbell Rows”, “DB Bicep Curl”, “Hammer Curls”, “Concentration Curls”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 3”: [“Squat”, “Leg Extensions”, “Leg Curls”, “Calf Raises”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 4”: [“Shoulder Press”, “Lateral Raises”, “Front Raises”, “Shrugs”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 5”: [“Deadlift”, “Romanian Deadlift”, “Hamstring Curls”, “Calf Raises”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 6”: [“Chest Dips”, “Push-ups”, “Tricep Dips”, “Cable Flies”, “Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”],
“Day 7”: [“Abs Crunches”, “Plank”, “Leg Raises”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”]
}

ABS_MASTER_LIST = [“Leg Drops”, “Reverse Leg Crunches”, “Sit-Up Twists”, “Russian Twists”, “Mountain Climber Twists”, “Flutter Kicks”, “Abs Crunches”, “Plank”, “Leg Raises”]

# –––––––– DATA ENGINE ––––––––

def load_data():
if not os.path.exists(DATA_FILE):
return pd.DataFrame(columns=REQUIRED_COLUMNS)
try:
df = pd.read_csv(DATA_FILE)
for col in REQUIRED_COLUMNS:
if col not in df.columns:
df[col] = 0 if col in (“Weight”, “Reps”, “Duration”, “Set”, “Week”) else “”
df[“Date”] = pd.to_datetime(df[“Date”], errors=“coerce”).dt.date
df = df.dropna(subset=[“Week”, “Day”, “Exercise”])
return df
except Exception as e:
st.warning(“Could not load data: “ + str(e) + “. Starting fresh.”)
return pd.DataFrame(columns=REQUIRED_COLUMNS)

def save_data(df):
tmp = DATA_FILE + “.tmp”
try:
df.to_csv(tmp, index=False)
os.replace(tmp, DATA_FILE)
except Exception as e:
st.error(“Save failed: “ + str(e))

def invalidate_cache():
if “cached_df” in st.session_state:
del st.session_state[“cached_df”]

def get_data():
if “cached_df” not in st.session_state:
st.session_state[“cached_df”] = load_data()
return st.session_state[“cached_df”]

def upsert_row(week, day, date_val, exercise, set_num, weight_val, reps_val, duration_val=0):
df = load_data()
mask = (
(df[“Week”] == week) &
(df[“Day”] == day) &
(df[“Exercise”] == exercise) &
(df[“Set”] == set_num)
)
df = df[~mask]
new_row = pd.DataFrame([{
“Week”: week, “Day”: day, “Date”: date_val, “Exercise”: exercise,
“Set”: set_num, “Weight”: weight_val, “Reps”: reps_val, “Duration”: duration_val
}])
save_data(pd.concat([df, new_row], ignore_index=True))
invalidate_cache()

def ensure_day_marker(week, day, date_val):
df = get_data()
exists = not df[
(df[“Week”] == week) & (df[“Day”] == day) & (df[“Exercise”] == “DAY MARKER”)
].empty
if not exists:
upsert_row(week, day, date_val, “DAY MARKER”, 0, 0.0, 0, 0)

def on_data_change(week, day, date_val, exercise, set_num, weight_key, reps_key):
raw_weight = st.session_state[weight_key]
weight_val = 0.0 if raw_weight == “Bodyweight” else float(raw_weight)
reps_val = int(st.session_state[reps_key])
upsert_row(week, day, date_val, exercise, set_num, weight_val, reps_val)
ensure_day_marker(week, day, date_val)

def duplicate_set_one(week, day, date_val, exercise, total_sets):
w1_key = “weight_” + str(week) + “*” + day + “*” + exercise + “*1”
r1_key = “reps*” + str(week) + “*” + day + “*” + exercise + “*1”
if w1_key in st.session_state and r1_key in st.session_state:
raw_w = st.session_state[w1_key]
val_w = 0.0 if raw_w == “Bodyweight” else float(raw_w)
val_r = int(st.session_state[r1_key])
df = load_data()
mask = (df[“Week”] == week) & (df[“Day”] == day) & (df[“Exercise”] == exercise) & (df[“Set”] > 0)
df = df[~mask]
new_rows = []
for s in range(1, total_sets + 1):
new_rows.append({
“Week”: week, “Day”: day, “Date”: date_val, “Exercise”: exercise,
“Set”: s, “Weight”: val_w, “Reps”: val_r, “Duration”: 0
})
st.session_state[“weight*” + str(week) + “*” + day + “*” + exercise + “*” + str(s)] = raw_w
st.session_state[“reps*” + str(week) + “*” + day + “*” + exercise + “_” + str(s)] = val_r
save_data(pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True))
invalidate_cache()
ensure_day_marker(week, day, date_val)

# –––––––– TIMER ––––––––

def init_timer():
st.session_state.setdefault(“timer_start”, None)
st.session_state.setdefault(“timer_running”, False)
st.session_state.setdefault(“timer_last_tick”, 0.0)

def show_timer(key_suffix):
t_c1, t_c2 = st.columns([3, 1.2])
with t_c1:
elapsed = 0
if st.session_state[“timer_running”] and st.session_state[“timer_start”]:
elapsed = int(time.time() - st.session_state[“timer_start”])

```
    if elapsed < 60:
        color = "#28a745"
    elif elapsed < 90:
        color = "#ffc107"
    else:
        color = "#FF0000"

    timer_html = (
        "<div style='display:flex; align-items:baseline; gap:10px;'>"
        "<span style='color:" + color + "; font-size:55px; font-weight:bold; font-family:monospace;'>"
        + str(elapsed) + "s</span>"
        "<span style='color:#aaa; font-size:22px; font-weight:bold;'>Resting</span>"
        "</div>"
    )
    st.markdown(timer_html, unsafe_allow_html=True)

with t_c2:
    st.write("")
    if st.button("RESET", key="reset_" + key_suffix, use_container_width=True):
        st.session_state["timer_start"] = time.time()
        st.session_state["timer_running"] = True
        st.session_state["timer_last_tick"] = time.time()
        st.rerun()
```

# –––––––– APP UI ––––––––

st.set_page_config(page_title=“Workout Tracker”, layout=“centered”)
init_timer()

col_ref, col_ver = st.columns([1, 2])
with col_ref:
if st.button(“Refresh”):
invalidate_cache()
st.rerun()
with col_ver:
st.caption(“Ver: “ + VERSION)

password = st.text_input(“Enter password”, type=“password”)
can_edit = password == EDIT_PASSWORD

log_df = get_data()
c_w, c_d = st.columns(2)
with c_w:
week = st.selectbox(“Week”, [1, 2, 3, 4])
with c_d:
day = st.selectbox(“Day”, list(workout_plan.keys()))

saved_marker = log_df[
(log_df[“Week”] == week) & (log_df[“Day”] == day) & (log_df[“Exercise”] == “DAY MARKER”)
]
day_date = st.date_input(
“Workout Date”,
value=saved_marker.iloc[0][“Date”] if not saved_marker.empty else date.today(),
disabled=not can_edit
)

if can_edit:
ensure_day_marker(week, day, day_date)

st.divider()
today_data = log_df[(log_df[“Week”] == week) & (log_df[“Day”] == day)]
gym_ex = [e for e in workout_plan[day] if e not in ABS_MASTER_LIST]
abs_ex = [e for e in workout_plan[day] if e in ABS_MASTER_LIST]

# –––––––– GYM EXERCISES ––––––––

weight_options = [“Bodyweight”] + [float(i * 2.5) for i in range(1, 121)]

for ex in gym_ex:
with st.expander(ex):
show_timer(“gym_” + ex)
st.divider()
c_sets, c_copy = st.columns([1, 1.5])
with c_sets:
sets_count = st.number_input(“Sets”, 1, 10, 4, key=“sets_” + str(week) + “*” + day + “*” + ex, disabled=not can_edit)
with c_copy:
st.write(””)
if st.button(“Copy Set 1 to All”, key=“copy_” + str(week) + “*” + day + “*” + ex, disabled=not can_edit, use_container_width=True):
duplicate_set_one(week, day, day_date, ex, sets_count)
st.rerun()

```
    h1, h2, h3 = st.columns([1, 2, 2])
    h1.caption("Set")
    h2.caption("Weight")
    h3.caption("Reps")

    for s in range(1, sets_count + 1):
        w_key = "weight_" + str(week) + "_" + day + "_" + ex + "_" + str(s)
        r_key = "reps_" + str(week) + "_" + day + "_" + ex + "_" + str(s)
        saved = today_data[(today_data["Exercise"] == ex) & (today_data["Set"] == s)]
        s_weight = saved["Weight"].iloc[0] if not saved.empty else 5.0
        s_reps = int(saved["Reps"].iloc[0]) if not saved.empty else 8

        if s_weight == 0.0:
            w_idx = 0
        else:
            try:
                w_idx = weight_options.index(float(s_weight))
            except ValueError:
                w_idx = 2

        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            st.write("**" + str(s) + "** " + ("✅" if not saved.empty else ""))
        with c2:
            st.selectbox("W", weight_options, index=w_idx, key=w_key,
                         disabled=not can_edit, label_visibility="collapsed",
                         on_change=on_data_change,
                         args=(week, day, day_date, ex, s, w_key, r_key))
        with c3:
            st.selectbox("R", list(range(0, 51)), index=s_reps, key=r_key,
                         disabled=not can_edit, label_visibility="collapsed",
                         on_change=on_data_change,
                         args=(week, day, day_date, ex, s, w_key, r_key))
```

# –––––––– ABS SECTION (manual save - unchanged per spec) ––––––––

if abs_ex:
with st.expander(“Abs Section”, expanded=False):
for set_num in [1, 2]:
st.markdown(”#### SET “ + str(set_num))
for ex in abs_ex:
saved_abs = today_data[(today_data[“Exercise”] == ex) & (today_data[“Set”] == set_num)]
dur_key = “abs_dur_” + str(week) + “*” + day + “*” + ex + “*” + str(set_num)
reps_key = “abs_reps*” + str(week) + “*” + day + “*” + ex + “*” + str(set_num)
s_dur = int(saved_abs[“Duration”].iloc[0]) if not saved_abs.empty else 30
s_reps = int(saved_abs[“Reps”].iloc[0]) if not saved_abs.empty else 10
st.write(”**” + ex + “** “ + (“✅” if not saved_abs.empty else “”))
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
st.selectbox(“Secs”, list(range(0, 125, 5)), index=int(s_dur / 5), key=dur_key, disabled=not can_edit)
with c2:
st.selectbox(“Reps”, list(range(0, 51)), index=s_reps, key=reps_key, disabled=not can_edit)
with c3:
if st.button(“Save”, key=“btn*” + dur_key, disabled=not can_edit, use_container_width=True):
upsert_row(week, day, day_date, ex, set_num, 0.0,
st.session_state[reps_key], st.session_state[dur_key])
ensure_day_marker(week, day, day_date)
st.rerun()
st.divider()

# –––––––– SUMMARY ––––––––

st.subheader(“Summary”)
summary_data = load_data()
summary_view = summary_data[
(summary_data[“Week”] == week) &
(summary_data[“Day”] == day) &
(summary_data[“Exercise”] != “DAY MARKER”)
]
if not summary_view.empty:
display_df = summary_view.sort_values(by=[“Exercise”, “Set”]).copy()

```
def format_perf(r):
    if r["Weight"] > 0 and r["Reps"] > 0:
        return str(r["Weight"]) + " lb x " + str(r["Reps"])
    elif r["Weight"] == 0 and r["Duration"] == 0 and r["Reps"] > 0:
        return "BW x " + str(r["Reps"])
    elif r["Weight"] == 0 and r["Duration"] > 0:
        return str(r["Duration"]) + "s | " + str(r["Reps"]) + "R"
    return "-"

display_df["Performance"] = display_df.apply(format_perf, axis=1)
st.dataframe(display_df[["Exercise", "Set", "Performance"]], use_container_width=True, hide_index=True)
```

else:
st.caption(“No data logged yet for this day.”)

# –––––––– SMART TIMER TICK ––––––––

if st.session_state[“timer_running”]:
now = time.time()
if now - st.session_state.get(“timer_last_tick”, 0) >= 1.0:
st.session_state[“timer_last_tick”] = now
time.sleep(max(0, 1.0 - (now % 1)))
st.rerun()