from pydantic import BaseModel

class FraudFeatures(BaseModel):
    velocity_10m: int
    total_24h: int
    high_value_count: int
    geo_mismatch: int
    round_amount_count: int


def enforce_rules(features: FraudFeatures):


    if features.velocity_10m >= 10:
        return {
            "status": "blocked",
            "reason": "high velocity"
        }
    if  features.total_24h > 100:
        return {
            "status": "blocked",
            "reason": "high amount of transactions within 24 hours"
        }
    if features.high_value_count > 2:
        return {
            "status": "blocked",
            "reason": "multiple high value transactions"
        }
    if features.geo_mismatch > 2:
        return {
            "status": "blocked",
            "reason": "multiple location mismatches"
        }
    if features.round_amount_count > 5:
        return {
            "status": "blocked",
            "reason": "round amount transactions exceeds 5"
        }
    else:
        return {
            "status": "allowed",
            "reasons": "all rules were passed"
        }