import torch
import pandas as pd
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, Dataset
import torch.nn.functional as F

import torch.optim as optim
from sklearn.model_selection import StratifiedShuffleSplit
from torchmetrics.classification import BinaryAccuracy, BinaryAUROC, BinaryROC
from torchmetrics.classification import ConfusionMatrix


def pos_class_weight(df: pd.DataFrame, target: str) -> float:
    """
    PARAMETERS:
    ----------
    - df [DataFrame] :
    - target [string] :
    RETURN:
    ------
    - Positive class weight for training on imbalance target
    """
    neg, pos = df[target].value_counts()
    return neg / pos


def data_splitter(df: pd.DataFrame,
                  pred_cols: list,
                  target: str,
                  test_size: float = 0.2,
                  holdout: bool = True) -> tuple:
    """Stratification splitter class with a test/validation size of <test_size> of the data.

    PARAMETER:
    ---------
    - df [DataFrame] :
    - pred_cols [List] :
    - target [String] :
    - test_size [Float] :
    - holdout [Boolean] :

    RETURN:
    ------
        Tuple with training data and holdout data.
    """
    # instantiate the stratification splitter class with a test/validation size of 20% of the data
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=42)

    x_train, y_train = None, None
    # split data into training and holdout (validation) datasets
    for train_idx, val_idx in splitter.split(df[pred_cols], df[target]):
        # define training set
        x_train, y_train = df[pred_cols].loc[train_idx], df[target].loc[train_idx]
        if holdout:
            # define validation/holdout set
            x_val, y_val = df[pred_cols].loc[val_idx], df[target].loc[val_idx]

            return x_train, y_train, x_val, y_val

    return x_train, y_train


# create a dataset class
class MyBiData(Dataset):
    def __init__(self, predictor: pd.DataFrame, label: pd.Series):
        super().__init__()
        self.predictor = torch.tensor(predictor.values, dtype=torch.float32)
        self.label = torch.tensor(label.values, dtype=torch.float32)

    # return the size of the total dataset
    def __len__(self):
        return len(self.predictor)

    def __getitem__(self, idx):
        pred_mean = self.predictor.mean()
        pred_std = self.predictor.std()
        self.predictor = (self.predictor - pred_mean) / pred_std
        return self.predictor[idx], self.label[idx]


def data_loader(x_train, y_train, x_val_=None, y_val_=None, x_test=None, y_test=None) -> tuple:
    """

    Args:
        x_train:
        y_train:
        x_val_:
        y_val_:
        x_test:
        y_test:

    Returns:

    """
    g = torch.Generator().manual_seed(42)

    # define training dataset
    train_dataset = MyBiData(predictor=x_train, label=y_train)
    # define training dataloader and shuffle the data
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, generator=g)

    if (x_val_ is not None) and (y_val_ is not None):
        # define holdout dataset
        val_dataset = MyBiData(predictor=x_val_, label=y_val_)
        # define holdout dataloader and shuffle the data
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=True, generator=g)

        return train_loader, val_loader

    if (x_test is not None) and (y_test is not None):
        # define testing dataset
        test_dataset = MyBiData(predictor=x_test, label=y_test)
        # define testing dataloader and do not shuffle the data
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

        return train_loader, test_loader

    return train_loader, None


def training_loop(model_clf, train_loader, val_loader, pos_weight, epochs) -> None:
    # define loss (or criterion) for training
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight, dtype=torch.float32))
    # define training accuracy metric
    train_metric = BinaryAccuracy(multidim_average="global")
    # define validation accuracy metric
    val_metric = BinaryAccuracy(multidim_average="global")

    # define the optimizer for the learning step
    optimizer = optim.Adam(model_clf.parameters(), lr=1e-2)

    # build the training loop
    for epoch in range(epochs + 1):
        # define loss counters and set them to zero
        train_loss = 0.0
        valid_loss = 0.0

        # set model to train
        model_clf.train()
        for (x_train, y_train) in train_loader:
            pred = model_clf(x_train)
            loss = criterion(pred, y_train.unsqueeze(dim=1))

            train_loss += loss.item()

            # batch accuracy
            train_metric(pred, y_train.unsqueeze(dim=1))

            # clear gradients
            optimizer.zero_grad()
            # compute gradients
            loss.backward()
            # learning step
            optimizer.step()

        # accuracy on all batches using custom accumulation
        train_acc = train_metric.compute()

        # set model to evaluate
        model_clf.eval()
        with torch.no_grad():
            for x_val, y_val in val_loader:
                logit = model_clf(x_val)
                val_loss = criterion(logit, y_val.unsqueeze(dim=1))

                valid_loss += val_loss.item()
                # batch validation accuracy
                val_metric(logit, y_val.unsqueeze(dim=1))

        valid_acc = val_metric.compute()

        if epoch % 5 == 0:
            print(f"Epoch: {epoch}")
            print(f"Train loss: {train_loss / len(train_loader)}, Train acc: {train_acc}")
            print(f"Val loss: {valid_loss / len(val_loader)}, Val acc: {valid_acc}")

        # Reseting internal state such that metric ready for new data
        train_metric.reset()
        # Reseting internal state such that metric ready for new data
        val_metric.reset()

    print("Training done!")


def testing_loop(model_clf, test_loader, pos_weight) -> None:
    """

    Args:
        model_clf:
        test_loader:
        pos_weight:

    Returns:

    """
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight, dtype=torch.float32))
    # define test binary accuracy metric
    test_metric = BinaryAccuracy(multidim_average="global")
    # define test binary receiver operator curve metric
    metric_roc = BinaryROC()
    # define test binary area under the ROC curve metric
    test_auc = BinaryAUROC()
    model_clf.eval()
    with torch.no_grad():
        for (x_test, y_test) in test_loader:
            pred = model_clf(x_test)
            val_loss = criterion(pred, y_test.unsqueeze(dim=1))

            test_metric(pred, y_test.unsqueeze(dim=1))
            test_auc(pred, y_test.unsqueeze(dim=1))
            metric_roc(pred, y_test.unsqueeze(dim=1).int())
    # compute total test accuracy
    test_acc = test_metric.compute()
    test_auc = test_auc.compute()
    test_roc = metric_roc.compute()

    # plot  obtained ROC
    fig_, ax_ = metric_roc.plot(score=True)
    plt.show()


def model_bn_inference(model_clf, target, predictions,
                       confusion_matrix: bool = False,
                       task_type: str = "binary",
                       n_classes: int = 2):
    # Convert predictors and target into tensors
    predictor_tensor = torch.tensor(predictions.values,
                                    dtype=torch.float32)
    true_label_tensor = torch.tensor(target.values,
                                     dtype=torch.float32)

    # Standardize the predictors
    pmean = predictor_tensor.mean()
    pstd = predictor_tensor.std()
    predictor_tensor = (predictor_tensor - pmean) / pstd
    # Make inference between 0 and 1
    inference = F.sigmoid(model_clf(predictor_tensor))
    # Compute confusion matrix
    if confusion_matrix:
        bcm = ConfusionMatrix(task=task_type,
                              num_classes=n_classes)
        bcm = bcm(inference, true_label_tensor.unsqueeze(dim=1))
        return bcm, inference

    return inference
