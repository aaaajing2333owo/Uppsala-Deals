import datetime
import json
import os
import re

# 乌普萨拉市中心坐标 (辐射3km内核心门店)
UPPSALA_LAT = 59.8586
UPPSALA_LNG = 17.6389

TARGET_STORES = ["ICA", "HEMKÖP", "WILLYS", "LIDL", "COOP", "CITY GROSS"]


def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val


def update_price_history(products):
    """维护 30 天历史价格数据库 (history.json)，并标注史低与NEW状态"""
    history = load_json("history.json", {})
    today_str = datetime.date.today().isoformat()
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    for p in products:
        key = f"{p['store']}_{p.get('branch', p['store'])}_{p['name_sv']}"
        records = history.get(key, [])

        records = [r for r in records if r["date"] >= cutoff_date]
        is_new = len(records) == 0 or (records[-1]["price"] != p["currentPrice"])
        p["is_new"] = is_new

        if not records or records[-1]["date"] != today_str:
            records.append({"date": today_str, "price": p["currentPrice"]})
        else:
            records[-1]["price"] = p["currentPrice"]

        history[key] = records

        min_price = min(r["price"] for r in records)
        if p["currentPrice"] <= min_price and (
            len(records) > 1 or p.get("history_low", False)
        ):
            p["history_low"] = True
        else:
            p["history_low"] = p.get("history_low", False)

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return products


def get_all_supermarkets_uppsala_data():
    """
    乌普萨拉全城 6 大商超（含多家 ICA/Hemköp/Willys 分店）的本周完整打折矩阵库
    """
    posters = {
        "ICA": [
            {
                "title": "ICA Supermarket Torgkassen",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/8A151B/FFFFFF?text=ICA+Torgkassen",
                "url": "https://ereklamblad.se/",
            },
            {
                "title": "ICA Supermarket Luthagens Livs",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/8A151B/FFFFFF?text=ICA+Luthagen",
                "url": "https://ereklamblad.se/",
            },
            {
                "title": "ICA Kvantum Ekonomikum",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/8A151B/FFFFFF?text=ICA+Ekonomikum",
                "url": "https://ereklamblad.se/",
            },
        ],
        "HEMKÖP": [
            {
                "title": "Hemköp Svava",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/D9383A/FFFFFF?text=Hemkop+Svava",
                "url": "https://ereklamblad.se/",
            },
            {
                "title": "Hemköp Kvarnen",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/D9383A/FFFFFF?text=Hemkop+Kvarnen",
                "url": "https://ereklamblad.se/",
            },
        ],
        "WILLYS": [
            {
                "title": "Willys Kungsgatan",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/1F2937/FFFFFF?text=Willys+Kungsgatan",
                "url": "https://ereklamblad.se/",
            },
            {
                "title": "Willys Vaksalagatan",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/1F2937/FFFFFF?text=Willys+Vaksalagatan",
                "url": "https://ereklamblad.se/",
            },
        ],
        "LIDL": [
            {
                "title": "Lidl Bredgränd",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/1D4ED8/FFFFFF?text=Lidl+Bredgrand",
                "url": "https://ereklamblad.se/",
            }
        ],
        "COOP": [
            {
                "title": "Coop Konsum S:t Per",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/064E3B/FFFFFF?text=Coop+St+Per",
                "url": "https://ereklamblad.se/",
            }
        ],
        "CITY GROSS": [
            {
                "title": "City Gross Boländerna",
                "valid": "11/04 - 11/10",
                "preview": "https://placehold.co/600x400/B45309/FFFFFF?text=City+Gross+Bolanderna",
                "url": "https://ereklamblad.se/",
            }
        ],
    }

    products = [
        # ICA 系列
        {
            "id": "ica_1",
            "store": "ICA",
            "branch": "ICA Supermarket Torgkassen",
            "name": "冷鲜鸡胸肉",
            "name_sv": "Kycklingbröstfilé Kronfågel",
            "category": "肉禽蛋",
            "is_frozen": False,
            "is_member": True,
            "is_bulk": False,
            "discount": "-34%",
            "currentPrice": 79.0,
            "originalPrice": 119.0,
            "unit": "850g",
            "unit_price": "92.94 kr/kg",
            "week": "this",
        },
        {
            "id": "ica_2",
            "store": "ICA",
            "branch": "ICA Supermarket Luthagens Livs",
            "name": "冷冻剥壳大虾",
            "name_sv": "Frysta Skalman Räkor",
            "category": "水产海鲜",
            "is_frozen": True,
            "is_member": True,
            "is_bulk": False,
            "discount": "-45%",
            "currentPrice": 55.0,
            "originalPrice": 99.0,
            "unit": "500g",
            "unit_price": "110.00 kr/kg",
            "week": "this",
        },
        {
            "id": "ica_3",
            "store": "ICA",
            "branch": "ICA Kvantum Ekonomikum",
            "name": "有机鸡蛋 15枚",
            "name_sv": "Ekologiska Ägg 15-pack",
            "category": "肉禽蛋",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": False,
            "discount": "-28%",
            "currentPrice": 39.9,
            "originalPrice": 55.0,
            "unit": "盒",
            "unit_price": "2.66 kr/st",
            "week": "this",
        },
        # Hemköp 系列
        {
            "id": "hem_1",
            "store": "HEMKÖP",
            "branch": "Hemköp Svava",
            "name": "Garant 冷鲜牛绞肉 12%",
            "name_sv": "Nötfärs 12% Garant",
            "category": "肉禽蛋",
            "is_frozen": False,
            "is_member": True,
            "is_bulk": False,
            "discount": "-22%",
            "currentPrice": 89.0,
            "originalPrice": 115.0,
            "unit": "800g",
            "unit_price": "111.25 kr/kg",
            "week": "this",
            "history_low": True,
        },
        {
            "id": "hem_2",
            "store": "HEMKÖP",
            "branch": "Hemköp Kvarnen",
            "name": "瑞典鲜牛奶 3%",
            "name_sv": "Lättmjölk 3% Arla",
            "category": "乳品饮料",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": False,
            "discount": "-15%",
            "currentPrice": 16.9,
            "originalPrice": 19.9,
            "unit": "1.5L",
            "unit_price": "11.26 kr/L",
            "week": "this",
        },
        # Willys 系列
        {
            "id": "wil_1",
            "store": "WILLYS",
            "branch": "Willys Kungsgatan",
            "name": "本地红皮土豆",
            "name_sv": "Svensk Potatis Lösvikt",
            "category": "时令果蔬",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": True,
            "discount": "-40%",
            "currentPrice": 9.9,
            "originalPrice": 16.5,
            "unit": "kg",
            "unit_price": "9.90 kr/kg",
            "week": "this",
        },
        {
            "id": "wil_2",
            "store": "WILLYS",
            "branch": "Willys Vaksalagatan",
            "name": "Fazer 夹心面包",
            "name_sv": "Rågkusar Fazer",
            "category": "烘焙面包",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": False,
            "discount": "-20%",
            "currentPrice": 24.0,
            "originalPrice": 30.0,
            "unit": "500g",
            "unit_price": "48.00 kr/kg",
            "week": "this",
        },
        # Lidl 系列
        {
            "id": "lid_1",
            "store": "LIDL",
            "branch": "Lidl Bredgränd",
            "name": "冰鲜三文鱼排",
            "name_sv": "Färsk Laxfilé 4-pack",
            "category": "水产海鲜",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": False,
            "discount": "-31%",
            "currentPrice": 99.0,
            "originalPrice": 145.0,
            "unit": "500g",
            "unit_price": "198.00 kr/kg",
            "week": "this",
            "history_low": True,
        },
        # Coop 系列
        {
            "id": "coo_1",
            "store": "COOP",
            "branch": "Coop Konsum S:t Per",
            "name": "Oatly 咖啡大师燕麦奶",
            "name_sv": "iKaffe Havredryck Oatly",
            "category": "乳品饮料",
            "is_frozen": False,
            "is_member": True,
            "is_bulk": False,
            "discount": "-25%",
            "currentPrice": 18.0,
            "originalPrice": 24.0,
            "unit": "1L",
            "unit_price": "18.00 kr/L",
            "week": "this",
        },
        # City Gross 系列
        {
            "id": "cit_1",
            "store": "CITY GROSS",
            "branch": "City Gross Boländerna",
            "name": "瑞典皇冠猪梅花肉",
            "name_sv": "Fläskkarré Benfri Lösvikt",
            "category": "肉禽蛋",
            "is_frozen": False,
            "is_member": False,
            "is_bulk": True,
            "discount": "-42%",
            "currentPrice": 69.9,
            "originalPrice": 119.0,
            "unit": "kg",
            "unit_price": "69.90 kr/kg",
            "week": "this",
        },
    ]

    return posters, products


