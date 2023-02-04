#!/usr/bin/env python3

"""
Accurate timing of Strava segments
"""

__author__ = "Tobias Hermann"
__copyright__ = "Copyright 2023, Tobias Hermann"
__license__ = "MIT"
__email__ = "editgym@gmail.com"

import argparse
import datetime
from typing import List, Optional, Any

import requests
from sympy import *
from sympy.geometry import *
from tcxreader.tcxreader import TCXReader, TCXTrackPoint


def log(msg: str) -> None:
    print(f'{datetime.datetime.now()}: {msg}', flush=True)


def get_segment(access_token: str, segment_id: int) -> Segment:
    if segment_id == 4391619:
        return Segment(Point(7.436902, 50.884516), Point(7.441928, 50.883243))
    log(f'Loading data for segment: {segment_id}')
    url = f'https://www.strava.com/api/v3/segments/{segment_id}'
    r = requests.get(url, headers={'Authorization': f'Bearer {access_token}'}).json()
    log(r)
    start_lat, start_lng = r['start_latlng']
    end_lat, end_lng = r['end_latlng']
    name = r['name']
    log(f'Loaded segment: {name}')
    return Segment(Point(start_lng, start_lat), Point(end_lng, end_lat))


def track_point_to_point(tp: TCXTrackPoint) -> Point:
    # As an approximation for small distances, we assume latitude and longitude to be a Euclidean space.
    # Close to the earth's poles, this would not be ok.
    return Point(tp.longitude, tp.latitude)


def point_to_track_point(p: Point, t: Any) -> TCXTrackPoint:
    return TCXTrackPoint(longitude=float(p.x), latitude=float(p.y), time=t)


def check_passed_point(step: Segment, p: Point) -> bool:
    # todo: For the segment creator, or for start/end points on a curve,
    #       the start point might be an exact match.
    #       Maybe consider processing two steps at a time.
    return step.distance(p) < min(step.p1.distance(p), step.p2.distance(p))


def interpolate(step: Segment,
                step_t1: datetime.datetime,
                step_t2: datetime.datetime,
                p: Point) -> Optional[TCXTrackPoint]:
    start_projection = Line(step.p1, step.p2).projection(p)
    start_step_fraction = float(start_projection.distance(p) / step.length)
    step_duration_s = (step_t2 - step_t1).total_seconds()
    dt_s = start_step_fraction * step_duration_s
    exact_time = step_t1 + datetime.timedelta(seconds=dt_s)
    return point_to_track_point(start_projection, exact_time)


def are_close(tp: TCXTrackPoint, p: Point) -> bool:
    return \
        p.y - 0.001 <= tp.latitude <= p.y + 0.001 and \
        p.x - 0.001 <= tp.longitude <= p.x + 0.001


def calc_time(segment: Segment, activity: List[TCXTrackPoint]) -> List[float]:
    start: Optional[TCXTrackPoint] = None
    end: Optional[TCXTrackPoint] = None
    result: List[float] = []
    for point_idx in range(len(activity[:-1])):
        ap1 = activity[point_idx]
        if not are_close(ap1, segment.p1) and not are_close(ap1, segment.p2):
            continue
        step_p1 = track_point_to_point(ap1)
        ap2 = activity[point_idx + 1]
        step_p2 = track_point_to_point(ap2)
        step = Segment(step_p1, step_p2)
        if check_passed_point(step, segment.p1):
            start = interpolate(step, ap1.time, ap2.time, segment.p1)
        if start:
            if check_passed_point(step, segment.p2):
                end = interpolate(step, ap1.time, ap2.time, segment.p2)
        if start and end:
            result.append((end.time - start.time).total_seconds())
            start = None
            end = None
    return result


def segment_time(activity_tcx_path: str, segment: Segment):
    tcx_reader = TCXReader()
    activity = tcx_reader.read(activity_tcx_path)
    log(f'Analyzing activity: {activity_tcx_path}')
    t = calc_time(segment, activity.trackpoints)  # type: ignore
    log(f'Segment times: {t=}')


def main() -> None:
    parser = argparse.ArgumentParser('AccurateTimingOfStravaSegments')
    parser.add_argument('-a', '--activity_tcx_file', help='Use Sauce for Strava™ to export TCX files.')
    parser.add_argument('-s', '--segment_id', type=int, help='Can be copied from the URL in the browser.')
    parser.add_argument('-t', '--access_token', help='See: https://developers.strava.com/docs/authentication/')
    args = parser.parse_args()
    segment_time(args.activity_tcx_file, get_segment(args.access_token, args.segment_id))


if __name__ == '__main__':
    main()