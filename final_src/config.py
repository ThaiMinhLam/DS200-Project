class Config:
    KAFKA_SERVERS               = ['localhost:9092']
    DATA_PATH                   = r'F:\Studies\Third_year\Big_data\Final_Code\Data\ABSA_Dataset\ABSA_test.csv'
    KAFKA_TOPIC_COMMENTS        = 'comments'
    KAFKA_TOPIC_ABSA_RESULT     = 'absa_result'
    MODEL_NER_PATH              = r'F:\Studies\Third_year\Big_data\Final_Code\Model\PhoBERT_ner_finetuned_v2'
    ATTRACTIONS_ABSA_MODEL      = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_attractions.pkl'
    DRINKPLACES_ABSA_MODEL      = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_drinkplaces.pkl'
    CAMPINGS_ABSA_MODEL         = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_campings.pkl'
    EATERIES_ABSA_MODEL         = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_eateries.pkl'
    HOTELS_ABSA_MODEL           = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_hotels.pkl'
    RENTS_ABSA_MODEL            = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_rents.pkl'
    RESTAURANTS_ABSA_MODEL      = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_restaurants.pkl'
    TOURS_ABSA_MODEL            = r'F:\Studies\Third_year\Big_data\Final_Code\Model\ABSA_models\tfidf_linear_svc_tours.pkl'
