from datetime import datetime


def format_log_entry(old_state, new_state):
    # Generate the current timestamp in the desired format
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    # Construct the log entry
    log_entry = f"{timestamp}: {old_state}->{new_state}"
    return log_entry
