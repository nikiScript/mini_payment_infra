from pydantic import BaseModel

class FraudFeatures(BaseModel):
    velocity_10m: int
    total_24h: int
    high_value_count: int
    geo_mismatch: int
    round_amount_count: int

f = FraudFeatures(
    velocity_10m=10,
    total_24h=24,
    high_value_count=10,
    geo_mismatch=3,
    round_amount_count=3,
)

def some_func(
    velocity_10m: int,
    total_24h: int,
    high_value_count: int,
    geo_mismatch: int,
    round_amount_count: int,
):
    print(velocity_10m, total_24h, high_value_count, geo_mismatch, round_amount_count)

some_func(**f.model_dump())
