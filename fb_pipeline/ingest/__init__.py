"""Ingest pipeline for FB community scrapes.

Separate from the legacy 01_tag_and_batch / 02_chatgpt_prompts / 03_merge_outputs
pipeline. That pipeline was a ChatGPT-loop question extractor; this one produces a
deduplicated corpus ready for embeddings-based clustering (Task 2).
"""
