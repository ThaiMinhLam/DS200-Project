# import streamlit as st
# from apify_client import ApifyClient
# from kafka import KafkaProducer
# import json
# import time
# import os
# import sys
# from pathlib import Path
# from Producer.producer import *
# from Consumer.consumer1 import *
# from config import Config
# import threading

# ner_results = []

def push_text_and_run_consumer(config, text):
    # Push text lên Kafka topic
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )
    payload = {"text": text, "url": "streamlit_user_input"}
    producer.send(config.KAFKA_TOPIC_FB_POSTS, value=payload)
    producer.flush()
    print(f"✅ Pushed text to {config.KAFKA_TOPIC_FB_POSTS}")

    # Chạy consumer ngay sau khi push
    run_consumer_extract_push_kafka(config)

# def show_realtime_ner_results(config):
#     consumer = KafkaConsumer(
#         config.FB_POST_NER_TOPIC,
#         bootstrap_servers=config.KAFKA_SERVERS,
#         auto_offset_reset='latest',
#         group_id='fb_posts_ner_viewer',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8'))
#     )
#     try:
#         for message in consumer:
#             data = message.value
#             st.write(data)
#     except KeyboardInterrupt:
#         print("Stopping NER realtime viewer.")
#     finally:
#         consumer.close()

# def main():
#     config = Config()
#     st.title("🚀 Social Listening Pipeline (Streamlit)")

#     choice = st.radio("Bạn muốn thực hiện:", ("Nhập URL Facebook để crawl", "Nhập một đoạn text để phân tích"))

#     if choice == "Nhập URL Facebook để crawl":
#         url = st.text_input("Nhập URL Facebook:")
#         if st.button("START"):
#             if url.strip() == "":
#                 st.warning("⚠️ Vui lòng nhập URL.")
#             else:
#                 config.URL = url
#                 st.success("✅ Đang chạy crawl + push + consumer song song...")

#                 producer_thread = threading.Thread(target=run_apify_facebook_crawl_push_kafka_topic(config, url))
#                 consumer1_thread = threading.Thread(target=run_consumer_extract_push_kafka(config))
#                 ner_viewer_thread = threading.Thread(target=show_realtime_ner_results(config))
                
#                 consumer1_thread.start()
#                 producer_thread.start()
#                 ner_viewer_thread.start()

#                 producer_thread.join()
#                 consumer1_thread.join()
#                 ner_viewer_thread.join()

#                 st.info("⏳ Đang chạy song song, theo dõi log terminal để xem tiến trình.")

#     elif choice == "Nhập một đoạn text để phân tích":
#         text = st.text_area("Nhập nội dung:")
#         if st.button("Push Text và Chạy Consumer song song"):
#             if text.strip() == "":
#                 st.warning("⚠️ Vui lòng nhập nội dung.")
#             else:
#                 st.success("✅ Đang push text và chạy consumer song song...")

#                 producer_thread = threading.Thread(target=push_text_and_run_consumer(config,text))
#                 consumer1_thread = threading.Thread(target=run_consumer_extract_push_kafka(config))
#                 ner_viewer_thread = threading.Thread(target=show_realtime_ner_results(config))
                
#                 consumer1_thread.start()
#                 producer_thread.start()
#                 ner_viewer_thread.start()

#                 producer_thread.join()
#                 consumer1_thread.join()
#                 ner_viewer_thread.join()

#                 st.info("⏳ Đang xử lý, theo dõi log terminal để xem tiến trình.")


# # def main():
# #     config = Config()
# #     st.title("🚀 Social Listening Pipeline (Streamlit)")

# #     choice = st.radio("Bạn muốn thực hiện:", ("Nhập URL Facebook để crawl", "Nhập một đoạn text để phân tích"))

# #     producer_thread = None
# #     push_thread = None
# #     if choice == "Nhập URL Facebook để crawl":
# #         url = st.text_input("Nhập URL Facebook:")
# #         if st.button("Bắt đầu Crawl + Push Kafka + Consumer song song"):
# #             if url.strip() == "":
# #                 st.warning("⚠️ Vui lòng nhập URL.")
# #             else:
# #                 config.URL = url
# #                 st.success("✅ Đang chạy crawl + push + consumer song song...")

# #                 producer_thread = threading.Thread(target=run_apify_facebook_crawl_push_kafka_topic, args=(config,url))
# #                 # consumer_thread = threading.Thread(target=run_consumer_extract_push_kafka, args=(config,))

# #                 producer_thread.start()
# #                 # consumer_thread.start()

# #                 st.info("⏳ Đang chạy song song, theo dõi log terminal để xem tiến trình.")

# #     elif choice == "Nhập một đoạn text để phân tích":
# #         text = st.text_area("Nhập nội dung:")
# #         if st.button("Push Text và Chạy Consumer song song"):
# #             if text.strip() == "":
# #                 st.warning("⚠️ Vui lòng nhập nội dung.")
# #             else:
# #                 st.success("✅ Đang push text và chạy consumer song song...")

