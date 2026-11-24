import numpy as np
import pandas as pd
import os

def generate_concrete_dataset():
    np.random.seed(101)

    # Documented reference experimental samples from Kiran IDP concrete testing report
    anchors = [
        {"Sample_ID": "C001", "Age": 1, "Rebound_Index": 21.3, "UPV": 3649, "Actual_Strength": 8.00},
        {"Sample_ID": "C002", "Age": 1, "Rebound_Index": 21.9, "UPV": 3616, "Actual_Strength": 9.02},
        {"Sample_ID": "C003", "Age": 1, "Rebound_Index": 23.9, "UPV": 3592, "Actual_Strength": 9.08},
        {"Sample_ID": "C004", "Age": 1, "Rebound_Index": 20.6, "UPV": 3519, "Actual_Strength": 8.04},
        {"Sample_ID": "C005", "Age": 1, "Rebound_Index": 17.5, "UPV": 3346, "Actual_Strength": 7.74},
    ]

    # Standard testing ages in concrete technology: 1, 3, 7, 14, 28, 56, 90 days
    # Concrete mix targets (design 28-day characteristic cube strength):
    # M15 (20 MPa avg), M20 (26 MPa avg), M25 (32 MPa avg), M30 (38 MPa avg), M35 (44 MPa avg), M40 (50 MPa avg), M50 (58 MPa avg)
    mix_grades = [
        {"name": "M15", "fc28_mean": 20.5, "rebound_28": 28.5, "upv_28": 3950},
        {"name": "M20", "fc28_mean": 26.0, "rebound_28": 32.0, "upv_28": 4150},
        {"name": "M25", "fc28_mean": 32.5, "rebound_28": 35.5, "upv_28": 4350},
        {"name": "M30", "fc28_mean": 38.5, "rebound_28": 39.0, "upv_28": 4500},
        {"name": "M35", "fc28_mean": 44.5, "rebound_28": 42.0, "upv_28": 4650},
        {"name": "M40", "fc28_mean": 50.5, "rebound_28": 45.0, "upv_28": 4780},
        {"name": "M50", "fc28_mean": 58.5, "rebound_28": 48.5, "upv_28": 4900},
    ]

    age_strength_ratio = {
        1: 0.22,
        3: 0.45,
        7: 0.67,
        14: 0.86,
        28: 1.00,
        56: 1.12,
        90: 1.18
    }

    age_rebound_ratio = {
        1: 0.58,
        3: 0.72,
        7: 0.84,
        14: 0.93,
        28: 1.00,
        56: 1.06,
        90: 1.10
    }

    age_upv_ratio = {
        1: 0.85,
        3: 0.90,
        7: 0.94,
        14: 0.97,
        28: 1.00,
        56: 1.03,
        90: 1.05
    }

    samples = list(anchors)
    sample_num = 6

    for mix in mix_grades:
        for age in [1, 3, 7, 14, 28, 56, 90]:
            # Generate 3 specimens per mix per age
            for rep in range(3):
                # Strength variation (+- 3%)
                noise_s = np.random.normal(0, 0.025)
                fc = mix["fc28_mean"] * age_strength_ratio[age] * (1.0 + noise_s)
                fc = round(max(5.5, fc), 2)

                # Rebound hammer reading with realistic instrument scatter (+- 1.0 unit)
                noise_r = np.random.normal(0, 0.9)
                reb = mix["rebound_28"] * age_rebound_ratio[age] + noise_r
                reb = round(np.clip(reb, 15.0, 52.0), 1)

                # UPV reading with pulse transmission scatter (+- 35 m/s)
                noise_u = np.random.normal(0, 30)
                v = mix["upv_28"] * age_upv_ratio[age] + noise_u
                v = int(np.clip(round(v), 3150, 4980))

                sample_id = f"C{sample_num:03d}"
                samples.append({
                    "Sample_ID": sample_id,
                    "Age": age,
                    "Rebound_Index": reb,
                    "UPV": v,
                    "Actual_Strength": fc
                })
                sample_num += 1

    df = pd.DataFrame(samples)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/concrete_samples.csv", index=False)
    print(f"Generated {len(df)} concrete samples saved to data/concrete_samples.csv")
    print(df.head(10))
    print(df.tail(5))
    print(df.describe())

if __name__ == "__main__":
    generate_concrete_dataset()
