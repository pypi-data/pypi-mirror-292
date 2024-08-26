import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import torch
import time

import torch.nn.functional as F
from sklearn.feature_selection import f_classif
from utils.functional import feature_selection
from Models.nn.Torch.Classifier import (BinaryClassifier,
                                        data_splitter,
                                        data_loader,
                                        pos_class_weight,
                                        training_loop)


def feature_selection_plot(df: pd.DataFrame, nb_cols: list, target_col: str) -> alt.Chart:
    f_statistic, p_values = f_classif(df[nb_cols], df[target_col])

    data: dict[str, float] = {f: v for f, v in zip(nb_cols, f_statistic)}
    anom_df = pd.DataFrame(
        {"feature": data.keys(),
         "anova_score": data.values()},
        index=range(len(data))
    )
    anom_df.sort_values(by="anova_score", ascending=True, inplace=True)

    source = anom_df
    bars = alt.Chart(source).mark_bar(color="steelblue").encode(
        x=alt.X('anova_score:Q').title('ANOVA score'),
        y=alt.Y('feature:N').sort('-x').title("Features")
    )
    return bars.properties(
        title=alt.Title(text="One-way ANOVA"), width=400, height=400)


def prediction_state_comparison(healthy_pct: np.array, fail_pct: np.array) -> alt.Chart:
    source = pd.DataFrame({
        "state": ["healthy", "failure"],
        "value": [healthy_pct * 100, fail_pct * 100]
    })

    donut = alt.Chart(source).mark_arc(innerRadius=60).encode(
        theta="value:Q",
        color="state:N",
    )

    text = donut.mark_text(radius=170, size=12, color='white').encode(
        text="value:Q"
    )

    state_plot = (donut + text)
    return state_plot.properties(
        height=400)


def prediction_summary(model_clf, prod_id, true_label, pred_tensor) -> alt.LayerChart:
    predic_df = pd.DataFrame(
        {"product_id": prod_id.values,
         "failure_prob": F.sigmoid(model_clf(pred_tensor)).detach().numpy().reshape(-1),
         "actual_state": true_label.values
         }
    )
    predic_df_ = predic_df[["product_id", "failure_prob"]].sort_values(by="failure_prob").copy()

    source = predic_df_[["product_id", "failure_prob"]]
    threshold = 0.5

    bars = alt.Chart(source).mark_bar(color="steelblue").encode(
        x='failure_prob:Q',
        y=alt.Y('product_id:N').sort('-x')
    )

    highlight = bars.mark_bar(color="#e45755").encode(
        x2=alt.X2(datum=threshold)
    ).transform_filter(
        alt.datum.failure_proba > threshold
    )

    rule = alt.Chart(source).mark_rule().encode(
        x=alt.X(datum=threshold)
    )

    return (bars + highlight + rule).properties(width=600)

# ---------------------------------------------------------------
# --------------------------- APP -------------------------------
# ---------------------------------------------------------------


st.header("OPI Solutions", divider="rainbow")
st.write("""
    In OPI Solutions we leverage our proprietary software to develop :red[novel solutions] based on
    Advanced Analytic algorithms.
""")

col1, col2 = st.columns(2)

pg = st.navigation([st.Page("../DataAssessment.py"), st.Page("../AnalysisReport.py")])

