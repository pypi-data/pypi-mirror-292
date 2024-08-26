![ICON_OPI_LOGO_BLANCO_Horizontal.png](ICON_OPI_LOGO_BLANCO_Horizontal.png)

# OPI Solutions: Predictive Maintenance 

## About

### How to install

pip install --upgrade pip

pip install opipy-pm==0.1.0

## Examples

### Binary Classifier Training

```{python}
# Import classifier from Models package
from opipy_pm.Models.nn.Torch.Classifier import BinaryClassifier
from opipy_pm.Models.nn.Torch.Classifier import training_loop, data_loader
from opipy_pm.Models.nn.Torch.Classifier import pos_class_weight, data_splitter

pos_weight = pos_class_weight(df=df, target="machine_failure")
pred_cols: list[str] = ["torque", "tool_wear"]
Xtrain, Ytrain, Xval, Yval = data_splitter(df=df,
                                           pred_cols=pred_cols,
                                           test_size=0.2,
                                           holdout=True
                                           )

# instantiate the binary classification class
dim: int = len(pred_cols)
model_clf = BinaryClassifier(in_dim=dim)
model_clf._init_weights_()

train_loader, val_loader = data_loader(Xtrain, Ytrain, Xval, Yval)
epochs: int = 100
training_loop(model_clf, train_loader, val_loader, pos_weight, epochs)
```