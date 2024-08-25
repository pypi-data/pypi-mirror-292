from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from dateutil import parser

@dataclass
class RateListItem():
    RateID: str
    SignalType: str
    Description: str
    LastUpdated: Optional[str] = None

@dataclass
class ValueInfoItem:
    ValueName: str
    DateStart: str
    DateEnd: str
    DayStart: str
    DayEnd: str
    TimeStart: str
    TimeEnd: str
    value: float
    Unit: str

    def GetStart(self) -> datetime:
        """Get the start of this tariff as a python datetime"""
        return parser.parse(f"{self.DateStart} {self.TimeStart} -07:00")


    def GetEnd(self) -> datetime:
        """Get the end of this tariff as a python datetime"""
        return parser.parse(f"{self.DateEnd} {self.TimeEnd} -07:00")

@dataclass
class RateInfo:
    RateID: str
    SystemTime_UTC: str
    RateName: str
    RateType: str
    Sector: str
    API_Url: str
    RatePlan_Url: str
    EndUse: str
    AltRateName1: str
    AltRateName2: str
    SignupCloseDate: str
    ValueInformation: list[ValueInfoItem] = field(default_factory=list)
    """The list of tariffs"""

    def GetCurrentTariffs(self) -> list[ValueInfoItem]:
        """Gets all tariffs that are currently active"""
        
        # ValueInformation where getstart < now < getend
        now = datetime.now().timestamp()
        return list(filter(lambda t: t.GetStart().timestamp() < now and t.GetEnd().timestamp() > now, self.ValueInformation))