import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class DB_firebase:

    def __init__(self,
                creds_path = r'staticfiles\firebase_creds.json',
                collection = 'users'):

        cred = credentials.Certificate(creds_path)
        try:
            firebase_admin.initialize_app(cred)
        except:
            #Firebase Already Initialized
            pass
        self.db = firestore.client()
        self.collection = collection

    
    def set_user_data(self, user, dict_data):
        self.db.collection(self.collection).document(user).set(dict_data)

    
    def update_user_data(self, user, dict_data):
        self.db.collection(self.collection).document(user).update(dict_data)


    def update_user_data_field(self, user, field, value):
        self.db.collection(self.collection).document(user).update({field : value})    


    def delete_collection_data(self, collection, item):
        self.db.collection(collection).document(item).delete()


    def delete_user_data(self, user):
        self.db.collection(self.collection).document(user).delete()

    
    def __get_all_data(self, collection = None):
        docs = self.db.collection(collection or self.collection).stream()
        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')


    def get_user_data(self, user):
        doc = self.db.collection(self.collection).document(user).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return False

    def get_user_data_field(self, user, field):
        doc = self.db.collection(self.collection).document(user).get()
        return doc.to_dict()[field]
    
    def if_doc_exists(self, user):
        return self.db.collection(self.collection).document(user).get().exists





