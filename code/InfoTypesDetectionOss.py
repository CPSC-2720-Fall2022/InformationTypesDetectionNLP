import torch
import pandas as pd
from torch import nn
import datasets as dt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, Trainer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments
from sklearn.metrics import classification_report
import numpy as np

TOTAL_CLASS = 13
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")


# the goal of this function is to remove duplicate texts from the dataset and removing extra spaces from a text data
def preprocess_data(issue_df):
    # remove duplicate rows by Text Content
    issue_df = issue_df.drop_duplicates(subset=['Text Content'], keep='first')

    # replace newlines with space
    issue_df['Text Content'] = issue_df['Text Content'].str.replace('\n', ' ')

    # trim leading and trailing spaces
    issue_df['Text Content'] = issue_df['Text Content'].str.strip()
    return issue_df


# Call this function to get the dataset and get necessary information about the dataset: length of the dataset,
# number of items in per class, total number of classes
def getDatasetInfo():
    issue_df = pd.read_csv('../data/dataInfoTypes.csv')

    print('Total ' + str(len(issue_df['Code'].unique())) + ' Classes')
    print(set(issue_df['Code']))

    print('Total ' + str(len(issue_df)) + ' sentences\n\n')
    print(set(issue_df.head()))

    print('\n\n--------------Class Distribution----------')
    print(issue_df.Code.value_counts())

    # Only Text content and class label are needed. So other datas are dropped
    issue_df = issue_df[['Text Content', 'Code']]

    # cleanup the data
    issue_df = preprocess_data(issue_df)

    # Renaming code to label for better understanding
    issue_df = issue_df.rename(columns={'Text Content': 'text', 'Code': 'label'})

    # replacing label string with unique int value
    label_encoder = preprocessing.LabelEncoder()
    label_encoder.fit(issue_df['label'])
    issue_df['label'] = label_encoder.transform(issue_df['label'])

    print('\n\n------Final Columns on dataset---------')
    print(set(issue_df.head()))
    return issue_df


# 90% data are on training set and 10% on testset. 5% of the training data has been taken to the validation set.
def splitIntoTrainTestValSet(issue_df):
    train_df, test_df = train_test_split(issue_df, test_size=0.1, random_state=10, stratify=issue_df['label'])

    train_df, val_df = train_test_split(train_df, test_size=0.05, random_state=10, stratify=train_df['label'])

    train_dataset = Dataset.from_dict(train_df)
    val_dataset = Dataset.from_dict(val_df)
    test_dataset = Dataset.from_dict(test_df)

    dataset = dt.DatasetDict({"train": train_dataset, "val": val_dataset, "test": test_dataset})
    return dataset, train_df, val_df, test_df


# Class weight has been measured to handle the imbalance among class distribution and later fed into the trainer
def getClassWeight(train_df):
    total_class = len(set(train_df['label']))
    class_weight = [0 for i in range(total_class)]

    for i in range(total_class):
        count = len(train_df[train_df['label'] == i])
        class_weight[i] = (1 / count) * (len(train_df) / total_class)

    return class_weight


def preprocess_function(examples, text_column_name="text"):
    return tokenizer(examples[text_column_name], truncation=True)


def get_data_collator():
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    return data_collator


# Bert tokenizer and model has been used
def tokenize(dataset):
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    return tokenized_dataset


def getModel():
    model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=TOTAL_CLASS)
    return model


def getTraining_args():
    training_args = TrainingArguments(
        output_dir="./results",
        learning_rate=2e-5,
        per_device_train_batch_size=16,  # 16
        per_device_eval_batch_size=16,  # 16
        num_train_epochs=10,
        weight_decay=0.01,
    )

    return training_args


# this function take dataset as a input, calculate class weights, tokenize text data and then train the model based
# on the text data only.
def train_model():
    # loading dataset file into dataframe
    issue_df = getDatasetInfo()

    # splitting dataset into 3 non overlapping sets: train,test, validation
    dataset, train_df, val_df, test_df = splitIntoTrainTestValSet(issue_df)

    # for balancing this imbalanced dataset, classweight has been determined
    class_weight = getClassWeight(train_df)

    # tokenized the texts using bert
    tokenized_dataset = tokenize(dataset)

    data_collator = get_data_collator()
    model = getModel()

    # set some hyperparameters
    training_args = getTraining_args()

    # a custometrainer for incorporating class weight
    class CustomTrainer(Trainer):

        def compute_loss(self, model, inputs, return_outputs=False):
            device = model.device
            labels = inputs.get("labels").to(device)
            # forward pass
            outputs = model(**inputs)
            logits = outputs.get("logits").to(device)
            # compute custom loss (suppose one has 3 labels with different weights)
            loss_fct = nn.CrossEntropyLoss(weight=torch.tensor(
                [class_weight[0], class_weight[1], class_weight[2], class_weight[3], class_weight[4], class_weight[5],
                 class_weight[6], class_weight[7], class_weight[8], class_weight[9], class_weight[10], class_weight[11],
                 class_weight[12]])).to(
                device)  # ,class_weight_8,class_weight_9,class_weight_10,class_weight_11,class_weight_12
            loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
            return (loss, outputs) if return_outputs else loss

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["val"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()


train_model()
