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
from typing import List, Tuple

import requests
from sympy.geometry import Point, Line, Segment as GeoSegment
from tcxreader.tcxreader import TCXReader, TCXTrackPoint


def log_msg(msg: str) -> None:
    """Generic console logging with timestamp."""
    print(f'{datetime.datetime.now()}: {msg}', flush=True)


# Start of the actual algorithm


def track_point_to_point(trackpoint: TCXTrackPoint) -> Point:
    """As an approximation for small distances,
    we assume latitude and longitude to be a Euclidean space.
    Very close to the earth's poles, this would not be ok."""
    return Point(trackpoint.longitude, trackpoint.latitude)


def closest_point_on_step(step_start: TCXTrackPoint,
                          step_end: TCXTrackPoint,
                          point: Point) -> TCXTrackPoint:
    """Find the closest point on a step (line segment) and interpolate the timestamp."""
    step = GeoSegment(track_point_to_point(step_start), track_point_to_point(step_end))
    distance_to_step = step.distance(point)
    distance_to_step_start = step.p1.distance(point)
    distance_to_step_end = step.p2.distance(point)
    if distance_to_step >= min(distance_to_step_start, distance_to_step_end):
        return step_start if distance_to_step_start < distance_to_step_end else step_end

    # Find orthogonal projection of the point onto the step.
    projection = Line(step.p1, step.p2).projection(point)
    step_fraction = float(projection.distance(point) / step.length)
    step_duration_s = (step_end.time - step_start.time).total_seconds()
    dt_s = step_fraction * step_duration_s
    exact_time = step_start.time + datetime.timedelta(seconds=dt_s)
    return TCXTrackPoint(
        longitude=float(projection.x),
        latitude=float(projection.y),
        time=exact_time)


def closest_virtual_trackpoint(point: Point, trackpoints: List[TCXTrackPoint]) -> TCXTrackPoint:
    """Find the closest trackpoints (potentially interpolated) on a polygon chain of trackpoints."""
    if len(trackpoints) == 1:
        return trackpoints[0]
    candidates = [closest_point_on_step(tp1, tp2, point)
                  for tp1, tp2 in zip(trackpoints, trackpoints[1:])]
    return min(map(lambda tp: (track_point_to_point(tp).distance(point), tp), candidates))[1]


def calc_effort_time(segment: GeoSegment,
                     points_close_to_start: List[TCXTrackPoint],
                     points_close_to_end: List[TCXTrackPoint]) -> float:
    """Return the precise effort time."""
    start = closest_virtual_trackpoint(segment.p1, points_close_to_start)
    end = closest_virtual_trackpoint(segment.p2, points_close_to_end)
    return float((end.time - start.time).total_seconds())


def with_surrounding_trackpoints(
        trackpoints: List[TCXTrackPoint],
        center_idx: int) -> List[TCXTrackPoint]:
    """Get trackpoint surrounding a center one."""
    all_idxs = [center_idx - 2, center_idx - 1, center_idx, center_idx + 1, center_idx + 2]
    valid_idxs = sorted(list(set((filter(lambda idx: 0 <= idx < len(trackpoints), all_idxs)))))
    return [trackpoints[idx] for idx in valid_idxs]


# Auxiliary things


def is_trackpoint_close_to_point(trackpoint: TCXTrackPoint, point: Point) -> bool:
    """For performance, we simply compare latitude and longitude.
    An actual implementation would do probably something
    that also works on the earth's poles."""
    return bool(
        float(point.y) - 0.0005 <= trackpoint.latitude <= float(point.y) + 0.0005 and
        float(point.x) - 0.0005 <= trackpoint.longitude <= float(point.x) + 0.0005)


def find_indexes_of_trackpoints_closest_to_segment_start_or_and(
        segment: GeoSegment, trackpoints: List[TCXTrackPoint]) -> Tuple[int, int]:
    """
    This could be the replaced by any other (probably already existing) way
    of finding the closest trackpoints.
    """
    invalid_idx = -1
    invalid_distance = 99999999.9
    start_idx_dist: Tuple[int, float] = invalid_idx, invalid_distance
    end_idx_dist: Tuple[int, float] = invalid_idx, invalid_distance
    for point_idx, trackpoint in enumerate(trackpoints):

        # Find start of effort first.
        if is_trackpoint_close_to_point(trackpoints[point_idx], segment.p1):
            start_dist = track_point_to_point(trackpoint).distance(segment.p1)
            if start_idx_dist[0] == invalid_idx or \
                    start_dist < start_idx_dist[1] or \
                    (trackpoint.time - trackpoints[start_idx_dist[0]].time).total_seconds() > 100:
                start_idx_dist = point_idx, start_dist

        # Only consider potential end points if they came after a start point.
        if start_idx_dist[0] != invalid_idx:
            if is_trackpoint_close_to_point(trackpoints[point_idx], segment.p2):
                end_dist = track_point_to_point(trackpoint).distance(segment.p2)
                if not end_idx_dist or end_dist < end_idx_dist[1]:
                    end_idx_dist = point_idx, end_dist

    if not start_idx_dist:
        raise RuntimeError("Did not find a suitable segment start point in the activity.")
    if not end_idx_dist:
        raise RuntimeError("Did not find a suitable segment end point in the acticity.")
    return start_idx_dist[0], end_idx_dist[0]


def calculate_effort_time(activity_tcx_path: str, segment: GeoSegment) -> None:
    """Calculate the effort time of an activity on a specific segment."""
    tcx_reader = TCXReader()
    activity = tcx_reader.read(activity_tcx_path)
    log_msg(f'Analyzing activity: {activity_tcx_path}')

    trackpoints: List[TCXTrackPoint] = activity.trackpoints

    start_idx, end_idx = \
        find_indexes_of_trackpoints_closest_to_segment_start_or_and(segment, trackpoints)

    segment_time = calc_effort_time(
        segment,
        with_surrounding_trackpoints(trackpoints, start_idx),
        with_surrounding_trackpoints(trackpoints, end_idx))

    log_msg(f'Segment time: {segment_time=:0.1f}')


def get_segment(access_token: str, segment_id: int) -> GeoSegment:
    """Download segment data using the Strava API"""

    # Hardcoded segment IDs, so one does not always need a valid access token.
    if segment_id == 4391619:  # Marienfeld Climb
        return GeoSegment(Point(7.436902, 50.884516), Point(7.441928, 50.883243))

    log_msg(f'Loading data for segment: {segment_id}')
    url = f'https://www.strava.com/api/v3/segments/{segment_id}'
    response = requests.get(url,
                            headers={'Authorization': f'Bearer {access_token}'},
                            timeout=10
                            ).json()
    log_msg(response)
    start_lat, start_lng = response['start_latlng']
    end_lat, end_lng = response['end_latlng']
    name = response['name']
    log_msg(f'Loaded segment: {name}')
    return GeoSegment(Point(start_lng, start_lat), Point(end_lng, end_lat))


def main() -> None:
    """Parse command line and run calculation."""
    parser = argparse.ArgumentParser('AccurateTimingOfStravaSegments')
    parser.add_argument('-a', '--activity_tcx_file',
                        help='Use Sauce for Strava™ to export TCX files.')
    parser.add_argument('-s', '--segment_id', type=int,
                        help='Can be copied from the URL in the browser.')
    parser.add_argument('-t', '--access_token',
                        help='See: https://developers.strava.com/docs/authentication/')
    args = parser.parse_args()
    calculate_effort_time(args.activity_tcx_file, get_segment(args.access_token, args.segment_id))


if __name__ == '__main__':
    main()
