import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


st.set_page_config(page_title="篮球比赛数据统计分析软件", layout="wide")


EXPECTED_COLUMNS = [
    "TEAM_NAME",
    "GAME_DATE",
    "WL",
    "PTS",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PLUS_MINUS",
    "SEASON",
]

NUMERIC_COLUMNS = [
    "PTS",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PLUS_MINUS",
    "eFG_PCT",
    "AST_RATE",
    "THREE_P_RATE",
    "WIN_BIN",
]

CORE_METRICS = [
    "PTS",
    "FG_PCT",
    "FG3_PCT",
    "REB",
    "AST",
    "STL",
    "BLK",
    "PF",
    "TOV",
    "PLUS_MINUS",
    "eFG_PCT",
    "AST_RATE",
    "THREE_P_RATE",
]

METRIC_LABELS = {
    "PTS": "得分",
    "FG_PCT": "投篮命中率",
    "FG3_PCT": "三分命中率",
    "REB": "篮板",
    "AST": "助攻",
    "STL": "抢断",
    "BLK": "盖帽",
    "PF": "犯规",
    "OREB": "前场篮板",
    "DREB": "后场篮板",
    "TOV": "失误",
    "PLUS_MINUS": "净胜分",
    "eFG_PCT": "有效命中率",
    "AST_RATE": "助攻率",
    "THREE_P_RATE": "三分出手占比",
    "WIN_BIN": "胜负二元变量",
}

PERCENT_METRICS = {"FG_PCT", "FG3_PCT", "FT_PCT", "eFG_PCT", "AST_RATE", "THREE_P_RATE"}

MODULE_OPTIONS = [
    "首页说明",
    "模块一：球队画像",
    "模块二：指定对手比较",
    "模块三：胜负因素分析",
    "模块四：建议",
]

MODULE_DESCRIPTIONS = {
    "模块一：球队画像": "查看球队自身特征、与联盟整体水平对比结果和整体风格画像",
    "模块二：指定对手比较": "比较本队与指定对手的均值差异，并进行 t 检验",
    "模块三：胜负因素分析": "观察赢球和输球比赛的关键差异，并分析与胜负的相关性",
    "模块四：建议": "结合统计结果给出具体建议",
}

def format_metric(metric: str, value: float) -> str:
    if pd.isna(value):
        return "N/A"
    if metric in PERCENT_METRICS:
        return f"{value:.1%}"
    return f"{value:.2f}"


