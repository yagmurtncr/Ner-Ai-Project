import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import datetime
import json
import traceback
import scipy.special

from sklearn.metrics import precision_recall_curve, f1_score, confusion_matrix, accuracy_score
from transformers import Trainer, AutoModelForTokenClassification
from preprocessing import get_tokenized_datasets
from seqeval.metrics import classification_report as seqeval_report

def evaluate_per_entity_thresholds(probabilities, true_labels, label_list, threshold_list=None):
    if threshold_list is None:
        threshold_list = [round(i * 0.05, 2) for i in range(1, 21)]

    entity_types = sorted(set(label.split("-")[-1] for label in label_list if label != 'O'))
    best_thresholds = {}

    for entity in entity_types:
        print(f"\nEntity: {entity}")
        best_f1 = -1.0
        best_threshold = 0.0

        result_table = []

        for threshold in threshold_list:
            TP = FP = FN = TN = 0

            for token_probs, true_label in zip(probabilities, true_labels):
                true_entity = true_label.split("-")[-1] if true_label != 'O' else 'O'
                pred_index = np.argmax(token_probs)
                pred_label = label_list[pred_index]
                pred_score = token_probs[pred_index]
                pred_entity = pred_label.split("-")[-1] if pred_label != 'O' else 'O'

                if pred_score < threshold or pred_entity != entity:
                    pred_entity = 'O'

                if true_entity == entity and pred_entity == entity:
                    TP += 1
                elif true_entity != entity and pred_entity == entity:
                    FP += 1
                elif true_entity == entity and pred_entity != entity:
                    FN += 1
                else:
                    TN += 1

            precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
            recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = (TP + TN) / (TP + FP + FN + TN) if (TP + FP + FN + TN) > 0 else 0.0

            result_table.append([threshold, precision, recall, f1, accuracy, TP, FP, TN, FN])

            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        df = pd.DataFrame(result_table, columns=["Threshold", "Precision", "Recall", "F1", "Accuracy", "TP", "FP", "TN", "FN"])
        df.to_csv(f"visual_results/{entity}_threshold_results.csv", index=False)

        print(df.to_string(index=False))
        print(f"\n✅ Entity '{entity}' için en iyi threshold: {best_threshold} (F1: {best_f1:.3f})")

        best_thresholds[entity] = best_threshold

    return best_thresholds

def evaluate_model(model_path="./ner_model/checkpoint-1100", model_name="dbmdz/bert-base-turkish-cased",
                   train_path="raw_data/balanced_train_dataset.csv",
                   dev_path="raw_data/balanced_dev_dataset.csv",
                   test_path="raw_data/balanced_test_dataset.csv"):

    os.makedirs("visual_results", exist_ok=True)

    dataset, label_list, label2id, id2label, tokenizer = get_tokenized_datasets(
        train_path, dev_path, test_path, model_name
    )

    model = AutoModelForTokenClassification.from_pretrained(model_path)
    trainer = Trainer(model=model)
    outputs = trainer.predict(dataset["test"])

    predictions = outputs.predictions.argmax(axis=-1)
    labels = outputs.label_ids

    true_labels = []
    pred_labels = []
    all_scores = []
    all_true = []
    all_probabilities = []

    for i in range(len(labels)):
        for j in range(len(labels[i])):
            if labels[i][j] != -100:
                true_label = id2label[labels[i][j]]
                pred_label = id2label[predictions[i][j]]

                probs = scipy.special.softmax(outputs.predictions[i][j])
                all_probabilities.append(probs)

                entity_probs = [probs[k] for k, label in id2label.items() if label != 'O']
                score = max(entity_probs)

                all_true.append(1 if true_label != 'O' else 0)
                all_scores.append(score)

                true_labels.append(true_label)
                pred_labels.append(pred_label)

    print("\n📊 Sınıflandırma Raporu:\n")
    seqeval_true = []
    seqeval_pred = []
    for i in range(len(labels)):
        tmp_true_seq = []
        tmp_pred_seq = []
        for j in range(len(labels[i])):
            if labels[i][j] != -100:
                tmp_true_seq.append(id2label[labels[i][j]])
                tmp_pred_seq.append(id2label[predictions[i][j]])
        seqeval_true.append(tmp_true_seq)
        seqeval_pred.append(tmp_pred_seq)
    print(seqeval_report(seqeval_true, seqeval_pred))

    # Threshold analizini yap
    best_thresholds = evaluate_per_entity_thresholds(
        probabilities=all_probabilities,
        true_labels=true_labels,
        label_list=[id2label[i] for i in range(len(id2label))]
    )

    with open("visual_results/best_entity_thresholds.json", "w", encoding="utf-8") as f:
        json.dump(best_thresholds, f, indent=2, ensure_ascii=False)

    # Ek olarak CSV tablo olarak da yaz
    summary_df = pd.DataFrame([
        {"Entity": entity, "Best_Threshold": threshold}
        for entity, threshold in best_thresholds.items()
    ])
    summary_df.to_csv("visual_results/summary_best_thresholds.csv", index=False)
    print("\n📄 Tüm entity'ler için en iyi threshold özet tablosu:\n")
    print(summary_df.to_string(index=False))

    
def main():
    try:
        print("\n📈 NER Model Performans Analizi\n")
        evaluate_model()
    except Exception as e:
        print("HATA OLUŞTU:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
