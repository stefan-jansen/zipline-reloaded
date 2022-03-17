from datetime import timedelta

from dateutil.relativedelta import MO
from pandas import DateOffset, Timestamp
from pandas.tseries.holiday import Holiday, sunday_to_monday

from .common_holidays import new_years_day
from .exchange_calendar import SUNDAY


def sunday_to_tuesday(dt):
    """
    If holiday falls on Sunday, use Tuesday instead.
    """
    if dt.weekday() == SUNDAY:
        return dt + timedelta(2)
    return dt


def sunday_to_wednesday(dt):
    """
    If holiday falls on Sunday, use Wednesday instead.
    """
    if dt.weekday() == SUNDAY:
        return dt + timedelta(3)
    return dt


NewYearsHolidayJan1 = new_years_day()

NewYearsHolidayJan2 = Holiday(
    "New Year's Holiday (Jan 2)",
    month=1,
    day=2,
)
NewYearsHolidayJan3 = Holiday(
    "New Year's Holiday (Jan 3)",
    month=1,
    day=3,
)

# https://en.wikipedia.org/wiki/Coming_of_Age_Day
ComingOfAgeDayThrough1999 = Holiday(
    "Coming of Age Day (through 1999)",
    month=1,
    day=15,
    start_date="1948-01-01",
    end_date="2000-01-01",
    observance=sunday_to_monday,
)
ComingOfAgeDay2000Onwards = Holiday(
    "Coming of Age Day (2000 onwards)",
    month=1,
    day=1,
    offset=DateOffset(weekday=MO(2)),
    start_date="2000-01-01",
)

NationalFoundationDay = Holiday(
    "National Foundation Day",
    month=2,
    day=11,
    observance=sunday_to_monday,
)

# The dates on which the vernal/autumnal equinox will be observed
# are announced on the first weekday of February of the previous
# year, so we treat them as ad-hoc holidays, even though they
# occur every year. For more info, see:
# https://en.wikipedia.org/wiki/Public_holidays_in_Japan#cite_note-3
# See:
# https://www.timeanddate.com/holidays/japan/
# https://www.timeanddate.com/holidays/japan/spring-equinox
VernalEquinoxes = [
    Timestamp("1997-03-20"),
    Timestamp("1998-03-21"),
    Timestamp("1999-03-22"),
    Timestamp("2000-03-20"),
    Timestamp("2001-03-20"),
    Timestamp("2002-03-21"),
    Timestamp("2003-03-21"),
    Timestamp("2004-03-20"),
    Timestamp("2005-03-21"),
    Timestamp("2006-03-21"),
    Timestamp("2007-03-21"),
    Timestamp("2008-03-20"),
    Timestamp("2009-03-20"),
    Timestamp("2010-03-22"),
    Timestamp("2011-03-21"),
    Timestamp("2012-03-20"),
    Timestamp("2013-03-20"),
    Timestamp("2014-03-21"),
    Timestamp("2015-03-21"),
    Timestamp("2016-03-21"),
    Timestamp("2017-03-20"),
    Timestamp("2018-03-21"),
    Timestamp("2019-03-21"),
    Timestamp("2020-03-20"),
    Timestamp("2021-03-20"),
]

# The Golden Week holidays (late April - early May) are listed in reverse
# chronological order because earlier holidays must be aware of later holidays
# so that that if an earlier holiday (Constitution Memorial Day, Greenery Day)
# falls on a Sunday, that holiday can be observed on the next non-holiday
# weekday.
# Clash with GreeneryDay and ConstitutionMemorialDay
ChildrensDay = Holiday(
    "Children's Day",
    month=5,
    day=5,
    observance=sunday_to_monday,
)

# From 1986-2006, the day between Constitution Memorial Day and Children's
# Day was an unnamed citizen's holiday because it was between two holidays.
# In 2007, Greenery Day was moved from April 29 to May 4, replacing the
# unnamed citizen's holiday. For more info, see:
# https://en.wikipedia.org/wiki/Golden_Week_(Japan)
# Clash with ChildrensDay and ConstitutionMemorialDay
GreeneryDay2007Onwards = Holiday(
    "Greenery Day",
    month=5,
    day=4,
    start_date="2007-01-01",
    observance=sunday_to_tuesday,
)

CitizensHolidayGoldenWeek = Holiday(
    "Citizen's Holiday Golden Week",
    month=5,
    day=4,
    end_date="2007-01-01",
    observance=sunday_to_monday,
)

# In 2007, April 29 was changed from Greenery Day to Showa Day,
# and Greenery Day was moved to May 4.
GreeneryDayThrough2006 = Holiday(
    "Greenery Day",
    month=4,
    day=29,
    end_date="2007-01-01",
    observance=sunday_to_monday,
)

ShowaDay = Holiday(
    "Showa Day",
    month=4,
    day=29,
    start_date="2007-01-01",
    observance=sunday_to_monday,
)

# Clash with ChildrensDay
ConstitutionMemorialDay = Holiday(
    "Constitution Memorial Day",
    month=5,
    day=3,
    observance=sunday_to_wednesday,
)

MarineDayThrough2002 = Holiday(
    "Marine Day (through 2002)",
    month=7,
    day=20,
    end_date="2003-01-01",
    observance=sunday_to_monday,
)

MarineDay2003OnwardsThrough2019 = Holiday(
    "Marine Day (2003 - 2019)",
    month=7,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2003-01-01",
    end_date="2020-01-01",
)

