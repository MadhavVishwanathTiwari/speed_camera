import datetime

def get_speed(pixels, ftperpixel, secs):
    """Calculate speed from pixels and time."""
    return ((pixels * ftperpixel) / secs) * 0.681818 if secs > 0.0 else 0.0

def secs_diff(end_time, start_time):
    """Calculate elapsed seconds."""
    return (end_time - start_time).total_seconds()

def record_speed(res, csv_file):
    """Record speed in .csv format."""
    with open(csv_file, 'a') as f:
        f.write(res + "\n")