# "with" notation
with st.sidebar:
    # st.sidebar.markdown("# Page 2 ❄️")
    st.markdown(
        """
        [streamlit.io](https://streamlit.io)
    """)
    st.subheader("Let's assess your assets", divider=True)
    dataset = st.file_uploader(label="Drag and drop files here", type=["CSV", "TXT"])
    if not dataset:
        st.error("Please upload a file at least one country.")
    else:
        # Read dataset full path and create a DataFrame
        df = pd.read_csv(dataset)

    # rename columns inplace by making names lowercase and joining with an underscore
    df.rename(
        columns={col: '_'.join(col.lower().strip().split(' ')) for col in df.columns},
        inplace=True
    )

    # Feature selections
    st.subheader("Feature selections", divider=True)
    df_columns: list[str] = list(df.columns)  # select_dtypes("number")
    # df_columns: list[str] = list(df_.select_dtypes("number").columns)

    date_feature: str = st.selectbox(
        "Is there any datetime feature?",
        df_columns, None)
    if date_feature:
        df[date_feature] = pd.to_datetime(df[date_feature])
        df.set_index(date_feature, inplace=True)
        df_columns.remove(date_feature)

    # Drop column udi which corresponds to product index
    st.write("Asset ID")
    asset_id: str = st.selectbox(
        "What's your asset ID feature?",
        df_columns)

    if asset_id:
        df_columns.remove(asset_id)

    # Select target feature
    target: str = st.selectbox(
        "What's your target feature?",
        df_columns)
    st.write("You selected:", target)
    df_columns.remove(target)

    # df: pd.DataFrame = df_[df_columns].copy()
    # df_col.remove(asset_id)

    # -------------------------------------
    # df.select_dtypes("number")
    cols = st.multiselect(
        "What are your favorite colors",
        df_columns,
        df_columns)

    top_n_feat: int = st.slider("Feature Selection: top k (sorted by feature prediction importance)",
                                min_value=2,
                                max_value=len(df_columns),
                                value=5,
                                step=1)

    # Take best top k features from ANOVA test
    top_k_pred_cols: np.array = feature_selection(df=df,
                                                  nb_cols=df_columns,
                                                  target=target,
                                                  top_n=top_n_feat)
    st.write("Top K selected features", len(top_k_pred_cols))

    # Split data into training set
    x_train, y_train, x_val, y_val = data_splitter(df=df,
                                                   pred_cols=top_k_pred_cols,
                                                   target=target,
                                                   test_size=0.2,
                                                   holdout=True)
    #train_loader, val_loader = data_loader(x_train=x_train, y_train=y_train,
     #                                      x_val_=x_val, y_val_=y_val)
    # ---------------------------------------
    # Binary classification model training section
    pw: float = pos_class_weight(df=df, target=target)
    # Activate training bottom
    model = BinaryClassifier(in_dim=len(top_k_pred_cols))
    model._init_weights_()
    #if st.button('Train model'):
       # with st.spinner("Training..."):
     #       training_loop(model_clf=model,
      #                    train_loader=train_loader,
       #                   val_loader=val_loader,
        #                  pos_weight=pw,
         #                 epochs=11
          #                )
           # time.sleep(5)
            #st.success("Training successful!")

    # Testing
    cols_: list[str] = [target, asset_id]
    nb_col: list[str] = list(top_k_pred_cols)
    # test_col: list[str] = test_col.extend(cols)
    test_sample = df[nb_col + cols_].sample(n=500).copy()
    true_label = test_sample.pop(target)
    product_id = test_sample.pop(asset_id)

    predictor_tensor = torch.tensor(test_sample.values, dtype=torch.float32)
    true_label_tensor = torch.tensor(true_label.values, dtype=torch.float32)
    predictor_tensor = (predictor_tensor - predictor_tensor.mean()) / predictor_tensor.std()

    model.to("cpu")
    infer_bool = (F.sigmoid(model(predictor_tensor)).detach().numpy() > .5).reshape(-1)
    fail_prob = infer_bool.sum() / len(infer_bool)
    healthy_prob = 1 - fail_prob

    st.button('Report', {"vertical_alignment": "bottom"})

df_to_display: pd.DataFrame = df.head(n=20)
col1.dataframe(df_to_display)

with col2.container():
    st.write("This is inside the container")

    # st.write("You selected:", cols)
    st.altair_chart(
        feature_selection_plot(
            df=df,
            nb_cols=cols,
            target_col=target
        )
    )

#st.altair_chart(
 #       prediction_state_comparison(
  #          healthy_pct=healthy_prob,
   #         fail_pct=fail_prob
    #    )
    #)

pg.run()
