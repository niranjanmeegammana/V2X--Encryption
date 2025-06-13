# STEP 1: Install required package
#!pip install pycryptodome psutil

# STEP 2: Import libraries
import time
import psutil
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import numpy as np
import pandas as pd

# STEP 3: Upload your CSV file
#from google.colab import files
#uploaded = files.upload()

# STEP 4: Load the dataset
df_veremi = pd.read_csv("veremi_balanced_5000.csv")
data_rows = df_veremi.astype(str).agg(','.join, axis=1).tolist()

# STEP 5: AES Evaluation Function
def evaluate_aes(data_subset):
    key = get_random_bytes(16)
    block_size = AES.block_size

    enc_times = []
    dec_times = []
    cpu_usages = []
    mem_usages = []

    for row in data_subset:
        data = row.encode()

        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent

        start_enc = time.time()
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, block_size))
        iv = cipher.iv
        enc_times.append(time.time() - start_enc)

        start_dec = time.time()
        cipher_dec = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher_dec.decrypt(ct_bytes), block_size)
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
results = []
for size in [100, 500, 1000, 5000]:
    subset = data_rows[:size]
    print(size)
    metrics = evaluate_aes(subset)
    results.append(metrics)

# STEP 7: Show and save results
df_metrics = pd.DataFrame(results)
print(df_metrics)

df_metrics.to_csv("aes_evaluation_metrics.csv", index=False)
#files.download("aes_evaluation_metrics.csv")
