# STEP 1: Install required packages
#!pip install pycryptodome psutil

# STEP 2: Import libraries
import time
import psutil
import numpy as np
import pandas as pd
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA256
#from google.colab import files

# STEP 3: Upload dataset
#uploaded = files.upload()

# STEP 4: Load dataset
df_veremi = pd.read_csv("veremi_balanced_5000.csv")
data_rows = df_veremi.astype(str).agg(','.join, axis=1).tolist()

# STEP 5: Simulate DH-like Key Exchange using DSA parameters
def evaluate_dh_key_exchange(data_subset):
    key_gen_times = []
    shared_secret_times = []
    cpu_usages = []
    mem_usages = []

    for _ in data_subset:
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent

        # Key generation for Party A
        start_keygen = time.time()
        key_a = DSA.generate(1024)
        pub_a = key_a.publickey()
        key_gen_times.append(time.time() - start_keygen)

        # Key generation for Party B
        key_b = DSA.generate(1024)
        pub_b = key_b.publickey()

        # Simulate shared secret agreement using public values
        start_shared = time.time()
        # Simulated by hashing public key bytes from both sides
        shared_secret_a = SHA256.new(pub_b.y.to_bytes(128, byteorder='big')).digest()
        shared_secret_b = SHA256.new(pub_a.y.to_bytes(128, byteorder='big')).digest()
        shared_secret_times.append(time.time() - start_shared)

        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().percent
        cpu_usages.append(cpu_after - cpu_before)
        mem_usages.append(mem_after - mem_before)

    return {
        "Records": len(data_subset),
        "Avg_KeyGen_Time": np.mean(key_gen_times),
        "Avg_SharedSecret_Time": np.mean(shared_secret_times),
        "Avg_Latency": np.mean(key_gen_times) + np.mean(shared_secret_times),
        "Avg_CPU_Usage": np.mean(cpu_usages),
        "Avg_Mem_Usage": np.mean(mem_usages),
        "Throughput (exchanges/sec)": len(data_subset) / sum(shared_secret_times)
    }

# STEP 6: Evaluate at multiple sizes
metrics_results = []
for size in [100, 500, 1000, 5000]:
    subset = data_rows[:size]
    print(size)
    metrics = evaluate_dh_key_exchange(subset)
    metrics_results.append(metrics)

# STEP 7: Save and download results
df_metrics = pd.DataFrame(metrics_results)
print(df_metrics)

df_metrics.to_csv("dh_key_exchange_metrics.csv", index=False)
#files.download("dh_key_exchange_metrics.csv")
