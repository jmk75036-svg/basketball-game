# 篮球比赛数据统计分析软件

这是一个基于 `Streamlit` 开发的篮球比赛数据分析项目，面向课程展示、答辩汇报和本地数据练习。应用支持上传本地球队单场比赛数据文件，对球队表现进行统计分析，并以中文页面展示分析结果。

## 主要功能

- 模块一：球队画像  
  查看球队整体画像、自身数据分布，并与联盟整体水平进行比较。

- 模块二：指定对手比较  
  对比本队与指定对手在主要指标上的差异，并结合 t 检验进行解释。

- 模块三：胜负因素分析  
  分析赢球与输球比赛之间的关键差异，并查看主要指标与比赛结果的相关性。

- 模块四：建议  
  根据统计分析结果，生成简洁直观的中文建议。

## 使用方式

1. 打开应用后，在左侧上传本地 `CSV / Excel / TXT` 文件。
2. 选择赛季、目标球队和指定对手。
3. 按页面导航切换不同分析模块。

## 本地运行

在项目目录下运行：

```powershell
streamlit run "basketball game data analysis app.py"
```

## 依赖安装

先安装依赖：

```powershell
pip install -r requirements.txt
```

## 数据说明

本项目主要面向球队单场比赛统计数据，常用字段包括：

- `TEAM_NAME`
- `GAME_DATE`
- `WL`
- `PTS`
- `FG_PCT`
- `FG3_PCT`
- `REB`
- `AST`
- `STL`
- `BLK`
- `TOV`
- `PF`
- `PLUS_MINUS`
- `SEASON`

如果部分字段缺失，页面中的相关模块会自动降级，但应用不会直接中断。

## 部署说明

本项目可部署到 `Streamlit Community Cloud`。部署时：

- Repository：选择当前 GitHub 仓库
- Branch：`main`
- Main file path：`basketball game data analysis app.py`

部署成功后，其他人可以直接通过网页访问。

## 项目说明

本项目用于篮球比赛数据的统计分析与展示，重点放在：

- 描述统计
- 对手比较
- 胜负因素分析
- 中文化结果展示

