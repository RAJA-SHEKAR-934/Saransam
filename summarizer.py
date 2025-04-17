import re
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

print(torch.cuda.is_available())       # Should return True
print(torch.cuda.get_device_name(0))   # Should print your GPU name
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

nltk.download('punkt')

# Load offline model
tokenizer = AutoTokenizer.from_pretrained("bart_model")
model = AutoModelForSeq2SeqLM.from_pretrained("bart_model").to(device)
summarizer_pipeline = pipeline("summarization", model=model, tokenizer=tokenizer)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'[^a-zA-Z0-9.,?! ]', '', text)
    return text.strip()

# def chunk_text(text, max_tokens=512):
#     sentences = sent_tokenize(text)
#     chunks, chunk = [], ""
#     for sentence in sentences:
#         if len((chunk + sentence).split()) <= max_tokens:
#             chunk += sentence + " "
#         else:
#             chunks.append(chunk.strip())
#             chunk = sentence + " "
#     if chunk:
#         chunks.append(chunk.strip())
#     return chunks

def chunk_text(text, tokenizer, max_tokens=1024):
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""

    for sentence in sentences:
        tentative_chunk = current_chunk + sentence + " "
        token_count = len(tokenizer.encode(tentative_chunk, truncation=False))

        if token_count <= max_tokens:
            current_chunk = tentative_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If even the sentence itself is too long, split it
            sentence_token_count = len(tokenizer.encode(sentence, truncation=False))
            if sentence_token_count > max_tokens:
                # Break it at word-level
                words = sentence.split()
                small_chunk = ""
                for word in words:
                    tentative_small = small_chunk + word + " "
                    if len(tokenizer.encode(tentative_small, truncation=False)) <= max_tokens:
                        small_chunk = tentative_small
                    else:
                        chunks.append(small_chunk.strip())
                        small_chunk = word + " "
                if small_chunk:
                    chunks.append(small_chunk.strip())
                current_chunk = ""
            else:
                current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# def summarize_text(raw_text, purpose="default"):
#     print(purpose)
#     cleaned = clean_text(raw_text)
#     prompt = purpose_prompts.get(purpose, purpose_prompts["default"])
#     print(prompt)
    
#     # Add the prompt to every chunk
#     chunks = chunk_text(cleaned, tokenizer, max_tokens=1024 - len(tokenizer(prompt)["input_ids"]))
    
#     summaries = []
#     for chunk in chunks:
#         input_text = prompt + chunk
#         tokens = tokenizer(input_text, return_tensors="pt", truncation=False)["input_ids"]
#         if tokens.shape[1] > 1024:
#             print("Too long chunk found! Length:", tokens.shape[1])
        
#         summary = summarizer_pipeline(
#             input_text,
#             max_length=150,
#             min_length=40,
#             do_sample=False
#         )[0]['summary_text']
#         summaries.append(summary)
    
#     return " ".join(summaries)

# def summarize_text(raw_text, batch_size=2):
#     cleaned = clean_text(raw_text)
#     chunks = chunk_text(cleaned, tokenizer, max_tokens=1024)

#     summaries = []

#     # Process chunks in batches
#     for i in range(0, len(chunks), batch_size):
#         batch_chunks = chunks[i:i + batch_size]
#         input_texts = [chunk for chunk in batch_chunks]

#         inputs = tokenizer(
#             input_texts,
#             return_tensors="pt",
#             truncation=True,
#             max_length=1024,
#             padding=True
#         ).to(device)

#         with torch.no_grad():
#             output_ids = model.generate(
#                 input_ids=inputs["input_ids"],
#                 attention_mask=inputs["attention_mask"],
#                 max_length=150,
#                 min_length=40,
#                 length_penalty=2.0,
#                 num_beams=4,
#                 early_stopping=True
#             )

#         batch_summaries = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
#         summaries.extend(batch_summaries)

#     return " ".join(summaries)


def summarize_text(raw_text):
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, tokenizer, max_tokens=1024)
    for chunk in chunks:
        tokens = tokenizer(chunk, return_tensors="pt", truncation=False)["input_ids"]
        if tokens.shape[1] > 1024:
            print("Too long chunk found! Length:", tokens.shape[1])

    summaries = [summarizer_pipeline(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text'] for chunk in chunks]
    return " ".join(summaries)