from DataBase.firebase import DB_firebase as db

DB = db()

def get_token(user):
    return DB.get_user_data(user)['access_token']