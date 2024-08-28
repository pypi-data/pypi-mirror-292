# Import fundamental libraries
import numpy as np
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import StandardScaler

# Set plot parameters
mpl.rcParams["font.size"] = 8
mpl.rcParams["figure.figsize"] = [8, 7]
plt.style.use("fivethirtyeight")


# Visualize feature data distributions
def feature_data_distro(df: pd.DataFrame,
                        nb_cols: list,
                        safefig: bool = False) -> None:
    """
    PARAMETERS:
    ----------
    - df [DataFrame] :
    - nb_cols [List] :
    """
    ncols: int = len(nb_cols)
    fig, ax = plt.subplots(figsize=(20, 12), nrows=2, ncols=ncols)
    for (i, c) in enumerate(nb_cols):
        # Plot a boxplot for none binary features
        sns.boxplot(
            data=df,
            y=c,
            hue="machine_failure",
            ax=ax[0, i]
        )
        # Plot a histogram for none binary features
        sns.histplot(
            data=df,
            x=c,
            hue="machine_failure",
            ax=ax[1,i]
        )
    fig.tight_layout()
    if safefig:
        plt.savefig("figure.png")
    plt.show()


##############################
# Inspect outliers
def outlier_bound(df, feat) -> tuple:
    # Get the first quartile, Q1
    q1 = np.quantile(df[feat], .25)
    # Get the third quartile, Q3
    q3 = np.quantile(df[feat], .75)
    # Compute the inter-quartile-range, IQR
    iqr = q3 - q1
    # Obtain data lower bound
    lower_bound = q1 - 1.5*iqr
    # Obtain data upper bound
    upper_bound = q3 + 1.5*iqr

    return lower_bound, upper_bound


def outlier_inspector(df: pd.DataFrame, plot_cols: list) -> None:
    """
    PARAMETERS:
    ----------
    - df [DataFrame] :
    - plot_cols [List] :
    """
    rows: int = len(plot_cols)
    fig, ax = plt.subplots(figsize=(15,15), nrows=rows, sharex=True)
    for (i, c) in enumerate(plot_cols):
        # Obtain data lower and upper bounds
        lower_bound, upper_bound = outlier_bound(df, feat=c)

        # 
        ax[i].hlines(xmax=len(df), xmin=0, y=lower_bound, ls="dashed", color='k')
        sns.scatterplot(
            data=df,
            x=range(len(df)),
            y=c,
            hue="machine_failure",
            ax=ax[i]
        )
        ax[i].hlines(xmax=len(df), xmin=0, y=upper_bound, ls="dashed", color='k')
        ax[i].set_xlabel("Obervation")
    fig.suptitle("Outliers Visualization")
    plt.show()


##############################
# Anomaly detection
def anomaly_detection(feat: pd.Series, detector: str = "z-score") -> pd.Series:
    if detector == "z-score":
        series = feat.values.reshape(-1,1)
        z_score = (feat - np.mean(series))/np.std(series)
        deviation = (feat - np.mean(series))
        threshold = 3*np.std(series)
        anomalies = feat[np.abs(deviation) > threshold]
        return anomalies
        
    if detector == "isolation-forest":
        series = feat.values.reshape(-1,1)
        clf = IsolationForest(max_samples=100, contamination=.01, random_state=42, bootstrap=True)
        clf.fit(series)
        anomalies = clf.predict(series)
        anomalies_s = pd.Series(anomalies, index=feat.index)
        return anomalies_s


