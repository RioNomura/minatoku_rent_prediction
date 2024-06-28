import pandas as pd

# データの読み込み
df = pd.read_csv("minato-ku_data.csv")

# アクセスの欠損値がある箇所は行ごと削除
df.dropna(how="any", inplace=True)

# アクセスを最寄駅とアクセスに分割
df["最寄駅"] = df["アクセス"].apply(lambda x: x.split(" ")[0])
df["アクセス"] = df["アクセス"].apply(lambda x: x.split(" ")[1])

# 数字のみ抽出（"歩"と"分"を除外）
df["アクセス"] = df["アクセス"].apply(lambda x: ''.join(filter(str.isdigit, x)))

# 最寄駅の沿線は削除
df["最寄駅"] = df["最寄駅"].apply(lambda x: x.split("/")[1])

# 築年数
df["築年数"] = df["築年数"].apply(lambda x: x.strip("築年").replace("新", "0"))
df["築年数"] = pd.to_numeric(df["築年数"])

# 階数
df["階数"] = df["階数"].apply(lambda x: x.replace("階", "").replace("B", "-").split("-")[0])
df["階数"] = pd.to_numeric(df["階数"])

# 家賃
df["家賃"] = df["家賃"].apply(lambda x: float(x.replace("万円", "")) * 10000)

# 管理費
df["管理費"] = df["管理費"].apply(lambda x: float(x.replace("円", "").replace("-", "0")))

# 敷金
df["敷金"] = df["敷金"].apply(lambda x: float(x.replace("万円", "").replace("-", "0")) * 10000)

# 礼金
df["礼金"] = df["礼金"].apply(lambda x: float(x.replace("万円", "").replace("-", "0")) * 10000)

# 面積
df["面積"] = df["面積"].apply(lambda x: float(x.replace("m2", "")))

# 構造
df["構造"] = df["構造"].apply(lambda x: x.replace("階建", "").replace("地下1地上", "").replace("地下2地上", ""))
df["構造"] = pd.to_numeric(df["構造"])

# 管理費（円）と単位を揃える
df["家賃+管理費"] = df["家賃"] + df["管理費"]

# 最寄駅をダミー変数に変換
dummy_df = pd.get_dummies(df[['最寄駅']], drop_first=True)
df = pd.concat([df, dummy_df], axis=1)

# 不要な列を削除
df = df.drop(["名称", "カテゴリー", "アドレス", "間取り", "URL", "敷金", "礼金", "家賃", "管理費", "最寄駅"], axis=1)

# 列名を変更
df.columns = ["アクセス", "築年数", "階数", "構造", "面積", "家賃+管理費"] + ["station_" + str(i) for i in range(1, len(df.columns) - 5)]

# 前処理後のデータを保存
df.to_csv("minato-ku_data2.csv", index=False)
