from dateutil.parser import parse


class Util:
    @staticmethod
    def get_jst_timestamp_from_yyyymmdd(yyyymmdd: str) -> int:
        date = parse(f"{yyyymmdd} 00:00:00+09:00", default=parse("00:00Z"))
        return int(date.timestamp() * 1000)
