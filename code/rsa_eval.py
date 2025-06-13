# STEP 1: Install required packages
#!pip install pycryptodome psutil

# STEP 2: Import libraries
import time
import psutil
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import numpy as np
import pandas as pd

# STEP 3: Upload your dataset
#from google.colab import files
#uploaded = files.upload()

# STEP 4: Load dataset
df_veremi = pd.read_csv("veremi_balanced_5000.csv")
data_rows = df_veremi.astype(str).agg(','.join, axis=1).tolist()

# STEP 5: RSA Evaluation Function
def evaluate_rsa(data_subset):
    key = RSA.generate(2048)
    public_key = key.publickey()
    cipher = PKCS1_OAEP.new(public_key)
    decipher = PKCS1_OAEP.new(key)

    enc_times = []
    dec_times = []
    cpu_usages = []
    mem_usages = []

    for row in data_subset:
        data = row.encode()

        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent

        start_enc = time.time()
        encrypted = cipher.encrypt(data[:190])  # RSA 2048 max block ~190 bytes with PKCS1_OAEP
        enc_times.append(time.time() - start_enc)

        start_dec = time.time()
        decrypted = decipher.decrypt(encrypted)
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
        "Throughput": len(data_subset) / sum(enc_times)
    }

# STEP 6: Run evaluation at multiple scales
rsa_results = []
for size in [100, 500, 1000, 5000]:
    subset = data_rows[:size]
    print(size)
    metrics = evaluate_rsa(subset)
    rsa_results.append(metrics)

# STEP 7: Save and display results
df_rsa_metrics = pd.DataFrame(rsa_results)
print(df_rsa_metrics)

df_rsa_metrics.to_csv("rsa_evaluation_metrics.csv", index=False)

# Download CSV
#from google.colab import files
#files.download("rsa_evaluation_metrics.csv")
