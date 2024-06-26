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

import geopy.distance
import requests
from sympy.geometry import Point, Line, Segment as GeoSegment
from tcxreader.tcxreader import TCXReader, TCXTrackPoint


def log_msg(msg: str) -> None:
    """Generic console logging with timestamp."""
    print(f'{datetime.datetime.now()}: {msg}', flush=True)


# Start of the actual algorithm


def track_point_to_point(trackpoint: TCXTrackPoint) -> Point:
    """Point(longitude, latitude)."""
    return Point(trackpoint.longitude, trackpoint.latitude)


def geo_projection(line: GeoSegment, point: Point) -> Point:
    """Orthogonal projection for geo coordinates."""
    line_center: Point = (line.p1 + line.p2) / 2
    # If the line goes exactly through one of earth's poles, the numbers explode.
    x_scale = distance(line_center, Point(line_center.x + 0.1, line_center.y)) * 10
    y_scale = distance(line_center, Point(line_center.x, line_center.y + 0.1)) * 10
    euclidean_line = Line(Point(line.p1.x / x_scale, line.p1.y / y_scale),
                          Point(line.p2.x / x_scale, line.p2.y / y_scale))
    euclidean_point = Point(point.x / x_scale, point.y / y_scale)
    euclidean_projection = euclidean_line.projection(euclidean_point)
    projection = Point(euclidean_projection.x * x_scale, euclidean_projection.y * y_scale)
    return projection


def closest_point_on_step(step_start: TCXTrackPoint,
                          step_end: TCXTrackPoint,
                          point: Point) -> TCXTrackPoint:
    """Find the closest point on a step (line segment) and interpolate the timestamp."""
    step = GeoSegment(track_point_to_point(step_start), track_point_to_point(step_end))

    step_length = distance(step.p1, step.p2)
    distance_to_step_start = distance(step.p1, point)
    distance_to_step_end = distance(step.p2, point)

    # Find the orthogonal projection
    projection = geo_projection(step, point)

    projection_is_outside_step = \
        distance(step.p1, projection) > step_length or \
        distance(step.p2, projection) > step_length
    if projection_is_outside_step:
        return step_start if distance_to_step_start < distance_to_step_end else step_end

    step_duration_s = (step_end.time - step_start.time).total_seconds()
    step_fraction = float(distance(step.p1, projection) / step_length)
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
    return min(map(lambda tp: (distance(track_point_to_point(tp), point), tp), candidates))[1]


def calc_effort_time(segment: GeoSegment,
                     trackpoints: List[TCXTrackPoint],
                     start_idx: int,
                     end_idx: int) -> float:
    """Return the precise effort time."""
    points_close_to_start = with_surrounding_trackpoints(trackpoints, start_idx)
    points_close_to_end = with_surrounding_trackpoints(trackpoints, end_idx)
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


def distance(point1: Point, point2: Point) -> float:
    """Distance in meters between two geo coordinates"""
    return float(geopy.distance.geodesic((point1.y, point1.x), (point2.y, point2.x)).m)


def find_indexes_of_trackpoints_closest_to_first_effort_start_and_end(
        segment: GeoSegment, trackpoints: List[TCXTrackPoint]) -> Tuple[int, int]:
    """
    This could be the replaced by any other (probably already existing) way
    of finding the closest trackpoints.
    """
    invalid_idx = -1
    invalid_distance = 99999999.9
    start_idx_dist: Tuple[int, float] = invalid_idx, invalid_distance
    end_idx_dist: Tuple[int, float] = invalid_idx, invalid_distance
    left_start_zone = None
    left_end_zone = None
    for point_idx, trackpoint in enumerate(trackpoints):

        # Find start of effort first.
        if is_trackpoint_close_to_point(trackpoints[point_idx], segment.p1):
            start_dist = distance(track_point_to_point(trackpoint), segment.p1)
            if start_idx_dist[0] == invalid_idx or \
                    start_dist < start_idx_dist[1] or \
                    left_start_zone:
                start_idx_dist = point_idx, start_dist
                left_start_zone = False  # Skip previous passes though the start zone.
        else:
            left_start_zone = True

        # Only consider potential end points if they came after a start point.
        if start_idx_dist[0] != invalid_idx:
            if is_trackpoint_close_to_point(trackpoints[point_idx], segment.p2):
                end_dist = distance(track_point_to_point(trackpoint), segment.p2)
                if not end_idx_dist or end_dist < end_idx_dist[1]:
                    end_idx_dist = point_idx, end_dist
                    left_end_zone = False
        else:
            left_end_zone = True

        if left_start_zone and left_end_zone and \
                start_idx_dist[0] != invalid_idx and end_idx_dist[0] != invalid_idx:
            break

    if start_idx_dist[0] == invalid_idx:
        raise RuntimeError("Did not find a suitable segment start point in the activity.")
    if end_idx_dist[0] == invalid_idx:
        raise RuntimeError("Did not find a suitable segment end point in the acticity.")
    return start_idx_dist[0], end_idx_dist[0]


def calculate_effort_time(activity_tcx_path: str, segment: GeoSegment) -> None:
    """Calculate the effort time of an activity on a specific segment."""
    tcx_reader = TCXReader()
    activity = tcx_reader.read(activity_tcx_path)
    log_msg(f'Analyzing activity: {activity_tcx_path}')

    trackpoints: List[TCXTrackPoint] = activity.trackpoints

    start_idx, end_idx = find_indexes_of_trackpoints_closest_to_first_effort_start_and_end(
        segment, trackpoints)

    coarse_segment_time = float(
        (trackpoints[end_idx].time - trackpoints[start_idx].time).total_seconds()
    )

    # Refinement of the coarse start_idx-to-end_idx way.
    precise_segment_time = calc_effort_time(segment, trackpoints, start_idx, end_idx)

    log_msg(f'Coarse segment time: {coarse_segment_time=:0.1f}')
    log_msg(f'Precise segment time: {precise_segment_time=:0.1f}')


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