def inject_global_text_styles():
    st.markdown(
        """
<style>
[data-testid="stMetricLabel"] {
    color: #46566e !important;
    font-size: 1.12rem !important;
    font-weight: 600 !important;
}
.helper-text {
    font-size: 1.14rem;
    line-height: 1.9;
    color: #1f2d47;
    font-weight: 600;
    margin: 0.35rem 0 0.9rem 0;
}
section[data-testid="stSidebar"] h2 {
    font-size: 1.48rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 1.34rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] .sidebar-upload-label {
    font-size: 1.32rem !important;
    font-weight: 600 !important;
    color: #1f2d47 !important;
    margin: 0.35rem 0 0.45rem 0 !important;
}
section[data-testid="stSidebar"] .sidebar-field-label {
    font-size: 1.24rem !important;
    font-weight: 600 !important;
    color: #1f2d47 !important;
    margin: 0.55rem 0 0.35rem 0 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    font-size: 1.18rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    font-size: 1.18rem !important;
    color: #1f2d47 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    font-size: 1.16rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #edf4ff !important;
    border: 1px solid rgba(44, 92, 168, 0.12) !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label,
section[data-testid="stSidebar"] [role="radiogroup"] div {
    font-size: 1.16rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > label {
    display: none !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div {
    font-size: 1.18rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    min-height: 210px !important;
    padding: 1.15rem 1rem !important;
    border-radius: 18px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] div,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span {
    font-size: 1.18rem !important;
    color: #1f2d47 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    font-size: 1.24rem !important;
    padding: 0.9rem 1.35rem !important;
    min-height: 56px !important;
    margin-top: 0.75rem !important;
}
[data-testid="stAlert"] {
    font-size: 1.14rem !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div {
    font-size: 1.14rem !important;
    line-height: 1.85 !important;
    color: #1f2d47 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_helper_text(text: str):
    st.markdown(f'<div class="helper-text">{text}</div>', unsafe_allow_html=True)


def style_plotly_figure(fig: go.Figure, height: int | None = None):
    layout_args = dict(
        font=dict(size=16, color="#46566e"),
        legend=dict(font=dict(size=15, color="#46566e"), title=dict(font=dict(size=15, color="#46566e"))),
        xaxis=dict(
            title_font=dict(size=17, color="#46566e"),
            tickfont=dict(size=15, color="#46566e"),
        ),
        yaxis=dict(
            title_font=dict(size=17, color="#46566e"),
            tickfont=dict(size=15, color="#46566e"),
        ),
    )
    if height is not None:
        layout_args["height"] = height
    fig.update_layout(**layout_args)
    return fig


def build_vertical_box_scatter(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    color_map: dict[str, str],
    legend_title: str,
    x_title: str,
    y_title: str,
    height: int = 420,
) -> go.Figure:
    plot_df = df[[group_col, value_col]].copy()
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[group_col, value_col])

    fig = go.Figure()
    categories = [str(item) for item in plot_df[group_col].dropna().unique().tolist()]

    for index, category in enumerate(categories):
        values = plot_df.loc[plot_df[group_col] == category, value_col].dropna()
        if values.empty:
            continue

        q1, median, q3 = values.quantile([0.25, 0.5, 0.75]).tolist()
        color = color_map.get(category, "#4c78a8")

        fig.add_trace(
            go.Box(
                name=category,
                x0=index,
                q1=[q1],
                median=[median],
                q3=[q3],
                lowerfence=[values.min()],
                upperfence=[values.max()],
                boxpoints=False,
                width=0.38,
                fillcolor="rgba(76, 120, 168, 0.35)" if color == "#4c78a8" else "rgba(118, 181, 255, 0.35)",
                line=dict(color=color, width=2),
                marker=dict(color=color),
                legendgroup=category,
                showlegend=True,
            )
        )

    fig.update_layout(
        height=height,
        margin=dict(t=20, b=20, l=20, r=20),
        title_text="",
        boxmode="group",
        legend_title_text=legend_title,
    )
    fig.update_xaxes(
        title_text=x_title,
        tickmode="array",
        tickvals=list(range(len(categories))),
        ticktext=categories,
        type="linear",
        range=[-0.5, max(len(categories) - 0.5, 0.5)],
    )
    fig.update_yaxes(title_text=y_title)
    return style_plotly_figure(fig, height=height)


def significance_text(p_value: float) -> str:
    if pd.isna(p_value):
        return "样本不足，无法判断显著性"
    if p_value < 0.01:
        return "在 1% 显著性水平下差异显著"
    if p_value < 0.05:
        return "在 5% 显著性水平下差异显著"
    return "未达到常用显著性水平，暂不能认为差异显著"


def correlation_label(value: float) -> str:
    value = abs(value)
    if value < 0.1:
        return "几乎无线性相关"
    if value < 0.3:
        return "弱相关"
    if value < 0.5:
        return "中等相关"
    if value < 0.7:
        return "较强相关"
    return "强相关"


@st.cache_data
def read_table(source):
    name = str(getattr(source, "name", source)).lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(source)
    if name.endswith(".txt"):
        return pd.read_table(source)
    return pd.read_csv(source)


def parse_opponent(matchup: str) -> str | None:
    if pd.isna(matchup):
        return None
    text = str(matchup)
    if "vs." in text:
        return text.split("vs.")[-1].strip()
    if "@" in text:
        return text.split("@")[-1].strip()
    return None


def parse_home_away(matchup: str) -> str | None:
    if pd.isna(matchup):
        return None
    text = str(matchup)
    if "vs." in text:
        return "主场"
    if "@" in text:
        return "客场"
    return None


def preprocess_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df_raw.copy()
    df.columns = [str(col).strip().upper() for col in df.columns]

    if "GAME_DATE" in df.columns:
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "WL" in df.columns and "WIN_BIN" not in df.columns:
        df["WIN_BIN"] = df["WL"].astype(str).str.upper().eq("W").astype(int)
    elif "WIN_BIN" in df.columns:
        df["WIN_BIN"] = pd.to_numeric(df["WIN_BIN"], errors="coerce").fillna(0).astype(int)

    if "MATCHUP" in df.columns:
        df["HOME_AWAY"] = df["MATCHUP"].apply(parse_home_away)
        df["OPPONENT"] = df["MATCHUP"].apply(parse_opponent)

    if "eFG_PCT" not in df.columns and {"FGM", "FG3M", "FGA"}.issubset(df.columns):
        attempts = df["FGA"].replace(0, np.nan)
        df["eFG_PCT"] = (df["FGM"] + 0.5 * df["FG3M"]) / attempts

    if "AST_RATE" not in df.columns and {"AST", "FGM"}.issubset(df.columns):
        makes = df["FGM"].replace(0, np.nan)
        df["AST_RATE"] = df["AST"] / makes

    if "THREE_P_RATE" not in df.columns and {"FG3A", "FGA"}.issubset(df.columns):
        attempts = df["FGA"].replace(0, np.nan)
        df["THREE_P_RATE"] = df["FG3A"] / attempts

    if {"OREB", "REB"}.issubset(df.columns):
        total_reb = df["REB"].replace(0, np.nan)
        df["OREB_SHARE"] = df["OREB"] / total_reb

    if {"DREB", "REB"}.issubset(df.columns):
        total_reb = df["REB"].replace(0, np.nan)
        df["DREB_SHARE"] = df["DREB"] / total_reb

    if {"TOV", "FGA"}.issubset(df.columns):
        attempts = df["FGA"].replace(0, np.nan)
        df["TOV_FACTOR"] = df["TOV"] / attempts

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]

    if "SEASON" in df.columns:
        df["SEASON"] = df["SEASON"].astype(str)

    if "TEAM_NAME" in df.columns:
        df["TEAM_NAME"] = df["TEAM_NAME"].astype(str)

    return df, missing_columns


def metric_summary(series: pd.Series) -> dict[str, float]:
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return {
            "均值": np.nan,
            "中位数": np.nan,
            "标准差": np.nan,
        }
    mean_value = cleaned.mean()
    std_value = cleaned.std(ddof=1)
    return {
        "均值": mean_value,
        "中位数": cleaned.median(),
        "标准差": std_value,
    }


def safe_ttest(series_a: pd.Series, series_b: pd.Series) -> dict[str, float]:
    a = pd.to_numeric(series_a, errors="coerce").dropna()
    b = pd.to_numeric(series_b, errors="coerce").dropna()
    if len(a) < 2 or len(b) < 2:
        return {"t": np.nan, "p": np.nan, "n_a": len(a), "n_b": len(b)}

    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)
    return {"t": t_stat, "p": p_value, "n_a": len(a), "n_b": len(b)}


def build_overview_table(team_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in ["PTS", "FG_PCT", "FG3_PCT", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS", "eFG_PCT"]:
        if metric not in team_df.columns:
            continue
        summary = metric_summary(team_df[metric])
        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "均值": format_metric(metric, summary["均值"]),
                "中位数": format_metric(metric, summary["中位数"]),
                "标准差": format_metric(metric, summary["标准差"]),
            }
        )
    return pd.DataFrame(rows)


def build_combined_overview_table(team_df: pd.DataFrame, league_df: pd.DataFrame) -> pd.DataFrame:
    comparison_df = build_league_comparison(team_df, league_df)
    comparison_map = comparison_df.set_index("metric_key").to_dict("index") if not comparison_df.empty else {}

    rows = []
    for metric in ["PTS", "FG_PCT", "FG3_PCT", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS", "eFG_PCT"]:
        if metric not in team_df.columns:
            continue
        summary = metric_summary(team_df[metric])
        comparison = comparison_map.get(metric, {})
        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "均值": format_metric(metric, summary["均值"]),
                "中位数": format_metric(metric, summary["中位数"]),
                "标准差": format_metric(metric, summary["标准差"]),
                "联盟均值": format_metric(metric, comparison.get("联盟均值", np.nan)),
                "差值": format_metric(metric, comparison.get("差值", np.nan)),
                "结论": comparison.get("结论", "N/A"),
            }
        )
    return pd.DataFrame(rows)


def build_profile_scorecards(team_df: pd.DataFrame, league_df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    profile_map = {
        "进攻": [("PTS", False), ("eFG_PCT", False), ("AST", False), ("THREE_P_RATE", False), ("TOV", True)],
        "防守": [("REB", False), ("STL", False), ("BLK", False), ("PF", True), ("PLUS_MINUS", False)],
    }
    team_means = team_df.mean(numeric_only=True)
    league_team_means = league_df.groupby("TEAM_NAME", as_index=False).mean(numeric_only=True)

    rows = []
    category_scores = {}
    for category, metrics in profile_map.items():
        scaled_values = []
        for metric, reverse in metrics:
            if metric not in team_df.columns or metric not in league_team_means.columns:
                continue
            team_value = team_means.get(metric, np.nan)
            metric_series = pd.to_numeric(league_team_means[metric], errors="coerce").dropna()
            if pd.isna(team_value) or metric_series.empty:
                continue
            league_mean = metric_series.mean()
            league_std = metric_series.std(ddof=1)
            if pd.isna(league_mean) or pd.isna(league_std) or league_std == 0:
                continue
            relative_score = (team_value - league_mean) / league_std
            if reverse:
                relative_score = -relative_score
            scaled_values.append(relative_score)
            rows.append({"类别": category, "指标": METRIC_LABELS.get(metric, metric), "标准化得分": relative_score})
        category_scores[category] = float(np.mean(scaled_values)) if scaled_values else np.nan

    style_label = "攻守均衡型"
    offense_score = category_scores.get("进攻", np.nan)
    defense_score = category_scores.get("防守", np.nan)
    if pd.notna(offense_score) and pd.notna(defense_score):
        if offense_score - defense_score > 0.25:
            style_label = "偏进攻型"
        elif defense_score - offense_score > 0.25:
            style_label = "偏防守型"

    return pd.DataFrame(rows), style_label


def build_style_explanation(profile_df: pd.DataFrame, style_label: str) -> str:
    if profile_df.empty:
        return "当前样本不足，暂时无法稳定判断球队的攻防风格"

    category_scores = profile_df.groupby("类别")["标准化得分"].mean()
    offense_score = category_scores.get("进攻", np.nan)
    defense_score = category_scores.get("防守", np.nan)

    offense_text = f"进攻综合表现为 {offense_score:.2f}" if pd.notna(offense_score) else "进攻综合表现暂不可用"
    defense_text = f"防守综合表现为 {defense_score:.2f}" if pd.notna(defense_score) else "防守综合表现暂不可用"

    if style_label == "偏进攻型":
        return f"{offense_text}，{defense_text}，说明球队相对更依赖得分效率、组织和进攻输出建立优势，整体画像偏进攻型"
    if style_label == "偏防守型":
        return f"{offense_text}，{defense_text}，说明球队在篮板、抢断、盖帽或限制犯规等防守相关维度更突出，整体画像偏防守型"
    return f"{offense_text}，{defense_text}，两类得分接近，说明球队没有明显单边倾向，整体更接近攻守均衡型"


def build_team_style_quadrant(league_df: pd.DataFrame) -> pd.DataFrame:
    profile_map = {
        "进攻得分": [("PTS", False), ("eFG_PCT", False), ("AST", False), ("THREE_P_RATE", False), ("TOV", True)],
        "防守得分": [("REB", False), ("STL", False), ("BLK", False), ("PF", True), ("PLUS_MINUS", False)],
    }
    group_df = league_df.groupby("TEAM_NAME", as_index=False).mean(numeric_only=True)
    if group_df.empty:
        return pd.DataFrame()

    for score_name, metrics in profile_map.items():
        available_metrics = [metric for metric, _ in metrics if metric in group_df.columns]
        if not available_metrics:
            group_df[score_name] = np.nan
            continue

        relative_components = []
        for metric, reverse in metrics:
            if metric not in group_df.columns:
                continue
            series = group_df[metric]
            mean_value = series.mean()
            metric_range = series.max() - series.min()
            if pd.isna(mean_value) or pd.isna(metric_range) or metric_range == 0:
                continue
            relative_series = (series - mean_value) / metric_range
            if reverse:
                relative_series = -relative_series
            relative_components.append(relative_series)

        if relative_components:
            group_df[score_name] = pd.concat(relative_components, axis=1).mean(axis=1)
        else:
            group_df[score_name] = np.nan

    return group_df[["TEAM_NAME", "进攻得分", "防守得分"]].dropna()


def build_league_comparison(team_df: pd.DataFrame, league_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in CORE_METRICS:
        if metric not in team_df.columns or metric not in league_df.columns:
            continue

        league_series = pd.to_numeric(league_df[metric], errors="coerce").dropna()
        team_series = pd.to_numeric(team_df[metric], errors="coerce").dropna()
        if league_series.empty or team_series.empty:
            continue

        team_mean = team_series.mean()
        league_mean = league_series.mean()
        diff_value = team_mean - league_mean
        relative_diff = (diff_value / abs(league_mean)) if pd.notna(league_mean) and league_mean not in (0, 0.0) else np.nan
        direction = (
            "明显高于平均"
            if pd.notna(relative_diff) and relative_diff >= 0.08
            else "明显低于平均"
            if pd.notna(relative_diff) and relative_diff <= -0.08
            else "接近联盟平均"
        )

        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "metric_key": metric,
                "本队均值": team_mean,
                "联盟均值": league_mean,
                "差值": diff_value,
                "相对差值": relative_diff,
                "结论": direction,
            }
        )
    return pd.DataFrame(rows)


def build_opponent_comparison(team_df: pd.DataFrame, opponent_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in ["PTS", "FG_PCT", "FG3_PCT", "REB", "AST", "TOV", "PLUS_MINUS", "eFG_PCT"]:
        if metric not in team_df.columns or metric not in opponent_df.columns:
            continue
        test_result = safe_ttest(team_df[metric], opponent_df[metric])
        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "本队均值": pd.to_numeric(team_df[metric], errors="coerce").mean(),
                "对手均值": pd.to_numeric(opponent_df[metric], errors="coerce").mean(),
                "t 值": test_result["t"],
                "p 值": test_result["p"],
                "统计解释": significance_text(test_result["p"]),
            }
        )
    return pd.DataFrame(rows)


def build_win_loss_comparison(team_df: pd.DataFrame) -> pd.DataFrame:
    if "WL" not in team_df.columns:
        return pd.DataFrame()

    win_df = team_df[team_df["WL"].astype(str).str.upper() == "W"]
    loss_df = team_df[team_df["WL"].astype(str).str.upper() == "L"]
    if win_df.empty or loss_df.empty:
        return pd.DataFrame()

    rows = []
    for metric in ["PTS", "REB", "AST", "TOV", "FG3_PCT", "THREE_P_RATE", "eFG_PCT"]:
        if metric not in team_df.columns:
            continue
        test_result = safe_ttest(win_df[metric], loss_df[metric])
        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "赢球均值": pd.to_numeric(win_df[metric], errors="coerce").mean(),
                "输球均值": pd.to_numeric(loss_df[metric], errors="coerce").mean(),
                "差值": pd.to_numeric(win_df[metric], errors="coerce").mean() - pd.to_numeric(loss_df[metric], errors="coerce").mean(),
                "p 值": test_result["p"],
                "统计解释": significance_text(test_result["p"]),
            }
        )
    return pd.DataFrame(rows)


def build_correlation_table(team_df: pd.DataFrame) -> pd.DataFrame:
    if "WIN_BIN" not in team_df.columns:
        return pd.DataFrame()

    rows = []
    for metric in ["PTS", "REB", "AST", "TOV", "FG3_PCT", "THREE_P_RATE", "eFG_PCT"]:
        if metric not in team_df.columns:
            continue
        data = team_df[[metric, "WIN_BIN"]].dropna()
        if len(data) < 3 or data[metric].nunique() < 2:
            continue
        corr, p_value = stats.pearsonr(data[metric], data["WIN_BIN"])
        rows.append(
            {
                "指标": METRIC_LABELS.get(metric, metric),
                "相关系数 r": corr,
                "p 值": p_value,
                "解释": f"{correlation_label(corr)}；{significance_text(p_value)}",
            }
        )
    return pd.DataFrame(rows).sort_values(by="相关系数 r", key=lambda col: col.abs(), ascending=False)


def build_recommendations(
    team_name: str,
    league_cmp: pd.DataFrame,
    win_loss_cmp: pd.DataFrame,
    correlation_table: pd.DataFrame,
) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []
    used_metrics: set[str] = set()

    if not league_cmp.empty:
        for metric in ["eFG_PCT", "TOV", "REB"]:
            subset = league_cmp[league_cmp["metric_key"] == metric]
            if subset.empty:
                continue
            row = subset.iloc[0]
            if metric == "eFG_PCT" and pd.notna(row["相对差值"]) and row["相对差值"] <= -0.05:
                suggestions.append(
                    {
                        "统计发现": f"{team_name}的有效命中率低于联盟平均",
                        "证据说明": f"eFG% 均值为{row['本队均值']:.1%}，联盟均值为{row['联盟均值']:.1%}，相对差值为{row['相对差值']:.1%}",
                        "篮球建议": "优先提升高质量出手比例，增加篮下终结和空位三分，减少低效率强投",
                    }
                )
                used_metrics.add("有效命中率")
            if metric == "TOV" and pd.notna(row["相对差值"]) and row["相对差值"] >= 0.08:
                suggestions.append(
                    {
                        "统计发现": f"{team_name}的失误偏多",
                        "证据说明": f"场均失误{row['本队均值']:.2f} 次，高于联盟均值{row['联盟均值']:.2f}次，相对差值为{row['相对差值']:.1%}",
                        "篮球建议": "降低高风险传导比例，优化后卫出球选择，重点训练半场阵地战的决策稳定性",
                    }
                )
                used_metrics.add("失误")
            if metric == "REB" and pd.notna(row["相对差值"]) and row["相对差值"] <= -0.08:
                suggestions.append(
                    {
                        "统计发现": f"{team_name}的篮板保护弱于联盟平均",
                        "证据说明": f"场均篮板{row['本队均值']:.2f}，联盟均值{row['联盟均值']:.2f}，相对差值为{row['相对差值']:.1%}",
                        "篮球建议": "加强卡位和弱侧收板，优先提升防守回合结束能力，减少对手二次进攻",
                    }
                )
                used_metrics.add("篮板")

    if not win_loss_cmp.empty:
        significant = win_loss_cmp[win_loss_cmp["p 值"] < 0.05].sort_values(by="p 值", ascending=True)
        significant = significant[~significant["指标"].isin(used_metrics)]
        if not significant.empty:
            row = significant.iloc[0]
            metric_label = row["指标"]
            direction = "更高" if row["差值"] > 0 else "更低"
            advice_text = "保持这一优势，并将其作为比赛计划中的优先目标" if row["差值"] > 0 else "把这个短板当作重点修正对象，赛前准备和轮换要围绕它做补强"
            suggestions.append(
                {
                    "统计发现": f"{metric_label}在赢球与输球比赛中存在显著差异",
                    "证据说明": f"赢球均值为{row['赢球均值']:.2f}，输球均值为{row['输球均值']:.2f}，p 值为{row['p 值']:.4f}",
                    "篮球建议": f"赢球时该指标通常{direction}，建议在临场策略中优先围绕{metric_label}进行资源配置{advice_text}",
                }
            )
            used_metrics.add(metric_label)

    if not correlation_table.empty:
        available_corr = correlation_table[
            (correlation_table["p 值"] < 0.05) & (~correlation_table["指标"].isin(used_metrics))
        ]
        if not available_corr.empty:
            top_corr = available_corr.iloc[0]
            relation = "正相关" if top_corr["相关系数 r"] > 0 else "负相关"
            suggestions.append(
                {
                    "统计发现": f"{top_corr['指标']}与胜负结果呈 {relation}",
                    "证据说明": f"Pearson r = {top_corr['相关系数 r']:.3f}，p 值 = {top_corr['p 值']:.4f}",
                    "篮球建议": f"比赛准备中应持续监控{top_corr['指标']}，把它作为影响比赛结果的重点过程指标",
                }
            )
            used_metrics.add(top_corr["指标"])


    if not suggestions:
        suggestions.append(
            {
                "统计发现": "当前样本下尚未发现足够强的显著性结论",
                "证据说明": "可能原因是样本量偏小，或球队多项指标接近联盟平均",
                "篮球建议": "首版仍建议继续积累比赛样本，并优先关注 eFG%、失误和篮板这三类经典效率指标",
            }
        )

    return suggestions[:4]


def show_method_note(title: str, description: str):
    st.markdown(
        f'<div style="font-size:1.22rem; line-height:1.95; color:#1f2d47; font-weight:600; margin:0.45rem 0 1rem 0;">{title}：{description}</div>',
        unsafe_allow_html=True,
    )


def render_page_header(module_name: str, team_name: str, compare_team: str | None):
    compare_text = compare_team if compare_team else "未选择"
    compare_line = (
        f'<div style="font-size:1.16rem; line-height:1.9; color:#1f2d47; font-weight:500;">当前球队：<b>{team_name}</b> ｜ 对手比较：<b>{compare_text}</b></div>'
        if module_name == "模块二：指定对手比较"
        else ""
    )
    description = MODULE_DESCRIPTIONS.get(module_name, "分析球队数据的当前模块")
    st.markdown(
        f"""
### {module_name}
{compare_line}

<div style="font-size:1.16rem; line-height:1.9; color:#1f2d47; font-weight:500;">{description}</div>
"""
        ,
        unsafe_allow_html=True,
    )
    st.divider()


def render_intro(missing_columns: list[str]):
    st.title("篮球比赛数据统计分析软件")
    st.markdown(
        """

- 数据描述与可视化
- 与指定对手比较
- 胜负差异检验与相关性分析
- 结合统计结果给出具体建议
"""
    )
    if missing_columns:
        st.warning(f"当前文件缺少以下预期字段：{', '.join(missing_columns)}相关模块会自动降级，但页面不会中断")
    else:
        st.success("数据结构完整，所有核心分析模块均可运行")


def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str | None, str]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("数据设置")
    seasons = sorted(df["SEASON"].dropna().astype(str).unique().tolist()) if "SEASON" in df.columns else []
    st.sidebar.markdown('<div class="sidebar-field-label">选择赛季</div>', unsafe_allow_html=True)
    selected_seasons = st.sidebar.multiselect(
        "选择赛季",
        seasons,
        default=seasons[:1] if seasons else None,
        label_visibility="collapsed",
    )
    filtered_df = df[df["SEASON"].astype(str).isin(selected_seasons)].copy() if selected_seasons else df.copy()

    teams = sorted(filtered_df["TEAM_NAME"].dropna().astype(str).unique().tolist()) if "TEAM_NAME" in filtered_df.columns else []
    if not teams:
        st.error("当前数据中缺少 TEAM_NAME，无法继续分析")
        st.stop()

    st.sidebar.markdown('<div class="sidebar-field-label">目标球队</div>', unsafe_allow_html=True)
    target_team = st.sidebar.selectbox("目标球队", teams, label_visibility="collapsed")
    opponents = [team for team in teams if team != target_team]
    st.sidebar.markdown('<div class="sidebar-field-label">指定对手（可选）</div>', unsafe_allow_html=True)
    compare_team = st.sidebar.selectbox(
        "指定对手（可选）",
        ["不比较"] + opponents,
        label_visibility="collapsed",
    )
    st.sidebar.subheader("页面导航")
    module_options = MODULE_OPTIONS.copy()
    module_name = st.sidebar.radio("切换模块", module_options, index=0, label_visibility="collapsed")
    return filtered_df, target_team, None if compare_team == "不比较" else compare_team, module_name


def render_overview(team_df: pd.DataFrame, league_df: pd.DataFrame, team_name: str):
    show_method_note("方法说明", "用均值、中位数、标准差描述球队自身特征，再结合联盟均值、差值判断球队所处位置")

    wins = int(team_df["WIN_BIN"].sum()) if "WIN_BIN" in team_df.columns else 0
    total_games = len(team_df)
    win_rate = wins / total_games if total_games else np.nan

    st.markdown(
        """
<style>
.overview-card {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
    border-radius: 22px;
    padding: 1rem 1.1rem 0.6rem 1.1rem;
    box-shadow: 0 12px 28px rgba(28, 44, 76, 0.05);
    margin-bottom: 1rem;
}
.overview-card-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #1f2d47;
    margin-bottom: 0.45rem;
}
.overview-card-text {
    color: #4f6078;
    font-size: 1.14rem;
    line-height: 1.95;
    margin-bottom: 0.4rem;
}
.overview-equal-card {
    min-height: 108px;
}
.overview-align-box {
    min-height: 88px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 0.1rem 0 0.85rem 0;
}
.overview-inline-select-label {
    font-size: 1.14rem;
    line-height: 1.9;
    color: #1f2d47;
    font-weight: 500;
    margin: 0.15rem 0 0.5rem 0;
}
.overview-selectbox div[data-baseweb="select"] > div {
    font-size: 1.14rem !important;
    color: #1f2d47 !important;
}
.overview-note-box {
    min-height: 78px;
    display: flex;
    align-items: center;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    background: #eef5ff;
    color: #355a8c;
    font-size: 1.14rem;
    line-height: 1.95;
    margin: 0.15rem 0 0.9rem 0;
}
.overview-note-box.empty {
    background: transparent;
    border: none;
    color: transparent;
    box-shadow: none;
}
.overview-stat {
    padding: 0.2rem 0 0.4rem 0;
}
.overview-stat-label {
    color: #46566e;
    font-size: 1.18rem;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 0.45rem;
}
.overview-stat-value {
    color: #1f2d47;
    font-size: 2.3rem;
    font-weight: 500;
    line-height: 1.1;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
<div class="overview-stat">
    <div class="overview-stat-label">样本场次</div>
    <div class="overview-stat-value">{total_games}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
<div class="overview-stat">
    <div class="overview-stat-label">胜率</div>
    <div class="overview-stat-value">{f"{win_rate:.1%}" if pd.notna(win_rate) else "N/A"}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
<div class="overview-stat">
    <div class="overview-stat-label">场均得分</div>
    <div class="overview-stat-value">{format_metric("PTS", team_df["PTS"].mean()) if "PTS" in team_df.columns else "N/A"}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
<div class="overview-stat">
    <div class="overview-stat-label">场均净胜分</div>
    <div class="overview-stat-value">{format_metric("PLUS_MINUS", team_df["PLUS_MINUS"].mean()) if "PLUS_MINUS" in team_df.columns else "N/A"}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    overview_table = build_combined_overview_table(team_df, league_df)
    st.markdown(
        """
<div class="overview-card">
    <div class="overview-card-title">核心指标总览</div>
    <div class="overview-card-text">先看球队自身表现，再和联盟均值对照，快速判断哪些指标明显偏强、偏弱或接近平均</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.table(overview_table.set_index("指标"))

    radar_metrics = ["PTS", "REB", "AST", "STL", "BLK", "eFG_PCT", "THREE_P_RATE"]
    available = [metric for metric in radar_metrics if metric in team_df.columns]
    comparison_df = build_league_comparison(team_df, league_df)
    top_left, top_right = st.columns(2, gap="large")
    if available:
        standardized = []
        for metric in available:
            value = pd.to_numeric(team_df[metric], errors="coerce").mean()
            if metric in PERCENT_METRICS:
                standardized.append(float(value) * 100)
            else:
                standardized.append(float(value))
        standardized.append(standardized[0])
        labels = [METRIC_LABELS.get(metric, metric) for metric in available]
        labels.append(labels[0])
        radar = go.Figure()
        radar.add_trace(
            go.Scatterpolar(
                r=standardized,
                theta=labels,
                fill="toself",
                name=team_name,
                line=dict(color="#c0392b"),
            )
        )
        radar.update_layout(
            height=460,
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=False,
            margin=dict(t=20, b=56, l=72, r=36),
        )
        style_plotly_figure(radar, height=460)
        with top_left:
            st.markdown(
                """
<div class="overview-card">
    <div class="overview-equal-card">
    <div class="overview-card-title">图 1：球队综合画像</div>
    <div class="overview-card-text">用一张图查看球队在得分、篮板、组织和防守维度上的整体轮廓，适合做风格概览</div>
    </div>
</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="overview-align-box" style="min-height: 148px;"></div>', unsafe_allow_html=True)
            st.plotly_chart(radar, use_container_width=True)
            st.markdown("<div style='height: 88px;'></div>", unsafe_allow_html=True)
            render_helper_text("读图提示：轮廓越向外，说明该方向表现越突出；更适合看整体风格，不适合比较不同量纲的绝对大小")

    if not comparison_df.empty:
        with top_right:
            st.markdown(
                """
<div class="overview-card">
    <div class="overview-equal-card">
    <div class="overview-card-title">图 2：与联盟整体水平比较</div>
    <div class="overview-card-text">比较目标球队与联盟样本的某一具体指标，查看这一项指标是高于平均、接近平均还是相对偏低</div>
    </div>
</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="overview-align-box">', unsafe_allow_html=True)
            st.markdown('<div class="overview-inline-select-label">选择一个指标与联盟整体水平比较</div>', unsafe_allow_html=True)
            st.markdown('<div class="overview-selectbox">', unsafe_allow_html=True)
            box_metric = st.selectbox(
                "选择一个指标与联盟整体水平比较",
                [METRIC_LABELS.get(metric, metric) for metric in comparison_df["metric_key"]],
                key="league_metric",
                label_visibility="collapsed",
            )
            st.markdown("</div></div>", unsafe_allow_html=True)
            metric_key = comparison_df.loc[comparison_df["指标"] == box_metric, "metric_key"].iloc[0]
            plot_df = league_df[[metric_key, "TEAM_NAME"]].dropna().copy()
            plot_df["类型"] = np.where(plot_df["TEAM_NAME"] == team_name, team_name, "联盟样本")
            fig = build_vertical_box_scatter(
                plot_df,
                group_col="类型",
                value_col=metric_key,
                color_map={"联盟样本": "#1368c4", team_name: "#7ec3ff"},
                legend_title="类型",
                x_title="类型",
                y_title=metric_key,
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<div style='height: 52px;'></div>", unsafe_allow_html=True)
            render_helper_text("读图提示：箱线图展示当前样本的数据分布，上下限对应最大值与最小值，箱体与中位线可用于比较数据整体分布水平")

    profile_df, style_label = build_profile_scorecards(team_df, league_df)
    if not profile_df.empty:
        style_explanation = build_style_explanation(profile_df, style_label)
        profile_fig = px.bar(
            profile_df,
            x="指标",
            y="标准化得分",
            color="类别",
            barmode="group",
            title="球队在进攻与防守维度上的标准化表现",
        )
        profile_fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.markdown(
            f"""
<div class="overview-card">
    <div class="overview-equal-card">
    <div class="overview-card-title">图 3：攻防倾向</div>
    <div class="overview-card-text">将核心指标转换为 Z 分数后再比较，更方便判断球队是偏进攻、偏防守，还是更接近均衡型<br>当前判定：<b>{style_label}</b></div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="overview-note-box">风格判定说明：{style_explanation}</div>', unsafe_allow_html=True)

        chart_col, explain_col = st.columns([1.1, 0.9], gap="large")
        with chart_col:
            style_plotly_figure(profile_fig, height=420)
            st.plotly_chart(profile_fig, use_container_width=True)
            render_helper_text("读图提示：Z 分数以 0 为联盟平均水平，柱状高于 0 表示高于联盟平均，低于 0 表示低于联盟平均；绝对值越大，说明该指标偏离联盟平均越明显")

        with explain_col:
            st.markdown("<div style='height: 72px;'></div>", unsafe_allow_html=True)
            st.markdown(
                """
<div class="overview-card">
    <div class="overview-card-title">图 3 解释</div>
    <div class="overview-card-text">
        <b>计算公式：</b> Z = (球队指标均值 - 联盟球队均值) / 联盟球队标准差<br>
        <b>读图方法：</b> 0 表示联盟平均；大于 0 表示高于平均；小于 0 表示低于平均<br>
        <b>方向统一：</b> 失误、犯规这类“越低越好”的指标在计算后做了反向处理，因此柱子越高代表表现越好<br>
        <b>综合判定：</b> 进攻类指标和防守类指标分别取平均，得到“进攻综合表现”和“防守综合表现”，再据此判断球队更偏进攻、偏防守还是攻守均衡
    </div>
    </div>
</div>
                """,
                unsafe_allow_html=True,
            )


def render_opponent_comparison(team_df: pd.DataFrame, opponent_df: pd.DataFrame | None, opponent_name: str | None):
    show_method_note("方法说明", "用两独立样本 t 检验比较两队赛季表现差异，并结合 p 值判断差异是否显著")

    st.markdown(
        """
<style>
.module-card {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
    border-radius: 22px;
    padding: 1rem 1.1rem 0.6rem 1.1rem;
    box-shadow: 0 12px 28px rgba(28, 44, 76, 0.05);
    margin-bottom: 1rem;
}
.module-card-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #1f2d47;
    margin-bottom: 0.45rem;
}
.module-card-text {
    color: #4f6078;
    font-size: 1.14rem;
    line-height: 1.95;
    margin-bottom: 0.4rem;
}
.inline-select-label {
    font-size: 1.14rem;
    line-height: 1.9;
    color: #1f2d47;
    font-weight: 500;
    margin: 0.15rem 0 0.5rem 0;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    font-size: 1.14rem !important;
    color: #1f2d47 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    if opponent_df is None or opponent_name is None:
        st.info("左侧未选择指定对手，本模块暂不展示")
        return pd.DataFrame()

    comparison_df = build_opponent_comparison(team_df, opponent_df)
    if comparison_df.empty:
        st.info("当前数据不足以完成对手比较")
        return comparison_df

    display_df = comparison_df.copy()
    for metric_key, label in METRIC_LABELS.items():
        mask = display_df["指标"] == label
        if mask.any():
            display_df.loc[mask, "本队均值"] = display_df.loc[mask, "本队均值"].map(lambda x, metric=metric_key: format_metric(metric, x))
            display_df.loc[mask, "对手均值"] = display_df.loc[mask, "对手均值"].map(lambda x, metric=metric_key: format_metric(metric, x))
    display_df["t 值"] = comparison_df["t 值"].map(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A")
    display_df["p 值"] = comparison_df["p 值"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
    st.markdown(
        f"""
<div class="module-card">
    <div class="module-card-title">核心比较结果</div>
    <div class="module-card-text">集中展示本队与 <b>{opponent_name}</b> 在主要指标上的均值差异、t 值、p 值和统计解释，总体把握两队主要差异</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.table(display_df.set_index("指标"))

    st.markdown(
        """
<div class="module-card">
    <div class="module-card-title">分布比较图</div>
    <div class="module-card-text">选择一个指标，直接比较本队和指定对手在该指标上的数据整体分布</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="inline-select-label">选择一项指标查看双队分布</div>', unsafe_allow_html=True)
    plot_metric = st.selectbox(
        "选择一项指标查看双队分布",
        comparison_df["指标"].tolist(),
        key="opp_metric",
        label_visibility="collapsed",
    )
    reverse_map = {value: key for key, value in METRIC_LABELS.items()}
    metric_key = reverse_map.get(plot_metric, plot_metric)
    pair_df = pd.concat(
        [
            team_df[[metric_key]].assign(球队="目标球队"),
            opponent_df[[metric_key]].assign(球队=opponent_name),
        ],
        ignore_index=True,
    )
    pair_fig = build_vertical_box_scatter(
        pair_df,
        group_col="球队",
        value_col=metric_key,
        color_map={"目标球队": "#1368c4", opponent_name: "#7ec3ff"},
        legend_title="球队",
        x_title="球队",
        y_title=metric_key,
        height=430,
    )
    st.plotly_chart(pair_fig, use_container_width=True)
    render_helper_text("读图提示：箱线图展示当前样本的数据分布，上下限对应最大值与最小值，箱体与中位线可用于比较数据整体分布水平")
    return comparison_df


def render_win_loss(team_df: pd.DataFrame):
    show_method_note("方法说明", "先比较赢球与输球比赛相关指标的均值差异、进行显著性检验，再用相关性分析判断哪些指标与胜负结果关联更强")

    st.markdown(
        """
<style>
.module-card {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
    border-radius: 22px;
    padding: 1rem 1.1rem 0.6rem 1.1rem;
    box-shadow: 0 12px 28px rgba(28, 44, 76, 0.05);
    margin-bottom: 1rem;
}
.module-card-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #1f2d47;
    margin-bottom: 0.45rem;
}
.module-card-text {
    color: #4f6078;
    font-size: 1.14rem;
    line-height: 1.95;
    margin-bottom: 0.4rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    win_loss_df = build_win_loss_comparison(team_df)
    if win_loss_df.empty:
        st.info("当前球队缺少足够的胜负样本，无法完成该模块")
        return pd.DataFrame(), pd.DataFrame()

    display_df = win_loss_df.copy()
    reverse_map = {value: key for key, value in METRIC_LABELS.items()}
    for label in display_df["指标"].tolist():
        metric_key = reverse_map.get(label, label)
        mask = display_df["指标"] == label
        display_df.loc[mask, "赢球均值"] = display_df.loc[mask, "赢球均值"].map(lambda x, metric=metric_key: format_metric(metric, x))
        display_df.loc[mask, "输球均值"] = display_df.loc[mask, "输球均值"].map(lambda x, metric=metric_key: format_metric(metric, x))
        display_df.loc[mask, "差值"] = display_df.loc[mask, "差值"].map(lambda x, metric=metric_key: format_metric(metric, x))
    display_df["p 值"] = win_loss_df["p 值"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
    st.markdown(
        """
<div class="module-card">
    <div class="module-card-title">胜负差异结果</div>
    <div class="module-card-text">对比赢球与输球比赛的关键指标均值，查看哪些指标在两种比赛结果下差异更明显</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.table(display_df.set_index("指标"))

    corr_df = build_correlation_table(team_df)
    if not corr_df.empty:
        corr_display = corr_df.copy()
        corr_display["相关系数 r"] = corr_display["相关系数 r"].map(lambda x: f"{x:.3f}")
        corr_display["p 值"] = corr_display["p 值"].map(lambda x: f"{x:.4f}")
        st.markdown(
            """
<div class="module-card">
    <div class="module-card-title">胜负相关性排序</div>
    <div class="module-card-text">把主要指标与胜负结果的相关系数放在一起，便于判断哪些指标与赢球相关性更强</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.table(corr_display.set_index("指标"))

        corr_plot = px.bar(
            corr_df,
            x="指标",
            y="相关系数 r",
            color="相关系数 r",
            color_continuous_scale="RdBu",
            title="各指标与胜负结果的相关系数",
        )
        corr_plot.update_layout(margin=dict(t=60, b=20, l=20, r=20))
        style_plotly_figure(corr_plot, height=430)
        st.markdown(
            """
<div class="module-card">
    <div class="module-card-title">相关性图</div>
    <div class="module-card-text">柱形越高表示正相关越强，柱形越低表示负相关越强，便于直观看到关键影响因素</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(corr_plot, use_container_width=True)
        render_helper_text("读图提示：正值越大说明该指标升高时更容易赢球，负值越小则说明该指标升高可能更不利于比赛结果")

    return win_loss_df, corr_df


def render_recommendations(recommendations: list[dict[str, str]]):
    st.markdown(
        """
<style>
.module-card {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
    border-radius: 22px;
    padding: 1rem 1.1rem 0.9rem 1.1rem;
    box-shadow: 0 12px 28px rgba(28, 44, 76, 0.05);
    margin-bottom: 1rem;
}
.module-card-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #1f2d47;
    margin-bottom: 0.7rem;
}
.module-card-text {
    color: #334866;
    font-size: 1.14rem;
    line-height: 2.0;
    margin-bottom: 0.35rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    for index, item in enumerate(recommendations, start=1):
        st.markdown(
            f"""
<div class="module-card">
    <div class="module-card-title">建议 {index}</div>
    <div class="module-card-text"><b>统计发现：</b>{item['统计发现']}</div>
    <div class="module-card-text"><b>证据说明：</b>{item['证据说明']}</div>
    <div class="module-card-text"><b>篮球建议：</b>{item['篮球建议']}</div>
</div>
"""
            ,
            unsafe_allow_html=True,
        )


def render_home_page(team_df: pd.DataFrame, team_name: str, compare_team: str | None, missing_columns: list[str], data_source: str):
    win_rate_text = f"{team_df['WIN_BIN'].mean():.1%}" if "WIN_BIN" in team_df.columns else "N/A"
    avg_pts_text = format_metric("PTS", team_df["PTS"].mean()) if "PTS" in team_df.columns else "N/A"

    st.markdown(
        """
<style>
.home-shell {
    padding-top: 0.6rem;
}
.home-hero {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background:
        radial-gradient(circle at top left, rgba(118, 167, 255, 0.14), transparent 34%),
        radial-gradient(circle at bottom right, rgba(122, 217, 196, 0.16), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, #f7faff 100%);
    border-radius: 28px;
    padding: 2.2rem 2.3rem;
    box-shadow: 0 20px 50px rgba(28, 44, 76, 0.08);
    min-height: 540px;
}
.home-title {
    font-size: 3rem;
    line-height: 1.08;
    font-weight: 800;
    color: #1e2b45;
    margin: 0;
}
.home-title-soft {
    color: #1e2b45;
}
.home-bullet {
    margin: 1rem 0 0 0;
    padding-left: 1.15rem;
    color: #44556f;
    font-size: 1.12rem;
    line-height: 2.0;
}
.home-bullet li {
    font-size: 1.12rem;
    line-height: 2.0;
}
.home-panel {
    border-radius: 24px;
    padding: 1.2rem;
    background: rgba(255, 255, 255, 0.90);
    border: 1px solid rgba(40, 61, 102, 0.10);
    box-shadow: 0 16px 36px rgba(28, 44, 76, 0.05);
    display: grid;
    grid-template-rows: auto auto 1fr auto;
    gap: 0.85rem;
    min-height: 540px;
}
.home-panel-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
}
.home-panel-title {
    font-size: 1.24rem;
    font-weight: 700;
    color: #20304d;
}
.home-chip {
    background: #edf4ff;
    color: #2c5ca8;
    border-radius: 999px;
    padding: 0.25rem 0.65rem;
    font-size: 1.04rem;
    font-weight: 600;
}
.home-panel-box {
    border-radius: 18px;
    background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    border: 1px solid rgba(52, 86, 140, 0.10);
    padding: 1rem;
}
.home-panel-box + .home-panel-box {
    margin-top: 0;
}
.home-kicker {
    color: #53647d;
    font-size: 1.12rem;
    margin-bottom: 0.35rem;
}
.home-big {
    font-size: 2.22rem;
    font-weight: 800;
    color: #1d2b45;
}
.home-list {
    margin: 0.5rem 0 0 0;
    padding-left: 1.05rem;
    color: #46566e;
    font-size: 1.16rem;
    line-height: 2.0;
}
.home-stats-list {
    margin: 0.55rem 0 0 0;
    padding-left: 1.05rem;
    color: #46566e;
    font-size: 1.16rem;
    line-height: 2.0;
}
.home-stats-list li {
    font-size: 1.16rem;
    line-height: 2.0;
}
.home-status {
    margin-top: 1rem;
    border-radius: 16px;
    padding: 0.95rem 1rem;
    background: #eef9f0;
    color: #2b7a44;
    font-size: 1.16rem;
    line-height: 1.9;
}
.home-status.warn {
    background: #fff5e8;
    color: #9a621c;
}
.home-source {
    margin-top: 0.9rem;
    color: #5e6e86;
    font-size: 1.12rem;
}
.home-card {
    border-radius: 22px;
    padding: 1.2rem 1.15rem;
    background: #ffffff;
    border: 1px solid rgba(40, 61, 102, 0.10);
    box-shadow: 0 14px 30px rgba(28, 44, 76, 0.05);
    height: 100%;
    min-height: 152px;
}
.home-card-title {
    color: #1f2d47;
    font-size: 1.22rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.home-card-text {
    color: #4d5e76;
    line-height: 1.95;
    font-size: 1.14rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    status_html = (
        f'<div class="home-status warn">当前文件缺少字段：{", ".join(missing_columns)}相关模块会自动降级，但页面不会中断</div>'
        if missing_columns
        else '<div class="home-status">数据结构完整，所有核心分析模块均可运行</div>'
    )

    st.markdown('<div class="home-shell">', unsafe_allow_html=True)
    hero_left, hero_right = st.columns([1.45, 1], gap="large")

    with hero_left:
        st.markdown(
            f"""
<div class="home-hero">
    <h1 class="home-title">篮球比赛数据统计分析软件</h1>
    <ul class="home-bullet">
        <li>数据描述与可视化</li>
        <li>与指定对手比较</li>
        <li>胜负差异检验与相关性分析</li>
        <li>结合统计结果给出具体建议</li>
    </ul>
    {status_html}
    <div class="home-source">当前数据源：{data_source}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with hero_right:
        st.markdown(
            f"""
<div class="home-panel">
    <div class="home-panel-top">
        <div class="home-panel-title">界面预览</div>
        <div class="home-chip">4 个模块</div>
    </div>
    <div class="home-panel-box">
        <div class="home-kicker">当前分析对象</div>
        <div class="home-big">{team_name}</div>
        <ul class="home-stats-list">
            <li>样本场次：{len(team_df)}</li>
            <li>胜率：{win_rate_text}</li>
            <li>场均得分：{avg_pts_text}</li>
        </ul>
    </div>
    <div class="home-panel-box">
        <div class="home-kicker">使用方式</div>
        <ul class="home-stats-list">
            <li>左侧可切换赛季、球队和分析模块</li>
            <li>当前对手比较：{compare_team if compare_team else '未选择'}</li>
            <li>切换模块查看不同统计结果</li>
        </ul>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    card1, card2, card3 = st.columns(3, gap="large")
    with card1:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">模块一</div>
    <div class="home-card-text">查看球队整体画像、自身数据分布、并与联盟均值对照，快速建立球队风格印象</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with card2:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">模块二与模块三</div>
    <div class="home-card-text">结合t 检验比较与对手差异，利用相关性分析解释哪些指标和赢球、输球更有关系</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with card3:
        st.markdown(
            """
<div class="home-card">
    <div class="home-card-title">模块四</div>
    <div class="home-card-text">结合统计分析结果，给出针对性建议</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_landing_page():
    st.markdown(
        """
<style>
.landing-shell {
    padding: 1.2rem 0 0.6rem 0;
}
.landing-hero {
    border: 1px solid rgba(40, 61, 102, 0.10);
    background:
        radial-gradient(circle at top left, rgba(118, 167, 255, 0.16), transparent 34%),
        radial-gradient(circle at bottom right, rgba(122, 217, 196, 0.18), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, #f6f9ff 100%);
    border-radius: 28px;
    padding: 2.4rem 2.4rem 2.1rem 2.4rem;
    box-shadow: 0 20px 50px rgba(28, 44, 76, 0.08);
    min-height: 470px;
}
.landing-title {
    font-size: 3.2rem;
    line-height: 1.08;
    font-weight: 800;
    color: #1e2b45;
    margin: 0;
}
.landing-subtitle {
    font-size: 1.16rem;
    line-height: 2.0;
    color: #485872;
    margin-top: 1rem;
    max-width: 42rem;
}
.landing-note {
    margin-top: 2rem;
    color: #2d5b9a;
    font-weight: 600;
    font-size: 1.38rem;
    line-height: 1.8;
}
.landing-preview {
    height: 100%;
    min-height: 470px;
    border-radius: 24px;
    padding: 1.2rem;
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(40, 61, 102, 0.10);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
}
.preview-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.preview-brand {
    font-weight: 700;
    color: #20304d;
    font-size: 1.24rem;
}
.preview-chip {
    background: #edf4ff;
    color: #2c5ca8;
    border-radius: 999px;
    padding: 0.25rem 0.65rem;
    font-size: 1.04rem;
    font-weight: 600;
}
.preview-panel {
    border-radius: 18px;
    background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    border: 1px solid rgba(52, 86, 140, 0.10);
    padding: 1rem;
}
.preview-panel + .preview-panel {
    margin-top: 0.85rem;
}
.preview-kicker {
    color: #53647d;
    font-size: 1.42rem;
    font-weight: 800;
    color: #1f2d47;
    margin-bottom: 0.7rem;
}
.preview-list {
    margin: 0.55rem 0 0 0;
    padding-left: 1.05rem;
    color: #46566e;
    font-size: 1.16rem;
    line-height: 2.0;
}
.preview-list li {
    font-size: 1.16rem;
    line-height: 2.0;
}
.landing-card {
    border-radius: 22px;
    padding: 1.2rem 1.15rem;
    background: #ffffff;
    border: 1px solid rgba(40, 61, 102, 0.10);
    box-shadow: 0 14px 30px rgba(28, 44, 76, 0.05);
    height: 100%;
    min-height: 152px;
}
.landing-card-title {
    color: #1f2d47;
    font-size: 1.22rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.landing-card-text {
    color: #43556f;
    line-height: 1.95;
    font-size: 1.14rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="landing-shell">', unsafe_allow_html=True)
    hero_left, hero_right = st.columns([1.22, 1], gap="large")

    with hero_left:
        st.markdown(
            """
<div class="landing-hero">
    <h1 class="landing-title">篮球比赛数据统计分析软件</h1>
    <div class="landing-subtitle">
        用球队多场比赛数据完成数据描述与可视化、与指定对手比较、胜负因素分析，给出针对性建议
    </div>
    <div class="landing-note">从左侧上传比赛数据文件后，即可进入完整分析界面</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with hero_right:
        st.markdown(
            """
<div class="landing-preview">
    <div class="preview-topbar">
        <div class="preview-brand">界面预览</div>
        <div class="preview-chip">4 个模块</div>
    </div>
    <div class="preview-panel">
        <div class="preview-kicker">核心功能</div>
        <ul class="preview-list">
            <li>球队数据分布并与联盟均值比较</li>
            <li>与指定对手差异检验</li>
            <li>胜负关键因素分析</li>
        </ul>
    </div>
    <div class="preview-panel">
        <div class="preview-kicker">使用方式</div>
        <ul class="preview-list">
            <li>上传本地 CSV / Excel / TXT 文件</li>
            <li>按赛季与球队筛选分析对象</li>
            <li>切换模块查看不同统计结果</li>
        </ul>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    card1, card2, card3 = st.columns(3, gap="large")
    with card1:
        st.markdown(
            """
<div class="landing-card">
    <div class="landing-card-title">球队画像</div>
    <div class="landing-card-text">集中查看球队得分、命中率、篮板、助攻、防守指标，并与联盟整体水平比较，快速建立整体画像</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with card2:
        st.markdown(
            """
<div class="landing-card">
    <div class="landing-card-title">与指定对手比较及胜负关键因素分析</div>
    <div class="landing-card-text">结合t 检验和相关性分析，解释与对手差异以及哪些指标更可能影响比赛结果</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with card3:
        st.markdown(
            """
<div class="landing-card">
    <div class="landing-card-title">建议</div>
    <div class="landing-card-text">结合统计分析结果，给出针对性建议</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    inject_global_text_styles()
    st.sidebar.header("文件导入")
    st.sidebar.markdown('<div class="sidebar-upload-label">上传本地 CSV / Excel / TXT 文件</div>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("上传本地 CSV / Excel / TXT 文件", type=["csv", "xlsx", "xls", "txt"], label_visibility="collapsed")

    if uploaded_file is None:
        render_landing_page()
        return

    df_raw = read_table(uploaded_file)
    data_source = f"上传文件：{uploaded_file.name}"
    df, missing_columns = preprocess_data(df_raw)

    filtered_df, target_team, compare_team, module_name = render_sidebar(df)
    team_df = filtered_df[filtered_df["TEAM_NAME"] == target_team].copy()
    opponent_df = filtered_df[filtered_df["TEAM_NAME"] == compare_team].copy() if compare_team else None

    if team_df.empty:
        st.error("当前筛选条件下没有找到目标球队的数据")
        return

    if "GAME_DATE" in team_df.columns:
        team_df = team_df.sort_values("GAME_DATE")

    league_cmp = build_league_comparison(team_df, filtered_df)
    win_loss_cmp = build_win_loss_comparison(team_df)
    correlation_df = build_correlation_table(team_df)
    recommendations = build_recommendations(target_team, league_cmp, win_loss_cmp, correlation_df)

    home_module = MODULE_OPTIONS[0]
    overview_module = MODULE_OPTIONS[1]
    opponent_module = MODULE_OPTIONS[2]
    win_loss_module = MODULE_OPTIONS[3]
    advice_module = MODULE_OPTIONS[4]

    if module_name == home_module:
        render_home_page(team_df, target_team, compare_team, missing_columns, data_source)
    else:
        render_page_header(module_name, target_team, compare_team)

    if module_name == overview_module:
        render_overview(team_df, filtered_df, target_team)
    elif module_name == opponent_module:
        render_opponent_comparison(team_df, opponent_df, compare_team)
    elif module_name == win_loss_module:
        render_win_loss(team_df)
    elif module_name == advice_module:
        render_recommendations(recommendations)

    with st.expander("查看原始比赛数据"):
        st.dataframe(team_df.head(50), use_container_width=True)

    export_df = team_df.copy()
    st.download_button(
        "下载当前分析数据 CSV",
        data=export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{target_team}_analysis_data.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    main()
