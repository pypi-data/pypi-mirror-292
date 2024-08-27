from datetime import datetime, date, timedelta
import pytz
import dateparser
import re

# Ignore warnings.
import warnings

warnings.filterwarnings("ignore")


def format(dt: datetime | date | str, tz=None):
    if isinstance(dt, (datetime, date)):
        dt = dt.isoformat()
    elif isinstance(dt, str):
        dt = dt.strip()
        if dt == "tod":
            dt = "today"
        elif dt == "tom":
            dt = "tomorrow"
        elif dt == "yest":
            dt = "yesterday"
        elif dt in ["M", "Mo", "Mon"]:
            dt = "Monday"
        elif dt in ["T", "Tu", "Tue", "Tues"]:
            dt = "Tuesday"
        elif dt in ["W", "We", "Wed"]:
            dt = "Wednesday"
        elif dt in ["U", "Th", "Thu", "Thur", "Thurs"]:
            dt = "Thursday"
        elif dt in ["F", "Fr", "Fri"]:
            dt = "Friday"
        elif dt in ["S", "Sa", "Sat"]:
            dt = "Saturday"
        elif dt in ["Y", "Su", "Sun"]:
            dt = "Sunday"

    settings = {
        "RELATIVE_BASE": datetime.now(pytz.timezone(tz)) if tz else datetime.now(),
        "PREFER_DATES_FROM": "future",
    }

    if tz is not None:
        settings["TIMEZONE"] = str(tz)

    parsed_date = dateparser.parse(
        dt.strip(),
        settings=settings,
    )

    if tz is not None:
        # If a timezone is provided, ensure the parsed date is aware
        timezone = pytz.timezone(tz)
        if parsed_date.tzinfo is None:
            parsed_date = timezone.localize(parsed_date)
        else:
            parsed_date = parsed_date.astimezone(timezone)
    else:
        # If no timezone is provided, return a naive datetime
        parsed_date = parsed_date.replace(tzinfo=None)

    return parsed_date


def floor_date(time: datetime, mins: int):
    return time.replace(minute=time.minute - (time.minute % mins))


def ceil_date(time: datetime, mins: int):
    minute = time.minute + (time.minute % mins)

    if minute >= 60:
        return time.replace(minute=0, hour=time.hour + 1)
    else:
        return time.replace(minute=minute)


def round_timedelta(delta: timedelta, mins: int):
    sec_in_interval = 60 * mins
    rounded_duration_in_sec = int(
        sec_in_interval * round(delta.total_seconds() / sec_in_interval)
    )

    return timedelta(seconds=rounded_duration_in_sec)


def remove_timezone(time: datetime | date | str):
    if isinstance(time, datetime):
        return time.replace(tzinfo=None)
    elif isinstance(time, date):
        return datetime(year=time.year, month=time.month, day=time.day)
    elif isinstance(time, str):
        return format(time).replace(tzinfo=None)


def format_as_relative_time(time: datetime | date | str, days_from_threshold: int = 7):
    if isinstance(time, date):
        time = datetime(year=time.year, month=time.month, day=time.day)
    elif isinstance(time, str):
        time = format(time)

    days_from_now = (time.date() - datetime.now().date()).days

    if days_from_now == 0:
        date_component = "today"
    elif days_from_now == 1:
        date_component = "tomorrow"
    elif days_from_now == -1:
        date_component = "yesterday"
    elif days_from_now > 1 and days_from_now <= days_from_threshold:
        date_component = f"in {days_from_now} days"
    elif days_from_now < -1 and days_from_now >= -days_from_threshold:
        date_component = f"{-days_from_now} days ago"
    else:
        if time.year == datetime.now().year or abs(days_from_now) <= 90:
            date_component = time.strftime("%b %e")
        else:
            date_component = time.strftime("%b %e, %Y")

    if time.hour != 0 or time.minute != 0:
        time_component = time.strftime("%I:%M %p")
        time_component = time_component.lstrip("0")
        time_component = time_component.replace(":00 ", "")
        formatted_time = f"{date_component} at {time_component}"
    else:
        formatted_time = date_component

    # Remove double spaces.
    formatted_time = re.sub(r"\s{2,}", " ", date_component)

    return formatted_time


def is_all_day(time: datetime | date):
    return type(time) == date or (
        type(time) == datetime and (time.hour == 0 and time.minute == 0)
    )


def min_bound_time(time: datetime, min_time: datetime):
    if time.hour <= min_time.hour and time.minute <= min_time.minute:
        return time.replace(
            hour=min_time.hour, minute=min_time.minute, second=0, microsecond=0
        )
    else:
        return time


def max_bound_time(time: datetime, min_time: datetime):
    if time.hour >= min_time.hour and time.minute >= min_time.minute:
        return time.replace(
            hour=min_time.hour, minute=min_time.minute, second=0, microsecond=0
        )
    else:
        return time
