from beanie.odm.operators.find.geospatial import (
    Box,
    GeoIntersects,
    GeoWithin,
    Near,
    NearSphere,
)
from tests.odm.models import Sample


async def test_geo_intersects():
    q = GeoIntersects(
        Sample.geo, geo_type="Polygon", coordinates=[[1, 1], [2, 2], [3, 3]]
    )
    assert q == {
        "geo": {
            "$geoIntersects": {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": [[1, 1], [2, 2], [3, 3]],
                }
            }
        }
    }


async def test_geo_within():
    q = GeoWithin(
        Sample.geo, geo_type="Polygon", coordinates=[[1, 1], [2, 2], [3, 3]]
    )
    assert q == {
        "geo": {
            "$geoWithin": {
                "$geometry": {
                    "type": "Polygon",
                    "coordinates": [[1, 1], [2, 2], [3, 3]],
                }
            }
        }
    }


async def test_box():
    q = Box(Sample.geo, lower_left=[1,3], upper_right=[2,4])
    assert q == {
        "geo": {
            "$geoWithin": {
                "$box": [[1,3], [2,4]]
            }
        }
    }


async def test_near():
    q = Near(Sample.geo, longitude=1.1, latitude=2.2)
    assert q == {
        "geo": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]}
            }
        }
    }

    q = Near(Sample.geo, longitude=1.1, latitude=2.2, max_distance=1)
    assert q == {
        "geo": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]},
                "$maxDistance": 1,
            }
        }
    }

    q = Near(
        Sample.geo,
        longitude=1.1,
        latitude=2.2,
        max_distance=1,
        min_distance=0.5,
    )
    assert q == {
        "geo": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]},
                "$maxDistance": 1,
                "$minDistance": 0.5,
            }
        }
    }


async def test_near_sphere():
    q = NearSphere(Sample.geo, longitude=1.1, latitude=2.2)
    assert q == {
        "geo": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]}
            }
        }
    }

    q = NearSphere(Sample.geo, longitude=1.1, latitude=2.2, max_distance=1)
    assert q == {
        "geo": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]},
                "$maxDistance": 1,
            }
        }
    }

    q = NearSphere(
        Sample.geo,
        longitude=1.1,
        latitude=2.2,
        max_distance=1,
        min_distance=0.5,
    )
    assert q == {
        "geo": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [1.1, 2.2]},
                "$maxDistance": 1,
                "$minDistance": 0.5,
            }
        }
    }
