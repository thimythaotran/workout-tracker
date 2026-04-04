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

# ---------------- LOAD DATA (FIXED) ----------------
if os.path.exists(DATA_FILE):
    log_df = pd.read_csv(DATA_FILE)

    if not log_df.empty:
        log_df["Date"] = pd.to_datetime(
            log_df["Date"],
            errors="coerce"
        )

        # 🔥 REMOVE BAD DATE ROWS THAT BREAK STREAMLIT
        log_df = log_df[log_df["Date"].notna()]

else:
    log_df = pd.DataFrame(columns=[
        "Week","Day","Date","Exercise","Set","Weight","Duration"
    ])

# ---------------- APP HEADER ----------------
st.set_page_config(page_title="Workout Tracker", layout="centered")

st.markdown("### 🏋️‍♂️ Mobile Workout Tracker")

st.caption(
    f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# ---------------- PASSWORD ----------------
password = st.text_input("Enter password", type="password")
can_edit = password == EDIT_PASSWORD

if not can_edit:
    st.info("🔒 View mode")

# ---------------- SELECT WEEK/DAY ----------------
week = st.selectbox("Week",[1,2,3,4])
day = st.selectbox("Day",list(workout_plan.keys()))

# ---------------- DATE (REAL FIX) ----------------
existing_dates = log_df.loc[
    (log_df["Week"]==week)&
    (log_df["Day"]==day)&
    (log_df["Exercise"]=="DAY MARKER"),
    "Date"
]

default_date = (
    existing_dates.max().date()
    if not existing_dates.empty
    else date.today()
)

day_date = st.date_input(
    "Workout Date",
    value=default_date,
    key=f"date_{week}_{day}",
    disabled=not can_edit
)

# ---------------- SAVE DAY BUTTON (FIXED) ----------------
if st.button("💾 Save Day Date", disabled=not can_edit):

    # remove old marker
    log_df = log_df[
        ~((log_df["Week"]==week)&
          (log_df["Day"]==day)&
          (log_df["Exercise"]=="DAY MARKER"))
    ]

    log_df = pd.concat([
        log_df,
        pd.DataFrame({
            "Week":[week],
            "Day":[day],
            "Date":[pd.to_datetime(day_date)],
            "Exercise":["DAY MARKER"],
            "Set":[0],
            "Weight":[0],
            "Duration":[0]
        })
    ], ignore_index=True)

    log_df.to_csv(DATA_FILE,index=False)

    st.success("✅ Date saved permanently")

# ---------------- NORMAL EXERCISES ----------------
st.subheader(day)

for ex in workout_plan[day]:

    if ex in abs_exercises:
        continue

    with st.expander(ex):

        sets = st.number_input(
            "Sets",
            1,10,4,
            key=f"{week}_{day}_{ex}_sets",
            disabled=not can_edit
        )

        for s in range(1,sets+1):

            key=f"{week}_{day}_{ex}_{s}"

            prev = log_df.loc[
                (log_df["Week"]==week)&
                (log_df["Day"]==day)&
                (log_df["Exercise"]==ex)&
                (log_df["Set"]==s),
                "Weight"
            ]

            default_weight=float(prev.values[0]) if not prev.empty else 5.0

            weight=st.selectbox(
                f"Set {s} weight",
                [i*2.5 for i in range(2,41)],
                index=int(default_weight/2.5)-2,
                key=key,
                disabled=not can_edit
            )

            if st.button(f"Save {ex} Set {s}",
                         key=f"save_{key}",
                         disabled=not can_edit):

                log_df = log_df[
                    ~((log_df["Week"]==week)&
                      (log_df["Day"]==day)&
                      (log_df["Exercise"]==ex)&
                      (log_df["Set"]==s))
                ]

                log_df = pd.concat([
                    log_df,
                    pd.DataFrame({
                        "Week":[week],
                        "Day":[day],
                        "Date":[pd.to_datetime(day_date)],
                        "Exercise":[ex],
                        "Set":[s],
                        "Weight":[weight],
                        "Duration":[0]
                    })
                ],ignore_index=True)

                log_df.to_csv(DATA_FILE,index=False)
                st.success(f"Saved {ex} Set {s}")

# ---------------- ABS SECTION (UNCHANGED) ----------------
if any(ex in abs_exercises for ex in workout_plan[day]):

    with st.expander("💪 Abs Exercises"):

        for set_num in range(1,3):

            st.markdown(f"### Set {set_num}")

            for ex in workout_plan[day]:

                if ex not in abs_exercises:
                    continue

                col1,col2=st.columns([3,1])

                duration_key=f"{week}_{day}_{ex}_abs_{set_num}"

                with col1:
                    duration=st.selectbox(
                        ex,
                        list(range(1,61)),
                        index=29,
                        key=duration_key,
                        disabled=not can_edit
                    )

                with col2:
                    done=st.checkbox(
                        "Done",
                        key=f"{duration_key}_done",
                        disabled=not can_edit
                    )

                if done and can_edit:

                    log_df = log_df[
                        ~((log_df["Week"]==week)&
                          (log_df["Day"]==day)&
                          (log_df["Exercise"]==ex)&
                          (log_df["Set"]==set_num))
                    ]

                    log_df = pd.concat([
                        log_df,
                        pd.DataFrame({
                            "Week":[week],
                            "Day":[day],
                            "Date":[pd.to_datetime(day_date)],
                            "Exercise":[ex],
                            "Set":[set_num],
                            "Weight":[0],
                            "Duration":[duration]
                        })
                    ],ignore_index=True)

                    log_df.to_csv(DATA_FILE,index=False)

# ---------------- VIEW LOG ----------------
st.subheader("📊 Progress")

view=log_df[
    (log_df["Week"]==week)&
    (log_df["Day"]==day)
]

st.dataframe(view)