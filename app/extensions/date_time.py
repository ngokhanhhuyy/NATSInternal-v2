import pytz
from datetime import datetime, date, timedelta
from app.config import Config

class Time:
    __timeZone = pytz.timezone(Config.TIME_ZONE)

    @classmethod
    def getCurrentDateTime(cls) -> datetime:
        currentDateTime = datetime.now()
        return currentDateTime.astimezone(cls.__timeZone)
    
    @classmethod
    def getCurrentDate(cls) -> date:
        currentDate = datetime.today()
        return currentDate.astimezone(cls.__timeZone)
    
    @classmethod
    def getTimeDeltaText(cls, dateTime1: datetime, dateTime2: datetime) -> str:
        timeDelta: timedelta = dateTime1.replace(tzinfo=None) - dateTime2.replace(tzinfo=None)
        if timeDelta < timedelta(minutes=1):
            return "Vừa xong"
        elif timeDelta < timedelta(hours=1):
            return f"{timeDelta.seconds // 60} phút"
        elif timeDelta < timedelta(days=1):
            return f"{timeDelta.seconds // 3600} giờ"
        elif timeDelta < timedelta(days=30):
            return f"{timeDelta.days} ngày"
        elif timeDelta < timedelta(days=365):
            return f"{timeDelta.days // 30} tháng"
        else:
            return f"{timeDelta.days // 365} năm"
        
    @classmethod
    def addTimeZoneToDateTime(cls, originalDateTime: datetime) -> datetime:
        newDateTime = datetime(
            tzinfo=Time.getCurrentDateTime().tzinfo,
            year=originalDateTime.year,
            month=originalDateTime.month,
            day=originalDateTime.day,
            hour=originalDateTime.hour,
            minute=originalDateTime.minute,
            second=originalDateTime.second,
        )
        return newDateTime