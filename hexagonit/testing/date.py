import datetime


def static_date(date):
    """Generates a modified ``datetime.date`` class with a static .today() method
    which returns the given ``date``, which must be an instance of
    ``datetime.date``.

    :param date: The static date that the `today()` will return.
    :type date: `datetime.date`

    :rtype: Modified `datetime.date`
    """
    if not isinstance(date, datetime.date):
        raise TypeError('The static date must be an instance of datetime.date.')

    class StaticToday(datetime.date):
        @classmethod
        def today(cls, *args, **kwargs):
            return date

    return StaticToday


def static_datetime(dt):
    """Generates a modified ``datetime.datetime`` class with a static .now()
    method which returns the given ``date`` which must be an instance of
    ``datetime.datetime``.

    :param dt: The static datetime that the `now()` method will return.
    :type dt: `datetime.datetime`

    :rtype: Modified `datetime.datetime`
    """
    if not isinstance(dt, datetime.datetime):
        raise TypeError('The static datetime must be an instance of datetime.datetime.')

    class StaticNow(datetime.datetime):
        @classmethod
        def now(cls, *args, **kwargs):
            return dt

    return StaticNow

__all__ = ['static_date', 'static_datetime']
