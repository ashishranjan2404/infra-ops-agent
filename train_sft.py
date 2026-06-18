#!/usr/bin/env python3
"""
SFT: fine-tune Qwen on the infra incident trajectories with Unsloth (cheap/fast).
Stack per project-root skills.md (Ben Burtenshaw: Unsloth + HF CLI + Trackio).

RUN ON A GPU (Colab / cloud). Not executed locally (no GPU here).
  pip install -r requirements.txt
  huggingface-cli login           # for pushing the model / using HF jobs
  python train_sft.py --model unsloth/Qwen2.5-7B-Instruct --data incidents.jsonl
"""
import argparse
import fmt
from datasets import load_dataset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="unsloth/Qwen2.5-7B-Instruct")  # or ...-14B-Instruct
    ap.add_argument("--data", default="incidents.jsonl")
    ap.add_argument("--max_seq", type=int, default=4096)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--out", default="qwen-infra-sft")
    args = ap.parse_args()

    from unsloth import FastLanguageModel
    from trl import SFTTrainer, SFTConfig

    model, tok = FastLanguageModel.from_pretrained(
        model_name=args.model, max_seq_length=args.max_seq, load_in_4bit=True, dtype=None)
    model = FastLanguageModel.get_peft_model(
        model, r=16, lora_alpha=16, lora_dropout=0.0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=42)

    ds = load_dataset("json", data_files=args.data, split="train")
    ds = ds.map(lambda ex: {"text": tok.apply_chat_template(fmt.to_messages(ex), tokenize=False)})

    trainer = SFTTrainer(
        model=model, tokenizer=tok, train_dataset=ds, dataset_text_field="text",
        args=SFTConfig(
            max_seq_length=args.max_seq, per_device_train_batch_size=2,
            gradient_accumulation_steps=8, warmup_ratio=0.03, num_train_epochs=args.epochs,
            learning_rate=2e-4, bf16=True, logging_steps=20, optim="adamw_8bit",
            output_dir="outputs_sft", report_to="trackio", seed=42))
    trainer.train()
    model.save_pretrained(args.out)
    tok.save_pretrained(args.out)
    print(f"saved -> {args.out}  (push: model.push_to_hub_merged('<user>/{args.out}', tok))")


if __name__ == "__main__":
    main()
