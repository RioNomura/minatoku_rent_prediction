import gc
import time
import csv
from retry import retry
import requests
from bs4 import BeautifulSoup

# 不動産サイトのURL
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13103&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1"

@retry(tries=3, delay=5, backoff=2)
def get_html(url):
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.content, "html.parser")

def save_data(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

max_page = 65

for page in range(1, max_page+1):
    print(f"現在 {page}/{max_page} ページを処理中...")
    
    url = base_url.format(page)
    
    try:
        soup = get_html(url)
        
        items = soup.findAll("div", {"class": "cassetteitem"})
        print(f"ページ {page}: {len(items)} 件の物件を取得")
        
        page_data = []
        
        for item in items:
            stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
            
            for station in stations:
                base_data = {
                    "名称": item.find("div", {"class": "cassetteitem_content-title"}).getText().strip(),
                    "カテゴリー": item.find("div", {"class": "cassetteitem_content-label"}).getText().strip(),
                    "アドレス": item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip(),
                    "アクセス": station.getText().strip(),
                    "築年数": item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip(),
                    "構造": item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip(),
                }
                
                tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
                
                for tbody in tbodys:
                    data = base_data.copy()
                    data.update({
                        "階数": tbody.findAll("td")[2].getText().strip(),
                        "家賃": tbody.findAll("td")[3].findAll("li")[0].getText().strip(),
                        "管理費": tbody.findAll("td")[3].findAll("li")[1].getText().strip(),
                        "敷金": tbody.findAll("td")[4].findAll("li")[0].getText().strip(),
                        "礼金": tbody.findAll("td")[4].findAll("li")[1].getText().strip(),
                        "間取り": tbody.findAll("td")[5].findAll("li")[0].getText().strip(),
                        "面積": tbody.findAll("td")[5].findAll("li")[1].getText().strip(),
                        "URL": "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href"),
                    })
                    page_data.append(data)
        
        save_data(page_data, "minato-ku_data.csv")
        print(f"ページ {page} のデータを保存しました。合計 {len(page_data)} 件")
        
        # メモリ解放
        del soup, items, page_data
        gc.collect()
        
        # リクエスト間隔を設定
        time.sleep(5)
        
    except Exception as e:
        print(f"ページ {page} の処理中にエラーが発生しました: {e}")
        continue

print("全てのページの処理が完了しました。")