def anomalies_plot(df: pd.DataFrame, plot_cols: list, save_fig: bool = False) -> None:
    """
    PARAMETERS:
    ----------
    - df [DataFrame] :
    - plot_cols [List] :
    - save_fig [Boolean] :
    """
    rows: int = len(plot_cols)
    if rows > 2:
        fig, ax = plt.subplots(figsize=(15, 15), nrows=rows, sharex=True)
    else:
        fig, ax = plt.subplots(figsize=(15, 8), nrows=rows, sharex=True)
    for (i, c) in enumerate(plot_cols):
        # 
        lower_bound, upper_bound = outlier_bound(df, feat=c)

        # Get anomalies
        anomalies: pd.Series = anomaly_detection(feat=df[c])
        # 
        ax[i].hlines(xmax=len(df), xmin=0, y=lower_bound, ls="dashed", color='k', label='outlier_border')
        sns.scatterplot(
            data=df,
            x=range(len(df)),
            y=c,
            ax=ax[i],
            alpha=.5
        )
        sns.scatterplot(
            x=anomalies.index,
            y=anomalies,
            ax=ax[i],
            color='r', 
            edgecolors='k',
            label="Anomalies"
        )
        #plt.scatter(anomalies.index, anomalies, color='r', edgecolors='k', label="Anomalies", ax=ax[i])
        ax[i].hlines(xmax=len(df), xmin=0, y=upper_bound, ls="dashed", color='k', label='outlier_border')
        ax[i].set_xlabel("Obervation")
    plt.legend()
    fig.suptitle("Anomalies Visualization")
    plt.show()


def anomaly_plot(source: pd.DataFrame, feat: str):
    """

    Args:
        source:
        feat:

    Returns:

    """
    alt.data_transformers.disable_max_rows()

    points1 = alt.Chart(source).mark_point().encode(
        x=alt.X("observation:T", axis=alt.Axis(domainColor='g', domainOpacity=.2)),  # .title("Observations"),
        y=alt.Y(f"{feat}:Q"),  # .title(f"{anomalies.name}"
        color=alt.Color("label:N", scale=alt.Scale(range=['red', 'steelblue']))
    )

    return points1  # .properties(height=400, width=950)


def anomalies_source(df: pd.DataFrame, id_feat: str, id_n: int, feat: str) -> pd.DataFrame:
    """

    Args:
        df:
        id_feat:
        id_n:
        feat:

    Returns:

    """
    anomalies = anomaly_detection(feat=df[df[id_feat] == id_n][feat])
    source = pd.DataFrame(
        data={"observation": anomalies.index, "anomaly": anomalies.values},
        index=range(0, len(anomalies))
    )

    df2 = pd.DataFrame(
        data={
            "observation": df[df[id_feat] == id_n].index,
            feat: df[df[id_feat] == id_n][feat]
            },
        )
    df2.reset_index(drop=True, inplace=True)

    source = df2.merge(source, on="observation", how='left')
    source["label"] = source["anomaly"].map(lambda x: "normal" if pd.isnull(x) else "anomaly")
    source = source.drop(columns="anomaly").copy()

    return source


########################
# Feature Selection: One-way Anova
def feature_selection_plot(df: pd.DataFrame, nb_cols: list, target: str) -> None:
    # Make a predictors DataFrame
    p_df = df[nb_cols].copy()
    df_std = (p_df - p_df.mean()) / p_df.std()
        
    f_statistic, p_values  = f_classif(df[nb_cols], df[target])
    
    data:dict[str, float] = {f:v for f,v in zip(df_std.columns, f_statistic)}
    anom_df = pd.DataFrame(
        {"features": data.keys(),
         "anova_score": data.values()},
        index=range(len(data))
    )
    anom_df.sort_values(by="anova_score", ascending=True, inplace=True)
    # f_statistic = np.sort(f_statistic)
    sns.barplot(data=anom_df, y="features", x="anova_score", orient='h')
    plt.title("Feature Importance: One-Way Anova Score")
    plt.show()


def feature_selection(df: pd.DataFrame, nb_cols: list, target: str, top_n: int) -> np.array:
    """

    Args:
        df:
        nb_cols:
        target:
        top_n:

    Returns:

    """
    p_df = df[nb_cols].copy()
    df_std = (p_df - p_df.mean()) / p_df.std()
        
    top_k = SelectKBest(f_classif, k=top_n)
    x_new = top_k.fit_transform(df_std, df[target])

    return top_k.get_feature_names_out()


if __name__ == "__main__":
    print("")
