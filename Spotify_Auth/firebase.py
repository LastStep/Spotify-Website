from firebase_admin import initialize_app, credentials, firestore, db
from django.contrib.staticfiles import finders


class DB_firebase:

    def __init__(self,
                creds_path = finders.find('firebase_creds.json'),
                collection = 'users'):

        cred = credentials.Certificate(creds_path)
        try:
            initialize_app(cred)
        except:
            #Firebase Already Initialized
            pass
        self.db = firestore.client()
        self.collection = collection
        self.ref = self.db.collection(self.collection)

    
    def if_doc_exists(self, user):
        return self.ref.document(user).get().exists


    def update_user_data(self, user, 
            dict_data=False, collection=False, doc=False, field=False, value=False):

        if collection and doc:
            ref = self.ref.document(user).collection(collection).document(doc)
        else:
            ref = self.ref.document(user)
        
        if dict_data:
            ref.set(dict_data , merge=True)
        elif field and value:
            ref.update({field : value})
        else:
            assert 'No dict_data or field value provided'


    def get_user_data(self, user, 
            collection=False, doc=False, field=None):

        if collection and doc:
            doc = self.ref.document(user).collection(collection).document(doc).get()
        else:
            doc = self.ref.document(user).get()

        if doc.exists:
            if field:
                return doc.to_dict()[field]
            return doc.to_dict()
        else:
            return False


    def delete_user_data(self, user):
        self.ref.document(user).delete()