# #                 push_thread = threading.Thread(target=push_text_and_run_consumer, args=(text, config))
# #                 push_thread.start()

# #                 st.info("⏳ Đang xử lý, theo dõi log terminal để xem tiến trình.")

# #     consumer_thread = threading.Thread(target=run_consumer_extract_push_kafka, args=(config,))
# #     consumer_thread.start()

# #     if producer_thread is not None:
# #         producer_thread.join()
# #     if producer_thread is not None:
# #         push_thread.join()
# #     consumer_thread.join()


# if __name__ == "__main__":
#     main()

import streamlit as st
from kafka import KafkaConsumer
import json
import threading
import pandas as pd
from queue import Queue, Empty
from config import Config
from Producer.producer import *
from Consumer.consumer1 import *

# Queue dùng để giao tiếp giữa thread consumer và giao diện
ner_queue = Queue()

# Hàm chạy Viewer realtime đẩy dữ liệu vào queue
def kafka_viewer_realtime(config, stop_event):
    consumer = KafkaConsumer(
        config.KAFKA_TOPIC_COMMENTS,
        bootstrap_servers=config.KAFKA_SERVERS,
        auto_offset_reset='latest',
        group_id='fb_posts_ner_viewer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    try:
        for message in consumer:
            if stop_event.is_set():
                break
            data = message.value
            ner_queue.put(data)
            print(f"📥 Received: {data}")
    except Exception as e:
        print(f"❌ Viewer error: {e}")
    finally:
        consumer.close()

def main():
    config = Config()
    st.title("Social Listening")

    # Stop event để dừng thread an toàn
    if "viewer_stop_event" not in st.session_state:
        st.session_state.viewer_stop_event = threading.Event()
    if "viewer_thread" not in st.session_state:
        st.session_state.viewer_thread = None

    choice = st.radio("Mời chọn:", ("Nhập URL Facebook để crawl", "Nhập một đoạn text để phân tích"))

    if choice == "Nhập URL Facebook để crawl":
        url = st.text_input("Nhập URL Facebook:")
        if st.button("START"):
            if url.strip() == "":
                st.warning("⚠️ Vui lòng nhập URL.")
            else:
                st.success("✅ RUNNING...")

                producer_thread = threading.Thread(
                    target=run_apify_facebook_crawl_push_kafka_topic,
                    args=(config, url),
                    daemon=True
                )
                consumer_thread = threading.Thread(
                    target=run_consumer_extract_push_kafka,
                    args=(config,),
                    daemon=True
                )

                producer_thread.start()
                consumer_thread.start()

                st.info("⏳ Still runing, check terminal !")

    elif choice == "Nhập một đoạn text để phân tích":
        text = st.text_area("Nhập nội dung:")
        if st.button("START"):
            if text.strip() == "":
                st.warning("⚠️ Vui lòng nhập nội dung.")
            else:
                st.success("✅ RUNNING...")

                producer_thread = threading.Thread(
                    target=push_text_and_run_consumer,
                    args=(config, text),
                    daemon=True
                )
                consumer_thread = threading.Thread(
                    target=run_consumer_extract_push_kafka,
                    args=(config,),
                    daemon=True
                )

                producer_thread.start()
                consumer_thread.start()

                st.info("⏳ Still runing, check terminal !")

    # st.markdown("---")
    # st.header("📊NER Viewer")

    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("▶️ Start Viewer"):
    #         if st.session_state.viewer_thread is None or not st.session_state.viewer_thread.is_alive():
    #             st.session_state.viewer_stop_event.clear()
    #             st.session_state.viewer_thread = threading.Thread(
    #                 target=kafka_viewer_realtime,
    #                 args=(config, st.session_state.viewer_stop_event),
    #                 daemon=True
    #             )
    #             st.session_state.viewer_thread.start()
    #             st.success("✅ Viewer NER realtime đã chạy.")
    #         else:
    #             st.info("⚠️ Viewer đã chạy, không cần chạy lại.")

    # with col2:
    #     if st.button("⏹️ Dừng Viewer Realtime"):
    #         if st.session_state.viewer_thread and st.session_state.viewer_thread.is_alive():
    #             st.session_state.viewer_stop_event.set()
    #             st.session_state.viewer_thread.join()
    #             st.success("✅ Viewer đã dừng.")
    #         else:
    #             st.info("⚠️ Viewer chưa chạy.")

    # st.markdown("### 📈 Kết quả NER realtime:")
    # ner_display = st.empty()
    # ner_list = []

    # while st.session_state.viewer_thread and st.session_state.viewer_thread.is_alive():
    #     try:
    #         # Lấy dữ liệu từ queue, nếu có thì append vào list
    #         data = ner_queue.get(timeout=1)
    #         ner_list.append(data)
    #         if len(ner_list) > 100:
    #             ner_list.pop(0)
    #         df = pd.DataFrame(ner_list)
    #         ner_display.dataframe(df, use_container_width=True)
    #     except Empty:
    #         continue
        # Khởi tạo trạng thái viewer
    if "viewer_running" not in st.session_state:
        st.session_state.viewer_running = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Viewer"):
            st.session_state.viewer_running = True
            st.success("✅ Viewer đã bắt đầu.")

    with col2:
        if st.button("⏹️ Stop Viewer"):
            st.session_state.viewer_running = False
            st.success("✅ Viewer đã dừng.")

    st.markdown("---")
    st.header("📊 Kết quả module NER")

    viewer_placeholder = st.empty()

    if st.session_state.viewer_running:

        with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\ner_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Kiểm tra kiểu dữ liệu của data
        if isinstance(data, list):
            # Xử lý khi data là list, có thể có nhiều đối tượng
            places = []
            labels = []
            for item in data:
                for place, label in item["label"].items():
                    places.append(place)
                    labels.append(label)
            df = pd.DataFrame({"Place": places, "Label": labels})

        elif isinstance(data, dict):
            # Xử lý khi data là dictionary (một đối tượng duy nhất)
            places = []
            labels = []
            for place, label in data["label"].items():
                places.append(place)
                labels.append(label)
            df = pd.DataFrame({"Place": places, "Label": labels})

        else:
            st.warning("⚠️ Định dạng file không hợp lệ.")
            df = pd.DataFrame()

        # Hiển thị dữ liệu nếu DataFrame không rỗng
        if not df.empty:
            viewer_placeholder = st.empty()  # Đặt chỗ hiển thị
            viewer_placeholder.dataframe(df.tail(100), use_container_width=True)
        else:
            viewer_placeholder.info("⏳ File không có dữ liệu phù hợp.")

    if "comments_viewer_running" not in st.session_state:
        st.session_state.comments_viewer_running = False

    col3, col4 = st.columns(2)
    with col3:
        if st.button("▶️ Start Comments Viewer"):
            st.session_state.comments_viewer_running = True
            st.success("✅ Comments Viewer đã bắt đầu.")

    with col4:
        if st.button("⏹️ Stop Comments Viewer"):
            st.session_state.comments_viewer_running = False
            st.success("✅ Comments Viewer đã dừng.")

    comments_placeholder = st.empty()

    if st.session_state.comments_viewer_running:
        try:
            with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\crawled_reviews.json", "r", encoding="utf-8") as f:
                comments_data = json.load(f)

            if isinstance(comments_data, list):
                places = []
                domains = []
                texts = []
                predicted = []

                for item in comments_data:
                    places.append(item.get("place_name", ""))
                    domains.append(item.get("domain", ""))
                    texts.append(item.get("review_text", ""))
                    predicted.append(json.dumps(item.get("absa_prediction", []), ensure_ascii=False))

                comments_df = pd.DataFrame({
                    "Place": places,
                    "Domain": domains,
                    "Review Text": texts,
                    "ABSA Prediction": predicted
                })

                comments_placeholder.dataframe(comments_df.tail(50), use_container_width=True)
            else:
                comments_placeholder.warning("⚠️ Định dạng `crawled_reviews.json` không hợp lệ.")

        except FileNotFoundError:
            comments_placeholder.info("⏳ Chưa có file `crawled_reviews.json`.")

    # ================== VIEWER ASPECT STATISTICS ==================
    st.markdown("---")
    st.header("📈 Viewer Aspect Sentiment Statistics")

    if "summary_viewer_running" not in st.session_state:
        st.session_state.summary_viewer_running = False

    col5, col6 = st.columns(2)
    with col5:
        if st.button("▶️ Start Aspect Stats Viewer"):
            st.session_state.summary_viewer_running = True
            st.success("✅ Aspect Stats Viewer đã bắt đầu.")

    with col6:
        if st.button("⏹️ Stop Aspect Stats Viewer"):
            st.session_state.summary_viewer_running = False
            st.success("✅ Aspect Stats Viewer đã dừng.")

    summary_placeholder = st.empty()

    if st.session_state.summary_viewer_running:
        try:
            with open(r"F:\Studies\Third_year\Big_data\Final_Code\run_result\summary_statistics.json", "r", encoding="utf-8") as f:
                summary_data = json.load(f)

            summary_list = []
            for aspect, senti_counts in summary_data.items():
                for sentiment, count in senti_counts.items():
                    summary_list.append({
                        "Aspect": aspect,
                        "Sentiment": sentiment,
                        "Count": count
                    })
            summary_df = pd.DataFrame(summary_list)

            if not summary_df.empty:
                st.subheader("📊 Aspect Sentiment Chart")
                chart_df = summary_df.pivot_table(index="Aspect", columns="Sentiment", values="Count", fill_value=0)
                st.bar_chart(chart_df)

                summary_placeholder.dataframe(
                    summary_df.sort_values(by=["Aspect", "Sentiment"]),
                    use_container_width=True
                )
            else:
                summary_placeholder.info("⏳ Chưa có dữ liệu thống kê.")

        except FileNotFoundError:
            summary_placeholder.info("⏳ Chưa có file `summary_statistics.json`.")

if __name__ == "__main__":
    main()
