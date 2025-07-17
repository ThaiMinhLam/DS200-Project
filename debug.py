"""
Tìm ra bug về pattern regex trong code
"""

import re

file_path = r"D:\BigData\annotated_labels\annotate_hotels.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "r\"" in line or "r'" in line:
        try:
            # Lấy pattern thô từ dòng code (cần tùy chỉnh chính xác hơn nếu cần)
            pattern_raw = line.split("r", 1)[1].split("\"", 1)[1].rsplit("\"", 1)[0]
            re.compile(pattern_raw)
        except Exception as e:
            print(f"Lỗi tại dòng {idx + 1}: {line.strip()}")
            print(f"Error: {e}\n")