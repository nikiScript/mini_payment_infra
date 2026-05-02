from models import FraudFeatures

def fraud_score(f: FraudFeatures):

    # adds up to 1 max is 100
    total_score = int(100 * (
        normalize(f.velocity_2m) * 0.35 +
        normalize(f.velocity_10m) * 0.25 +
        normalize(f.high_value_count) * 0.20 +
        normalize(f.geo_mismatch) * 0.15 +
        normalize(f.round_amount_count) * 0.05
    ))

    return total_score

def normalize(x):
    return x / (1 + x)

