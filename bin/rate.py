import datetime

class Rate:
    RATE_WEEKDAY = 0.1
    RATE_WEEKEND = 0.1
    FREE_TIME_WEEKDAY = 10
    FREE_TIME_WEEKEND = 10
    
    def is_today_weekend(self):
        return datetime.date.today().weekday() > 4
       
    def apply(self, today_used, duration):
        if self.is_today_weekend():
            rate = Rate.RATE_WEEKEND
            free_time = Rate.FREE_TIME_WEEKEND
        else:
            rate = Rate.RATE_WEEKDAY
            free_time = Rate.FREE_TIME_WEEKDAY

        free_time = free_time - today_used
        if free_time > 0 and free_time < duration:
            cost = (duration - free_time) * rate
        else:
            cost = 0
        return cost
