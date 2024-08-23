import argparse
import os
import json

from utils_hj3415 import utils

FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
mongo_addr_title = 'mongo_addr'
redis_addr_title = 'redis_addr'
# 테스트 서버 주소
def_mongo_addr = "mongodb+srv://Cluster13994:Rnt3Q1hrZnFT@cluster13994.vhtfyhr.mongodb.net"
def_redis_addr = "localhost"


def print_settings():
    mongo_addr = load_mongo_addr()
    redis_addr = load_redis_addr()
    print(f'Saved mongo address: {mongo_addr}')
    print(f'Saved redis address : {redis_addr}')


def save_mongo_addr(address: str):
    """주소를 파일에 저장합니다."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            settings = json.load(file)
    else:
        settings = {
        }

    settings[mongo_addr_title] = address

    with open(FILE_PATH, 'w') as file:
        json.dump(settings, file, indent=4)

    print(f"mongodb 주소가 저장 되었습니다: {address}")


def save_redis_addr(address: str):
    """주소를 파일에 저장합니다."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            settings = json.load(file)
    else:
        settings = {
        }

    settings[redis_addr_title] = address

    with open(FILE_PATH, 'w') as file:
        json.dump(settings, file, indent=4)

    print(f"redisdb 주소가 저장 되었습니다: {address}")


def load_mongo_addr() -> str:
    """파일에서 mongodb 주소를 불러옵니다."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            settings = json.load(file)
            return settings.get(mongo_addr_title, def_mongo_addr)
    else:
        # 기본값
        return def_mongo_addr


def load_redis_addr() -> str:
    """파일에서 redisdb 주소를 불러옵니다."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            settings = json.load(file)
            return settings.get(redis_addr_title, def_redis_addr)
    else:
        # 기본값
        return def_redis_addr


def db():
    from db_hj3415 import mymongo
    pages = mymongo.Corps.COLLECTIONS

    # 데이터베이스의 종류를 지정하는 subparsers 추가
    parser = argparse.ArgumentParser(description="데이터베이스 주소를 저장하고 불러오는 프로그램")
    subparsers = parser.add_subparsers(dest='database', help='데이터베이스 종류를 지정하세요(mongo, redis)')

    # database subparsers에 mongo subparsers 추가
    parser_mongo = subparsers.add_parser('mongo', help='mongo db를 관리합니다.')
    mongo_subparsers = parser_mongo.add_subparsers(dest='command', help='명령을 선택하세요.')

    # mongo subparsers에 save 명령어 추가
    mongo_save_parser = mongo_subparsers.add_parser('save', help='데이터베이스 주소를 저장합니다.')
    mongo_save_parser.add_argument('address', type=str, help='저장할 주소를 입력하세요.')

    # mongo subparsers에 print 명령어 추가
    mongo_print_parser = mongo_subparsers.add_parser('print', help='저장된 데이터베이스 주소를 불러옵니다.')

    # mongo subparsers에 drop 명령어 추가
    mongo_drop_parser = mongo_subparsers.add_parser('drop', help="데이터베이스나 페이지를 삭제합니다.")
    mongo_drop_parser.add_argument('page', help=f"Pages - {pages}")
    mongo_drop_parser.add_argument('targets', nargs='+', type=str, help="원하는 종류의 코드를 나열하세요.")

    # database subparsers에 redis subparsers 추가
    parser_redis = subparsers.add_parser('redis', help='redis db를 관리합니다.')
    redis_subparsers = parser_redis.add_subparsers(dest='command', help='명령을 선택하세요.')

    # redis subparsers에 save 명령어 추가
    redis_save_parser = redis_subparsers.add_parser('save', help='데이터베이스 주소를 저장합니다.')
    redis_save_parser.add_argument('address', type=str, help='저장할 주소를 입력하세요.')

    # redis subparsers에 print 명령어 추가
    redis_print_parser = redis_subparsers.add_parser('print', help='저장된 데이터베이스 주소를 불러옵니다.')

    # 인자 파싱
    args = parser.parse_args()

    # 명령에 따른 동작 수행
    if args.database == 'mongo':
        if args.command == 'save':
            save_mongo_addr(args.address)
        elif args.command == 'print':
            address = load_mongo_addr()
            if address:
                print(f"mongodb 데이터베이스 주소: {address}")
        elif args.command == 'drop':
            if args.page in pages:
                if len(args.targets) == 1 and args.targets[0] == 'all':
                    mymongo.Corps.drop_page_in_all_codes(args.page)
                else:
                    # args.targets의 코드 유효성을 검사한다.
                    is_valid = True
                    for code in args.targets:
                        # 하나라도 코드 형식에 이상 있으면 에러
                        is_valid = utils.is_6digit(code)
                    if is_valid:
                        for code in args.targets:
                            mymongo.Corps(code, args.page).drop_table()
                    else:
                        print(f"{args.targets} 종목 코드의 형식은 6자리 숫자입니다.")
            else:
                print(f"The page should be in {pages}")

    elif args.database == 'redis':
        if args.command == 'save':
            save_redis_addr(args.address)
        elif args.command == 'print':
            address = load_redis_addr()
            if address:
                print(f"redisdb 데이터베이스 주소: {address}")

    mymongo.Base.mongo_client.close()