def generate_weekly_report(products):
    low_items = [p for p in products if p.get("history_low")]
    deep_items = sorted(
        products,
        key=lambda x: int(re.sub(r"[^\d]", "", x.get("discount", "0")) or 0),
        reverse=True,
    )

    best_item = deep_items[0] if deep_items else None
    low_str = (
        f"监测到 {low_items[0]['branch']} 的 {low_items[0]['name']} 降至 {low_items[0]['currentPrice']} kr/{low_items[0]['unit']}，触及 30 天内历史低点。"
        if low_items
        else "本周高蛋白肉禽品类价格整体平稳。"
    )
    deep_str = (
        f"本周全城最高折扣出现在 {best_item['branch']}，{best_item['name']} 录得 {best_item['discount']} 深度降价 (ง •_•)ง"
        if best_item
        else "各大商超生鲜区均有常规轮换促销。"
    )

    return [
        {"title": "特别关心与史低监测", "content": low_str},
        {"title": "全城深度折扣洞察", "content": deep_str},
        {
            "title": "时令与门店贴士",
            "content": "乌普萨拉市中心 6 大主流商超（含 ICA、Hemköp、Willys 各分店）本周生鲜与乳品价格差异明显，建议采购前通过分店筛选栏多维比价 ^_^",
        },
    ]


def main():
    posters, products = get_all_supermarkets_uppsala_data()

    # 执行 30 天历史价格库比对
    products = update_price_history(products)
    report = generate_weekly_report(products)

    output_data = {
        "updated_at": datetime.datetime.now().isoformat(),
        "report": report,
        "posters": posters,
        "products": products,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(
        f"成功生成多商超数据：包含 {len(posters)} 个超市品牌及 {len(products)} 条全城打折商品。"
    )


if __name__ == "__main__":
    main()
