
def swap_item(item, max_duration):
    if not item:
        return None, None, 0
    start_time = item['it']
    end_time = item['ot']
    if start_time == 0 and end_time == -1:
        end_time = max_duration
    end_time = end_time if end_time <= max_duration else max_duration
    start_time = start_time / 1000
    end_time = end_time / 1000
    duration = end_time - start_time
    return start_time, end_time, duration
