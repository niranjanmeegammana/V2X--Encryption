# STEP 1: Install dependencies
#!pip install pycryptodome psutil

# STEP 2: Import required libraries
import pandas as pd
import time
import psutil
import numpy as np
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
#from google.colab import files

# STEP 3: Upload dataset
#uploaded = files.upload()

# STEP 4: Load full dataset
df_veremi = pd.read_csv("veremi_balanced_5000.csv")

# STEP 5: ECC Key Pair Setup
private_key = ECC.generate(curve='P-256')
public_key = private_key.public_key()
signer = DSS.new(private_key, 'fips-186-3')
verifier = DSS.new(public_key, 'fips-186-3')

# STEP 6: Performance metrics storage
metrics_results = []

# STEP 7: Loop over different dataset sizes
for size in [100, 500, 1000, 5000]:
    subset = df_veremi.iloc[:size].copy()
    messages = subset.astype(str).agg(','.join, axis=1).tolist()
    print(size)
    sign_times = []
    verify_times = []
    cpu_usages = []
    mem_usages = []
    verified = []

    for msg in messages:
        msg_bytes = msg.encode()
        hash_obj = SHA256.new(msg_bytes)

        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent

        # Sign
        start_sign = time.time()
        signature = signer.sign(hash_obj)
        sign_times.append(time.time() - start_sign)

        # Verify
        start_verify = time.time()
        try:
            verifier.verify(hash_obj, signature)
            verified.append(1)
        except ValueError:
            verified.append(0)
        verify_times.append(time.time() - start_verify)

        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().percent
        cpu_usages.append(cpu_after - cpu_before)
        mem_usages.append(mem_after - mem_before)

    metrics_results.append({
        "Records": size,
        "Avg_Sign_Time": np.mean(sign_times),
        "Avg_Verify_Time": np.mean(verify_times),
        "Avg_Latency": np.mean(sign_times) + np.mean(verify_times),
        "Avg_CPU_Usage": np.mean(cpu_usages),
        "Avg_Mem_Usage": np.mean(mem_usages),
        "Throughput (sign/sec)": size / sum(sign_times),
        "Verified_Rate": np.mean(verified)
    })

# STEP 8: Save results to CSV
df_metrics = pd.DataFrame(metrics_results)
print(df_metrics)

df_metrics.to_csv("veremi_ecc_metrics.csv", index=False)
#files.download("veremi_ecc_metrics.csv")
