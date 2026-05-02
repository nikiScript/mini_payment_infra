from pydantic import BaseModel

class FraudFeatures(BaseModel):
    velocity_10m: int
    total_24h: int
    high_value_count: int
    geo_mismatch: int
    round_amount_count: int

def fraud_score(features: FraudFeatures):

    total_score = (
        features.velocity_10m * 12 +
        features.high_value_count * 15 +
        features.geo_mismatch * 25 +
        features.round_amount_count * 5
    )

    return total_score