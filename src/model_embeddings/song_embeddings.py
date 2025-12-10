import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, models
import torch
import os
from tqdm import tqdm


df = pd.read_csv('spotify_millsongdata.csv')

print('loading model...')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# "Qwen/Qwen3-Embedding-0.6B" attempting as replacement for this, which took 9 minutes to run on 100 songs.

# Prepare list of all lyrics as strings
lyrics_list = df["text"].astype(str).tolist()

print("\ncreating embeddings in batches...")
emb_matrix = model.encode(
    lyrics_list,
    batch_size=32,          
    convert_to_numpy=True,
    show_progress_bar=True 
).astype("float32")

print('\nsaving compressed embeddings...')
np.savez_compressed("song_embeddings_miniLM.npz", embeddings=emb_matrix)

# print('\ncreating embeddings...')
# df["embedding"] = df["text"].apply(lambda x: model.encode(x, convert_to_numpy=True))
# emb_matrix = np.vstack(df["embedding"].values).astype("float32")

# # Save embeddings
# print('\nsaving embeddings...')
# np.savez_compressed("song_embeddings.npz", emb_matrix)
# # model.save("saved_lyrics_model")


#print(torch.cuda.is_available())


# ######################################################################

# # === CONFIG ===
# CSV_PATH = "spotify_millsongdata_subset.csv"
# EMBEDDING_SAVE_PATH = "song_embeddings.npy"
# CHECKPOINT_DIR = "embedding_checkpoints"
# PROGRESS_FILE = "embedding_progress.txt"
# BATCH_SIZE = 64

# # === SETUP ===
# os.makedirs(CHECKPOINT_DIR, exist_ok=True)
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device}")

# print("Loading model...")
# model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device=device)

# print("Loading data...")
# df = pd.read_csv(CSV_PATH)
# texts = df["text"].tolist()

# # === RESUME SUPPORT ===
# start_idx = 0
# if os.path.exists(PROGRESS_FILE):
#     with open(PROGRESS_FILE, "r") as f:
#         start_idx = int(f.read().strip())
#     print(f"Resuming from batch index: {start_idx}")

# # === EMBEDDING LOOP ===
# embeddings = []

# for i in range(start_idx, len(texts), BATCH_SIZE):
#     batch = texts[i:i + BATCH_SIZE]
#     emb = model.encode(batch, convert_to_numpy=True)
#     embeddings.extend(emb)

#     # Save checkpoint
#     if i % (BATCH_SIZE * 100) == 0:
#         checkpoint_path = os.path.join(CHECKPOINT_DIR, f"checkpoint_{i}.npy")
#         np.save(checkpoint_path, np.array(embeddings, dtype="float32"))
#         with open(PROGRESS_FILE, "w") as f:
#             f.write(str(i))
#         print(f"Checkpoint saved at batch {i}")
#         print(f"{i}/{len(texts)} complete")

# # === FINAL SAVE ===
# emb_matrix = np.array(embeddings, dtype="float32")
# np.save(EMBEDDING_SAVE_PATH, emb_matrix)
# print(f"Embeddings saved to {EMBEDDING_SAVE_PATH}")

# # === CLEANUP ===
# if os.path.exists(PROGRESS_FILE):
#     os.remove(PROGRESS_FILE)
# print("Embedding complete.")




