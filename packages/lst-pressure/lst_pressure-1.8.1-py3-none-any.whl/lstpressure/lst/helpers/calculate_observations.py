from ...observation import Observation
from ...lstindex import LSTIntervalType as I
import math
from typing import Tuple
from lstpressure.perf import track_total_runtime


def convert_to_hours(x):
    try:
        result = round(
            (int(x.split(":")[0]) * 3600 + int(x.split(":")[1]) * 60) / 3600, 2
        )
        return result
    except:
        return None


@track_total_runtime
def calculate_constraints(row) -> list[I]:
    constraints = []
    if row["night_obs"] == "Yes":
        constraints.append(I.NIGHT)
    elif row["avoid_sunrise_sunset"] == "Yes":
        constraints.append(I.SUNRISE_SUNSET)
        constraints.append(I.SUNSET_SUNRISE)
        constraints.append(I.DAY)

    # If neither night_obs nor avoid_sunrise_sunset was selected
    if not constraints:
        constraints.append(I.ALL_DAY)
        constraints.append(I.DAY)

    return constraints


@track_total_runtime
def split_dates(dict):
    if not len(dict.keys()):
        return None

    # Dictionary to store the start and end dates
    dates = {}

    # Iterate through the dictionary items
    for key, value in dict.items():
        # Check if the key ends with 'start_date' or 'end_date'
        if "start_date" in key or "end_date" in key:
            # Extract the base key by removing the suffix '_start_date' or '_end_date'
            base_key = key.replace("_start_date", "").replace("_end_date", "")
            if base_key not in dates:
                dates[base_key] = {}
            # Assign the value to the respective part of the tuple (start or end)
            if "start_date" in key:
                dates[base_key]["start"] = value
            elif "end_date" in key:
                dates[base_key]["end"] = value

    # Convert the dictionary to a list of tuples
    result = []
    for key in dates:
        if "start" in dates[key] and "end" in dates[key]:
            result.append((dates[key]["start"], dates[key]["end"]))

    return result


@track_total_runtime
def calc_tags(dict):
    if not len(dict.keys()):
        return None

    # 'tag' could be suffix for a number of fields. make sure we are only working with the intended field
    dict = {
        key: val for key, val in dict.items() if key == "tag" or key.startswith("tag_")
    }
    return [val for _, val in dict.items()]


@track_total_runtime
def wind_normalized_field(row, field):
    return {
        key: str(value)
        for key, value in row.items()
        if key.startswith(field) and str(value) != "nan"
    }


@track_total_runtime
def calculate_observations(dataFrame, observation_filter) -> Tuple[Observation]:
    try:
        # Convert durations to hours and round off
        dataFrame["duration_hours"] = dataFrame["simulated_duration"].apply(
            lambda x: round(0 if math.isnan(x) else x / 3600, 2)
        )

        # Convert LST start and end times to floating point hours
        dataFrame["lst_start_hours"] = dataFrame["lst_start"].apply(convert_to_hours)
        dataFrame["lst_end_hours"] = dataFrame["lst_start_end"].apply(convert_to_hours)

        # Build observations using list comprehension for efficiency
        observations = [
            Observation(
                id=row["id"],
                lst_window_start=row["lst_start_hours"],
                lst_window_end=row["lst_end_hours"],
                utc_constraints=constraint,
                duration=row["duration_hours"],
                tags=calc_tags(wind_normalized_field(row, "tag")),
                preferred_dates=split_dates(
                    wind_normalized_field(row, "preferred_dates")
                ),
                avoid_dates=split_dates(wind_normalized_field(row, "avoid_dates")),
                proposal_id=row["proposal_id"],
            )
            for _, row in dataFrame.iterrows()
            if row["lst_end_hours"] - row["lst_start_hours"] > 0
            for constraint in calculate_constraints(row)
        ]

        return tuple(filter(observation_filter, observations))
    except Exception as e:
        raise ValueError("Error parsing CSV - please check input.", e)
