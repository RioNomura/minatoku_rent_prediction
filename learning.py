from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.svm import SVR
import lightgbm as lgb
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import onnxmltools
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
#import japanize_matplotlib

# データの読み込み
df = pd.read_csv("minato-ku_data2.csv")

# 目的変数を作成
df['total_rent'] = df['家賃+管理費']

# 説明変数と目的変数を分ける
y = df['total_rent']
X = df[['築年数', '面積', 'アクセス']]

# 学習用データと評価用データに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)

# リッジ回帰
model_1 = Ridge()
model_1.fit(X_train, y_train)
print("リッジ回帰：{}".format(model_1.score(X_test, y_test)))

# ElasticNet
model_2 = ElasticNet()
model_2.fit(X_train, y_train)
print("ElasticNet:{}".format(model_2.score(X_test, y_test)))

# サポートベクトル回帰
model_3 = SVR(kernel='linear', C=1, epsilon=0.1, gamma='auto')
model_3.fit(X_train, y_train)
print("サポートベクトル回帰：{}".format(model_3.score(X_test, y_test)))

# lightGBM
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

lgbm_params = {
    'objective': 'regression',
    'metric': 'rmse',        
    'num_leaves': 60
}

# 特徴量の名前を明示的に指定
feature_names = ['築年数', '面積', 'アクセス']

# LightGBM モデルのトレーニング
model_4 = lgb.train(
    lgbm_params,
    lgb_train,
    valid_sets=[lgb_eval],
    num_boost_round=100,
    callbacks=[lgb.early_stopping(stopping_rounds=10)],
    feature_name=feature_names  # 特徴量名を明示的に指定
)

y_pred = model_4.predict(X_test, num_iteration=model_4.best_iteration)

#print("lightGBM:{}".format(r2_score(y_test, y_pred)))

# 特徴量重要度のプロット
#plt.figure(figsize=(10, 5))
#lgb.plot_importance(model_4, ax=plt.gca(), importance_type='split')
#plt.title('特徴量重要度')
#plt.tight_layout()
#plt.show()

# 予測用の関数を定義
def predict_rent(area, access, age):
    # 入力値を2次元配列に変換
    input_data = pd.DataFrame([[age, area, access]], columns=['築年数', '面積', 'アクセス'])
    
    # LightGBMモデルで予測
    prediction = model_4.predict(input_data)[0]
    
    return prediction

# ユーザー入力を受け取る
print("\n家賃予測プログラム")
area = float(input("面積（平方メートル）を入力してください: "))
access = float(input("アクセス（最寄り駅からの徒歩分数）を入力してください: "))
age = float(input("築年数を入力してください: "))

# 予測を実行
predicted_rent = predict_rent(area, access, age)

print(f"\n予測された家賃+管理費: {predicted_rent:.2f}円")

# 特徴量重要度の情報を表示
importance = model_4.feature_importance()
feature_importance = pd.DataFrame({'feature': feature_names, 'importance': importance})
feature_importance = feature_importance.sort_values('importance', ascending=False)

print("\n特徴量重要度:")
for index, row in feature_importance.iterrows():
    print(f"{row['feature']}: {row['importance']}")

# モデルを保存
joblib.dump(model_4, 'rent_prediction_model.joblib')
