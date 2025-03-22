from datetime import datetime
import json

class ScheduleProcessor:
    def __init__(self, json_data):
        self.s = 6.879  # square w:h
        self.x = 25.982  # x point where the table starts
        self.ss = 1.587  # Distance between 15 minutes
        self.end = 191.341  # x point where the table ends
        self.y = {
            'offduty': 115.75203333,
            'sleeperberth': 122.6312,
            'driving': 127.23733125,
            'onduty': 134.11702708
        }
        self.json_data = json.loads(json_data) if isinstance(json_data, str) else json_data
        self.draw_cordinate = {}

    def round_to_quarter_hour(self, time):
        """Round minute to the nearest quarter hour."""
        minute = time.minute
        if minute < 7.5:
            new_minute = 0
        elif minute < 22.5:
            new_minute = 15
        elif minute < 37.5:
            new_minute = 30
        elif minute < 52.5:
            new_minute = 45
        else:
            new_minute = 0
            time = time.replace(hour=(time.hour + 1) % 24)
        return time.replace(minute=new_minute, second=0, microsecond=0)

    def calculate_cordinate(self, time):
        """Calculate x coordinate based on time."""
        return self.x + (self.s * time.hour) + (time.minute / 15 * self.ss) + 0.5

    def process_schedule(self):
        first = True
        page_count = 1
        page_list = []
        for entry in self.json_data['schedule']:
            start_time = datetime.strptime(entry["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(entry["end_time"], "%Y-%m-%d %H:%M:%S")
            start_time = self.round_to_quarter_hour(start_time)
            end_time = self.round_to_quarter_hour(end_time)
            start_calculate_cordinate = self.calculate_cordinate(start_time)
            end_calculate_cordinate = self.calculate_cordinate(end_time)
            mode_key = entry['mode'].replace(" ", "").lower().split("(")[0]
            if mode_key not in self.y:
                print(f"Warning: Mode '{mode_key}' not found in y dictionary. Skipping entry.")
                continue

            if (start_time.minute == 30 or start_time.minute == 0):
                if first:
                    page_list.extend([[self.x, self.y["sleeperberth"]], [start_calculate_cordinate, self.y["sleeperberth"]], [start_calculate_cordinate, self.y[mode_key]]])
                    first = False
                elif (end_time.day != start_time.day):
                    page_list.extend([[start_calculate_cordinate, self.y[mode_key]], [self.end, self.y[mode_key]]])
                    first = True
                    self.draw_cordinate[f'page_{page_count}'] = page_list
                    page_list = []
                    page_count += 1
                    continue
                page_list.extend([[start_calculate_cordinate, self.y[mode_key]], [end_calculate_cordinate, self.y[mode_key]]])
            else:
                if first:
                    page_list.extend([[self.x, self.y["sleeperberth"]], [start_calculate_cordinate, self.y["sleeperberth"]], [start_calculate_cordinate, self.y[mode_key]]])
                    first = False
                elif (end_time.day != start_time.day):
                    page_list.extend([[start_calculate_cordinate, self.y[mode_key]], [self.end, self.y[mode_key]]])
                    first = True
                    self.draw_cordinate[f'page_{page_count}'] = page_list
                    page_list = []
                    page_count += 1
                    continue
                page_list.extend([[start_calculate_cordinate, self.y[mode_key]], [end_calculate_cordinate, self.y[mode_key]]])


        if page_list:  # Eğer page_list boş değilse
            self.draw_cordinate[f'page_{page_count}'] = page_list
            
        return self.draw_cordinate

def get_cordinates(json_data):
    processor = ScheduleProcessor(json_data)
    return processor.process_schedule()