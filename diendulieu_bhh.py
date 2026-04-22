import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import timedelta

# --- ANH DÁN LINK WEB APP MỚI VỪA COPY VÀO ĐÂY ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwYq2BCb2gbLZQKOOvxe2PgcBZ5DVmJ6WiSLGZvNohgstghF5r5MaHPe-zsINw1Cm7gZA/exec"

url = "http://bhh.com.vn/"
headers = {'User-Agent': 'Mozilla/5.0'}

print("⏳ Dang cao du lieu va gui sang Google Sheets...")
try:
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    all_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', soup.text)

    if all_dates:
        start_date_str = all_dates[0]
        # Doc ngay tu web (dd/mm/yyyy)
        current_date = pd.to_datetime(start_date_str, format='%d/%m/%Y')

        target_table = None
        for tb in soup.find_all('table'):
            if 'X. QUAN' in tb.text:
                target_table = tb
                break

        if target_table:
            data = []
            for row in target_table.find_all('tr'):
                cells = [c.text.strip() for c in row.find_all(['td', 'th'])]
                if len(cells) < 21: continue

                text_concat = "".join(cells)
                if any(x in text_concat for x in ['TB', 'Max', 'Min', 'Ngày']): continue

                time_val = cells[-21].lower().replace('h', '').strip()
                station_data = cells[-20:]

                if time_val not in ['1', '7', '13', '19']: continue
                if time_val == '1' and len(data) > 0:
                    current_date += timedelta(days=1)

                # DOI DINH DANG: Chuyen sang Thang/Ngay/Nam de khop voi Sheets cua anh
                date_str_formatted = current_date.strftime('%m/%d/%Y')
                station_data = [v if v != '--' else '' for v in station_data]

                data.append([date_str_formatted, time_val] + station_data)

            # Thêm dòng này để xem tận mắt 1 dòng dữ liệu
            print("DỮ LIỆU MẪU GỬI ĐI:", data[0])
            
            # Gui du lieu
            res = requests.post(WEB_APP_URL, json=data)
            print(f"Phan hoi: {res.text}")

except Exception as e:
    print(f"❌ Loi: {e}")
