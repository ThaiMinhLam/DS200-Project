import pandas as pd
import json
import time
from kafka import KafkaProducer
from pathlib import Path
import sys
sys.path.append(r'F:\Studies\Third_year\Big_data\Final_Code')
from final_src.config import Config

# import pandas as pd
# import json
# import time
# from kafka import KafkaProducer
# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[2]))
# from final_src.config import Config

# def run_csv_batch_push_kafka(config):

#     # Khởi tạo Kafka producer
#     producer = KafkaProducer(
#         bootstrap_servers=config.KAFKA_SERVERS,
#         value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
#     )

#     offset = 0  # Bắt đầu từ dòng đầu tiên

#     print(f"[SYSTEM] Start pushing CSV data from: {config.DATA_PATH}")

#     try:
#         while True:
#             # Đọc lại CSV (phòng trường hợp file có thêm dữ liệu)
#             df = pd.read_csv(config.DATA_PATH, index_col=0)
#             new_df = df[['text']]

#             total_rows = len(new_df)
#             if offset >= total_rows:
#                 print("[SYSTEM] No new records found. Sleeping 5 minutes...")
#                 time.sleep(5 * 60)
#                 continue

#             # Lấy batch kế tiếp
#             batch = new_df.iloc[offset:offset + 10]

#             # Gửi từng record vào Kafka
#             for _, row in batch.iterrows():
#                 record = row.to_dict()
#                 producer.send(config.KAFKA_TOPIC_COMMENTS, value=record)
            
#             producer.flush()

#             print(f"[SYSTEM] Pushed batch {offset} to {offset + len(batch)}. Sleeping 3 minutes...")

#             # Cập nhật offset
#             offset += len(batch)

#             # Nghỉ 3 phút trước khi đẩy batch kế tiếp
#             time.sleep(3 * 60)

#     except KeyboardInterrupt:
#         print("[SYSTEM] Stopped by user.")

#     finally:
#         producer.flush()
#         producer.close()
#         print("[SYSTEM] Kafka producer closed cleanly.")

def run_csv_batch_push_kafka(config):
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )

    offset = 0

    print(f"[SYSTEM] Start pushing CSV data from: {config.DATA_PATH}")

    try:
        df = pd.read_csv(config.DATA_PATH, index_col=0)
        new_df = df[['text']]
        total_rows = len(new_df)

        while offset < total_rows:
            batch = new_df.iloc[offset:offset + 1000]

            for _, row in batch.iterrows():
                record = row.to_dict()
                producer.send(config.KAFKA_TOPIC_COMMENTS, value=record)

            producer.flush()
            print(f"[SYSTEM] Pushed batch {offset} to {offset + len(batch)}. Sleeping 3 minutes...")

            offset += len(batch)
            time.sleep(3 * 60)  # Nghỉ đúng 3 phút

        print("[SYSTEM] All records pushed successfully.")

    except KeyboardInterrupt:
        print("[SYSTEM] Stopped by user.")

    finally:
        producer.flush()
        producer.close()
        print("[SYSTEM] Kafka producer closed cleanly.")
