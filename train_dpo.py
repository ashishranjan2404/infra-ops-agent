#!/usr/bin/env python3
"""
DPO: align the SFT model on the winner/loser preference pairs (pairs.jsonl).
This is what teaches process quality the binary verifier can't see (skipped
diagnosis, hallucinated args, thought/action mismatch). Start FROM the SFT ckpt.

RUN ON A GPU (Colab / cloud).
  python train_dpo.py --model qwen-infra-sft --data pairs.jsonl
"""
import argparse
import fmt
from datasets import load_dataset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen-infra-sft")  # start from SFT checkpoint
    ap.add_argument("--data", default="pairs.jsonl")
    ap.add_argument("--out", default="qwen-infra-dpo")
    args = ap.parse_args()

    from unsloth import FastLanguageModel, PatchDPOTrainer
    PatchDPOTrainer()
    from trl import DPOTrainer, DPOConfig

    model, tok = FastLanguageModel.from_pretrained(
        model_name=args.model, max_seq_length=4096, load_in_4bit=True, dtype=None)
    model = FastLanguageModel.get_peft_model(
        model, r=16, lora_alpha=16, lora_dropout=0.0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=42)

    ds = load_dataset("json", data_files=args.data, split="train").map(fmt.to_pref)

    trainer = DPOTrainer(
        model=model, ref_model=None, tokenizer=tok, train_dataset=ds,
        args=DPOConfig(
            beta=0.1, per_device_train_batch_size=2, gradient_accumulation_steps=8,
            warmup_ratio=0.03, num_train_epochs=1, learning_rate=5e-6, bf16=True,
            logging_steps=20, optim="adamw_8bit", output_dir="outputs_dpo",
            report_to="trackio", seed=42, max_length=4096, max_prompt_length=1024))
    trainer.train()
    model.save_pretrained(args.out)
    tok.save_pretrained(args.out)
    print(f"saved -> {args.out}")


if __name__ == "__main__":
    main()
