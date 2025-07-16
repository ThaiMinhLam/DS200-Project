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

 