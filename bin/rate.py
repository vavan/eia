import datetime

class RateSpec:
    def __init__(self, rate, free, max):
        self.rate = rate
        self.free = free
        self.max = max


class Rate:
    WEEKDAY = RateSpec(0.1, 0, 60)
    WEEKEND = RateSpec(0.1, 0, 60)
    
    def is_today_weekend(self):
        return datetime.date.today().weekday() > 4
       
    def apply(self, today_used, duration):
        if self.is_today_weekend():
            rate = Rate.WEEKDAY
        else:
            rate = Rate.WEEKEND

        total_time = today_used + duration
        if total_time < rate.max:
            free_time = rate.free - today_used
            if free_time > 0 and free_time < duration:
                cost = (duration - free_time) * rate.rate
            else:
                cost = 0
            return cost
        else:
            return None
