import re
from typing import List


class Point:
    _lat: float
    _lng: float
    _alt: float

    def __init__(self, lat: float, lng: float, alt: float = None):
        self._lat = lat
        self._lng = lng
        self._alt = alt

    def is_3d(self):
        return bool(self._alt)

    def __str__(self):
        return self.to_pair()

    def to_pair(self):
        pair = f"{self._stringify_float(self._lng)} {self._stringify_float(self._lat)}"
        if self.is_3d():
            pair = f"{pair} {self._stringify_float(self._alt)}"
        return pair

    @staticmethod
    def from_pair(pair: str) -> 'Point':
        pair = re.sub(r"[a-zA-Z\(\)]+", "", pair.strip())
        splits = pair.strip().split()
        lng, lat = splits[:2]
        alt = None
        if len(splits) > 2:
            alt = splits[2]
        return Point(lat=lat, lng=lng, alt=alt)

    @staticmethod
    def _stringify_float(num: float):
        return f"{num}".rstrip("0").rstrip(".")

    def to_wkt(self) -> str:
        wkt_type = "POINT"
        if self.is_3d():
            wkt_type = f"{wkt_type} Z"
        return f"{wkt_type}({str(self)})"

    def to_json(self) -> List[float]:
        output = [self._lng, self._lat]
        if self.is_3d():
            output.append(self._alt)
        return output
