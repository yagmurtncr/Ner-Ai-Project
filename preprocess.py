import pandas as pd
from transformers import AutoTokenizer
from datasets import DatasetDict, Dataset

def get_tokenized_datasets(train_path, dev_path, test_path, tokenizer_name="dbmdz/bert-base-turkish-cased"):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)

    def load_and_group(path):
        df = pd.read_csv(path).fillna("O")
        grouped = df.groupby("sentence_id").agg(list)
        return grouped["token"].tolist(), grouped["label"].tolist()

    def tokenize_and_align_labels(sentences, labels, label2id, ignore_id=-100):
        tokenized = tokenizer(sentences, is_split_into_words=True, padding="longest", truncation=True)
        aligned = []

        for i, label_seq in enumerate(labels):
            word_ids = tokenized.word_ids(i)
            aligned_labels = []
            prev_word = None

            for idx in word_ids:
                if idx is None:
                    aligned_labels.append(ignore_id)
                elif idx != prev_word:
                    token_label = label_seq[idx]
                    aligned_labels.append(label2id.get(token_label, ignore_id))
                else:
                    aligned_labels.append(ignore_id)

                prev_word = idx

            aligned.append(aligned_labels)

        tokenized["labels"] = aligned
        return tokenized

    # Veriyi oku
    train_sents, train_labels = load_and_group(train_path)
    dev_sents, dev_labels = load_and_group(dev_path)
    test_sents, test_labels = load_and_group(test_path)

    # Etiketleri çıkar
    all_labels = sorted(set(label for seq in train_labels for label in seq))
    label2id = {label: i for i, label in enumerate(all_labels)}
    id2label = {i: label for label, i in label2id.items()}

    # Tokenize et ve hizala
    train_tokenized = tokenize_and_align_labels(train_sents, train_labels, label2id)
    dev_tokenized = tokenize_and_align_labels(dev_sents, dev_labels, label2id)
    test_tokenized = tokenize_and_align_labels(test_sents, test_labels, label2id)

    # DatasetDict
    dataset = DatasetDict({
        "train": Dataset.from_dict(train_tokenized),
        "validation": Dataset.from_dict(dev_tokenized),
        "test": Dataset.from_dict(test_tokenized)
    })

    return dataset, all_labels, label2id, id2label, tokenizer