# Changed due to Tokyo Olympics
MarineDay2020 = Holiday(
    "Marine Day (2020)",
    month=7,
    day=23,
    year=2020,
)

MarineDay2021 = Holiday(
    "Marine Day (2021)",
    month=7,
    day=22,
    year=2021,
)

MarineDay2022Onwards = Holiday(
    "Marine Day (2022 onwards)",
    month=7,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2022-01-01",
)

MountainDayThrough2019 = Holiday(
    "Mountain Day (through 2019)",
    month=8,
    day=11,
    start_date="2016-01-01",
    end_date="2020-01-01",
    observance=sunday_to_monday,
)

# Changed due to Tokyo Olympics
MountainDay2020 = Holiday(
    "Mountain Day (2020)",
    month=8,
    day=10,
    year=2020,
)

MountainDay2021 = Holiday(
    "Mountain Day (2021)",
    month=8,
    day=9,
    year=2021,
)

MountainDay2022Onwards = Holiday(
    "Mountain Day (2022 onwards)",
    month=8,
    day=11,
    start_date="2022-01-01",
    observance=sunday_to_monday,
)

# See note on equinoxes above VernalEquinoxes
AutumnalEquinoxes = [
    Timestamp("1997-09-23"),
    Timestamp("1998-09-23"),
    Timestamp("1999-09-23"),
    Timestamp("2000-09-23"),
    Timestamp("2001-09-24"),
    Timestamp("2002-09-23"),
    Timestamp("2003-09-23"),
    Timestamp("2004-09-23"),
    Timestamp("2005-09-23"),
    Timestamp("2006-09-23"),
    Timestamp("2007-09-24"),
    Timestamp("2008-09-23"),
    Timestamp("2009-09-23"),
    Timestamp("2010-09-23"),
    Timestamp("2011-09-23"),
    Timestamp("2012-09-22"),
    Timestamp("2013-09-23"),
    Timestamp("2014-09-23"),
    Timestamp("2015-09-23"),
    Timestamp("2016-09-22"),
    Timestamp("2017-09-23"),
    Timestamp("2018-09-24"),
    Timestamp("2019-09-23"),
    Timestamp("2020-09-22"),
    Timestamp("2021-09-23"),
]

# If the Autumnal Equinox falls on a Wednesday, the Tuesday before
# it is a holiday because it will be sandwiched between Respect for
# the Aged Day and the Autumnal Equinox. For more info, see:
# https://en.wikipedia.org/wiki/Silver_Week
CitizensHolidaySilverWeek = [
    Timestamp("2009-09-22"),
    Timestamp("2015-09-22"),
]

RespectForTheAgedDayThrough2002 = Holiday(
    "Respect for the Aged Day (through 2002)",
    month=9,
    day=15,
    end_date="2003-01-01",
    observance=sunday_to_monday,
)

RespectForTheAgedDay2003Onwards = Holiday(
    "Respect for the Aged Day (2003 onwards)",
    month=9,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2003-01-01",
)

# https://en.wikipedia.org/wiki/Health_and_Sports_Day
HealthAndSportsDayThrough1999 = Holiday(
    "Heakth and Sports Day (through 1999)",
    month=10,
    day=10,
    start_date="1966-01-01",
    end_date="2000-01-01",
    observance=sunday_to_monday,
)

HealthAndSportsDay2000OnwardsThrough2019 = Holiday(
    "Health and Sports Day (2000 - 2019)",
    month=10,
    day=1,
    offset=DateOffset(weekday=MO(2)),
    start_date="2000-01-01",
    end_date="2020-01-01",
)

# Changed due to Tokyo Olympics
HealthAndSportsDay2020 = Holiday(
    "Health and Sports Day (2020)",
    month=7,
    day=24,
    year=2020,
)

HealthAndSportsDay2021 = Holiday(
    "Health and Sports Day (2021)",
    month=7,
    day=23,
    year=2021,
)

HealthAndSportsDay2022Onwards = Holiday(
    "Health and Sports Day (2022 onwards)",
    month=10,
    day=1,
    offset=DateOffset(weekday=MO(2)),
    start_date="2022-01-01",
)

CultureDay = Holiday(
    "Culture Day",
    month=11,
    day=3,
    observance=sunday_to_monday,
)

LaborThanksgivingDay = Holiday(
    "Labor Thanksgiving Day",
    month=11,
    day=23,
    observance=sunday_to_monday,
)

# Emperor Akihito is due to retire on 30 April 2019, meaning the holiday
# will not be observed in 2019, and its next celebration will be on the
# birthday of Crown Prince Naruhito (23 February 2020).
EmperorAkihitoBirthday = Holiday(
    "Emperor Akihito's Birthday",
    month=12,
    day=23,
    end_date="2019-04-30",
    observance=sunday_to_monday,
)

EmperorNaruhitoBirthday = Holiday(
    "Emperor Naruhito's Birthday",
    month=2,
    day=23,
    start_date="2019-04-30",
    observance=sunday_to_monday,
)

NewYearsHolidayDec31 = Holiday(
    "New Year's Holiday (Dec 31)",
    month=12,
    day=31,
)

Misc2019Holidays = [
    Timestamp("2019-04-30"),  # Abdication Day
    Timestamp("2019-05-01"),  # Accession Day
    Timestamp("2019-05-02"),  # Citizen's Holiday
    Timestamp("2019-10-22"),  # Enthronement Ceremony
]

EquityTradingSystemFailure = [
    # https://www.jpx.co.jp/english/corporate/news/news-releases/0060/20201019-01.html
    Timestamp("2020-10-01"),
]
