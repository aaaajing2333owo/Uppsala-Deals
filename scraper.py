import json
import datetime

def scrape_deals():
    # 模拟从 ereklamblad.se 成功获取的结构化数据
    scraped_data = [
        {"store": "ICA", "discount": "-30%", "name": "冷鲜鸡胸肉", "specs": "约 1kg / 盒", "currentPrice": "79"},
        {"store": "WILLYS", "discount": "-25%", "name": "网袋土豆", "specs": "3kg / 袋", "currentPrice": "29"},
        {"store": "HEMKÖP", "discount": "超值", "name": "红提", "specs": "500g / 盒", "currentPrice": "25"}
    ]
    
    # 将抓取到的数据写入 data.json 文件
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)
    print(f"数据已更新: {datetime.datetime.now()}")

if __name__ == "__main__":
    scrape_deals()
