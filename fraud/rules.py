from models import FraudFeatures

def enforce_rules(f: FraudFeatures):

    if f.velocity_2m >= 8:
        return {
            "status": "blocked",
            "reason": "high velocity"
        }

    if f.velocity_10m >= 10:
        return {
            "status": "blocked",
            "reason": "high velocity"
        }

    if f.high_value_count > 2:
        return {
            "status": "blocked",
            "reason": "multiple high value transactions"
        }
    if f.geo_mismatch > 2:
        return {
            "status": "blocked",
            "reason": "multiple location mismatches"
        }

    else:
        return {
            "status": "allowed",
            "reasons": "all rules were passed"
        }