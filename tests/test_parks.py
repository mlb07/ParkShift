from parkshift.parks import load_parks
from parkshift.mlb import TEAM_HOME_PARK_ID


def test_bundled_parks_have_one_degree_wall_profiles() -> None:
    parks = load_parks()

    assert len(parks) == 30
    for park in parks.values():
        angles = [point.angle_deg for point in park.wall]
        assert angles == list(range(-45, 46))


def test_yankee_profile_is_calibrated_to_published_markers() -> None:
    yankee = load_parks()["yankee"]
    by_angle = {point.angle_deg: point.distance_ft for point in yankee.wall}

    assert by_angle[-45] == 318
    assert by_angle[0] == 408
    assert by_angle[45] == 314


def test_every_team_home_park_mapping_exists() -> None:
    parks = load_parks()

    assert set(TEAM_HOME_PARK_ID.values()) == set(parks)
