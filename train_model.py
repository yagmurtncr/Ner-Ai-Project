from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from preprocessing import get_tokenized_datasets
from collections import Counter

def compute_metrics(p, id2label):
    predictions, labels = p
    preds = np.argmax(predictions, axis=2)

    true_labels_flat = []
    true_preds_flat = []

    for label_seq, pred_seq in zip(labels, preds):
        for l, p in zip(label_seq, pred_seq):
            if l != -100:
                true_labels_flat.append(id2label[l])
                true_preds_flat.append(id2label[p])

    precision, recall, f1, _ = precision_recall_fscore_support(true_labels_flat, true_preds_flat, average="weighted")
    acc = accuracy_score(true_labels_flat, true_preds_flat)

    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

if __name__ == "__main__":
    # Türkçe özel model
    tokenizer_name = "dbmdz/bert-base-turkish-cased"

    dataset, labels, label2id, id2label, tokenizer = get_tokenized_datasets(
        "raw_data/balanced_train_dataset.csv",
        "raw_data/balanced_dev_dataset.csv",
        "raw_data/balanced_test_dataset.csv",
        tokenizer_name=tokenizer_name,
    )

    model = AutoModelForTokenClassification.from_pretrained(
        tokenizer_name,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)

    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="steps",
        eval_steps=500,
        save_steps=500,
        learning_rate=3e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=2,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        fp16=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=lambda p: compute_metrics(p, id2label),
    )

    trainer.train()

    print("\nTest seti değerlendirmesi:")
    metrics = trainer.evaluate(dataset["test"])
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

    # PHONE etiketlerinin dağılımı
    raw_pred = trainer.predict(dataset["test"])
    preds = np.argmax(raw_pred.predictions, axis=2)

    flat_preds = []
    for pred_seq, label_seq in zip(preds, raw_pred.label_ids):
        for p, l in zip(pred_seq, label_seq):
            if l != -100:
                flat_preds.append(id2label[p])

    print("\nModelin test verisi tahminlerindeki etiket dağılımı:")
    print(Counter(flat_preds))