"""def dbmanager():
    cmd = ['repair', 'sync', 'eval', 'update']
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', help=f"Command - {cmd}")
    parser.add_argument('target', help="Target for scraping (type 6digit code or 'all' or 'parts')")
    parser.add_argument('-d', '--db_path', help="Set mongo database path")

    args = parser.parse_args()

    db_path = args.db_path if args.db_path else "mongodb://192.168.0.173:27017"
    client = mongo.connect_mongo(db_path)

    if args.cmd in cmd:
        if args.cmd == 'repair':
            if args.target == 'all' or utils.is_6digit(args.target):
                need_for_repair_codes = chk_db.chk_integrity_corps(client, args.target)
                # repair dict 예시 - {'343510': ['c106', 'c104', 'c103'], '298000': ['c104'], '091810': ['c104']}
                print(f"Need for repairing codes :{need_for_repair_codes}")
                if need_for_repair_codes:
                    # x = input("Do you want to try to repair db by scraping? (y/N)")
                    # if x == 'y' or x == 'Y':
                        for code, failed_page_list in need_for_repair_codes.items():
                            for page in failed_page_list:
                                if page == 'c101':
                                    nfsrun.c101([code, ], db_path)
                                elif page == 'c103':
                                    nfsrun.c103([code, ], db_path)
                                elif page == 'c104':
                                    nfsrun.c104([code, ], db_path)
                                elif page == 'c106':
                                    nfsrun.c106([code, ], db_path)
                            recheck_result = chk_db.chk_integrity_corps(client, code)
                            if recheck_result:
                                # 다시 스크랩해도 오류가 지속되는 경우
                                print(f"The db integrity failure persists..{recheck_result}")
                                # x = input(f"Do you want to delete {code} on DB? (y/N)")
                                # if x == 'y' or x == 'Y':
                                #    mongo.Corps.del_db(client, code)
                                # else:
                                #    print("Canceled.")
                                mongo.Corps.del_db(client, code)
                    # else:
                    #     print("Done.")
                else:
                    print("Done.")
            else:
                print(f"Invalid target option : {args.target}")
        elif args.cmd == 'update':
            if args.target == 'all' or utils.is_6digit(args.target):
                need_for_update_codes = list(chk_db.chk_modifying_corps(client, args.target).keys())
                # need_for_update_codes 예시 - [codes....]
                print(f"Need for updating codes :{need_for_update_codes}")
                if need_for_update_codes:
                    nfsrun.c103(need_for_update_codes, db_path)
                    nfsrun.c104(need_for_update_codes, db_path)
                    nfsrun.c106(need_for_update_codes, db_path)
            elif args.target == 'parts':
                pass
            else:
                print(f"Invalid target option : {args.target}")
        elif args.cmd == 'sync':
            if args.target == 'all':
                chk_db.sync_mongo_with_krx(client)
            else:
                print(f"The target should be 'all' in sync command.")
        elif args.cmd == 'eval':
            if args.target == 'all':
                # eval을 평가해서 데이터베이스에 저장한다.
                eval.make_today_eval_df(client, refresh=True)
            else:
                print(f"The target should be 'all' in sync command.")
    else:
        print(f"The command should be in {cmd}")

    client.close()"""
