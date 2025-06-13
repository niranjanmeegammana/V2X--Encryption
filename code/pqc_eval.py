import time
import os
import psutil
import hashlib
import numpy as np
import pandas as pd
#from google.colab import files

# STEP 1: Upload dataset
#uploaded = files.upload()

# STEP 2: Load your dataset
df_veremi = pd.read_csv("veremi_balanced_5000.csv")
data_rows = df_veremi.astype(str).agg(','.join, axis=1).tolist()

# STEP 3: Simulated NTRU-like encryption benchmark
def simulate_pqc(data_subset):
    enc_times = []
    dec_times = []
    cpu_usages = []
    mem_usages = []

    for _ in data_subset:
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent

        # Key generation simulation
        keypair = os.urandom(32)

        # Simulated encryption
        start_enc = time.time()
        ciphertext = hashlib.sha256(keypair).digest()
        enc_times.append(time.time() - start_enc)

        # Simulated decryption
        start_dec = time.time()
        recovered_key = hashlib.sha256(ciphertext).digest()
        dec_times.append(time.time() - start_dec)

        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().percent
        cpu_usages.append(cpu_after - cpu_before)
        mem_usages.append(mem_after - mem_before)

    return {
        "Records": len(data_subset),
        "Avg_Enc_Time": np.mean(enc_times),
        "Avg_Dec_Time": np.mean(dec_times),
        "Avg_Latency": np.mean(enc_times) + np.mean(dec_times),
        "Avg_CPU_Usage": np.mean(cpu_usages),
        "Avg_Mem_Usage": np.mean(mem_usages),
        "Throughput (encrypt/sec)": len(data_subset) / sum(enc_times)
    }

# STEP 4: Run for different record sizes
results = []
for size in [100, 500, 1000, 5000]:
    subset = data_rows[:size]
    print(size)
    metrics = simulate_pqc(subset)
    results.append(metrics)

# STEP 5: Save and download results
df_pqc = pd.DataFrame(results)
df_pqc.to_csv("veremi_pqc_simulated_metrics.csv", index=False)
#files.download("veremi_pqc_simulated_metrics.csv")

