import time



def test():
    import redis
    # Redis에 연결 (기본 설정: localhost, port 6379)
    r = redis.Redis(host='localhost', port=6379, db=0)

    # 1. 문자열 설정 및 가져오기
    r.set('name', 'John Doe')
    name = r.get('name').decode('utf-8')
    print(f"Name: {name}")  # 출력: Name: John Doe

    # 2. 숫자 증가 및 감소
    r.set('counter', 1)
    r.incr('counter')  # 1 증가
    r.incr('counter')  # 또 다시 1 증가
    r.decr('counter')  # 1 감소
    counter = r.get('counter').decode('utf-8')
    print(f"Counter: {counter}")  # 출력: Counter: 2

    # 3. 리스트 작업
    r.rpush('mylist', 'item1')
    r.rpush('mylist', 'item2')
    r.rpush('mylist', 'item3')
    items = r.lrange('mylist', 0, -1)  # 리스트의 모든 아이템 가져오기
    items = [item.decode('utf-8') for item in items]
    print(f"My list items: {items}")  # 출력: My list items: ['item1', 'item2', 'item3']

    # 4. 해시맵 작업
    r.hset('myhash', 'field1', 'value1')
    r.hset('myhash', 'field2', 'value2')
    fields = r.hgetall('myhash')
    fields = {k.decode('utf-8'): v.decode('utf-8') for k, v in fields.items()}
    print(f"My hash fields: {fields}")  # 출력: My hash fields: {'field1': 'value1', 'field2': 'value2'}

    # 5. 키 삭제
    r.delete('name')
    name_deleted = r.get('name')
    print(f"Name after deletion: {name_deleted}")  # 출력: Name after deletion: None

    # 6. 키 만료 설정
    r.set('temp_key', 'some_value')
    r.expire('temp_key', 10)  # 10초 후에 키가 만료됨
    #time.sleep(2)
    print(f"Temp key before expiration: {r.get('temp_key').decode('utf-8')}")  # 출력: Temp key before expiration: some_value

    r.close()



    """
    레디스에 데이터 없으면 몽고에서 가져오고 있으면 레디스 사용
    """

    from pymongo import MongoClient
    import redis
    import json

    # MongoDB에 연결
    mongo_client = MongoClient('localhost', 27017)
    mongo_db = mongo_client['test_db']
    mongo_collection = mongo_db['test_collection']

    # Redis에 연결
    redis_client = redis.Redis(host='localhost', port=6379, db=0)


    def get_data_from_mongo(document_id):
        """MongoDB에서 데이터를 가져오는 함수."""
        data = mongo_collection.find_one({"_id": document_id})
        if data:
            return data
        return None


    def get_data(document_id):
        """Redis에서 데이터를 캐시하고, 없을 경우 MongoDB에서 가져오는 함수."""
        # Redis에서 데이터 가져오기
        cached_data = redis_client.get(document_id)

        if cached_data:
            print("Redis 캐시에서 데이터 가져오기")
            return json.loads(cached_data)

        # Redis 캐시에 데이터가 없으면 MongoDB에서 가져오기
        print("MongoDB에서 데이터 가져오기")
        data = get_data_from_mongo(document_id)

        if data:
            # 데이터를 Redis에 캐싱
            redis_client.set(document_id, json.dumps(data))

        return data


    # 테스트용 데이터 삽입
    document_id = 1
    mongo_collection.insert_one({"_id": document_id, "name": "John Doe", "age": 30})

    # 데이터 가져오기
    result = get_data(document_id)
    print("결과:", result)

    # 동일한 데이터 가져오기 (이번에는 Redis 캐시에서 가져옴)
    result = get_data(document_id)
    print("결과:", result)



    """
    MongoDB 데이터를 업데이트하고, Redis 캐시를 갱신하거나 삭제
    """


    import redis
    from pymongo import MongoClient

    # Redis 및 MongoDB 클라이언트 설정
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    mongo_client = MongoClient('localhost', 27017)
    mongo_db = mongo_client['test_db']
    mongo_collection = mongo_db['test_collection']


    def update_data(document_id, update_data):
        """MongoDB 데이터를 업데이트하고, Redis 캐시를 갱신하거나 삭제"""
        # MongoDB에서 데이터 업데이트
        mongo_collection.update_one({"_id": document_id}, {"$set": update_data})

        # Redis 캐시 무효화 (삭제)
        redis_client.delete(document_id)
        print(f"Redis 캐시 삭제: {document_id}")

        # 또는 Redis 캐시를 갱신
        updated_data = mongo_collection.find_one({"_id": document_id})
        redis_client.set(document_id, json.dumps(updated_data))
        print(f"Redis 캐시 갱신: {document_id}")


    # MongoDB 데이터 업데이트 및 캐시 갱신 테스트
    update_data(1, {"name": "Jane Doe", "age": 25})

    """
    json을 이용해 딕셔너리 통채로 저장
    """


    import redis
    import json

    # Redis에 연결
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Python 딕셔너리 데이터
    my_dict = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }

    # 딕셔너리를 JSON 문자열로 변환하여 Redis에 저장
    r.set("user:1000", json.dumps(my_dict))

    # Redis에서 JSON 문자열을 가져와 다시 딕셔너리로 변환
    retrieved_json = r.get("user:1000").decode('utf-8')
    retrieved_dict = json.loads(retrieved_json)

    # 결과 출력
    print(retrieved_dict)

    """
    특정패턴에 맞는 키 전부 삭제
    """

    import redis

    # Redis 클라이언트 연결
    client = redis.Redis(host='localhost', port=6379, db=0)

    # 삭제할 키의 패턴
    pattern = "pattern*"

    # SCAN 명령어를 사용하여 패턴에 맞는 키를 찾고 삭제
    cursor = '0'
    while cursor != 0:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=1000)
        if keys:
            client.delete(*keys)

    print("삭제 완료")
