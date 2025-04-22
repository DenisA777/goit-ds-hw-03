from pymongo import MongoClient, errors


MONGO_URI = "mongodb+srv://mongo_power:fodsom-3dyjny-dezqaF@cluster0.yzdglvd.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

DB_NAME = "cats_db" 
COLLECTION_NAME = "cats"



try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  
    db = client[DB_NAME]
    cats_collection = db[COLLECTION_NAME]
    print("Успішне підключення до MongoDB Atlas")
except errors.ServerSelectionTimeoutError as e:
    print("Не вдалося підключитися до MongoDB:", e)
    exit(1)


try:
    cats_collection.insert_one({
        "name": "barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"]
    })
    print("Додано тестового кота 'barsik'")
except Exception as e:
    print("Помилка при додаванні кота:", e)


def get_all_cats():
    try:
        cats = cats_collection.find()
        for cat in cats:
            print(cat)
    except Exception as e:
        print("Помилка при читанні котів:", e)



def get_cat_by_name(name):
    try:
        cat = cats_collection.find_one({"name": name})
        if cat:
            print(cat)
        else:
            print("Кота з таким ім'ям не знайдено.")
    except Exception as e:
        print("Помилка при пошуку кота:", e)


def update_cat_age(name, new_age):
    try:
        result = cats_collection.update_one(
            {"name": name},
            {"$set": {"age": new_age}}
        )
        if result.modified_count:
            print("Вік оновлено.")
        else:
            print("Кота з таким ім'ям не знайдено або вік уже актуальний.")
    except Exception as e:
        print("Помилка при оновленні віку:", e)



def add_cat_feature(name, feature):
    try:
        result = cats_collection.update_one(
            {"name": name},
            {"$addToSet": {"features": feature}}  
        )
        if result.modified_count:
            print("Характеристику додано.")
        else:
            print("Кота не знайдено або така характеристика уже існує.")
    except Exception as e:
        print("Помилка при додаванні характеристики:", e)



def delete_cat_by_name(name):
    try:
        result = cats_collection.delete_one({"name": name})
        if result.deleted_count:
            print("Кота видалено.")
        else:
            print("Кота з таким ім'ям не знайдено.")
    except Exception as e:
        print("Помилка при видаленні кота:", e)



def delete_all_cats():
    try:
        result = cats_collection.delete_many({})
        print(f"Видалено {result.deleted_count} записів.")
    except Exception as e:
        print("Помилка при видаленні усіх котів:", e)



if __name__ == "__main__":
    print("--- Усі коти ---")
    get_all_cats()

    print("\n--- Пошук 'barsik' ---")
    get_cat_by_name("barsik")

    print("\n--- Оновлення віку barsik ---")
    update_cat_age("barsik", 4)

    print("\n--- Додавання характеристики ---")
    add_cat_feature("barsik", "любить рибу")

    print("\n--- Видалення barsik ---")
    delete_cat_by_name("barsik")

    print("\n--- Видалення усіх ---")
    delete_all_cats()
