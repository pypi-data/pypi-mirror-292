import time
import sys
from _datetime import datetime
from typing import Dict, List, Tuple, Callable
from multiprocessing import Process, Queue
from . import mymongo
from utils_hj3415 import utils, noti
from scraper2_hj3415.krx import krx
from scraper2_hj3415.nfscrapy import run as nfsrun
from pymongo import MongoClient
from selenium.webdriver.chrome.webdriver import WebDriver

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


"""
chk_integrity_corps 함수로 종목코드를 데이터베이스명으로 가지는 DB의 유효성을 검사한다. 
"""



def extract_addr_from_client(client: MongoClient) -> str:
    """
    scaraper는 클라이언트를 인자로 받지않고 주소를 받아서 사용하기 때문에 사용하는 주소 추출함수
    """
    # client에서 mongodb주소 추출
    ip = str(list(client.nodes)[0][0])
    port = str(list(client.nodes)[0][1])
    return 'mongodb://' + ip + ':' + port


def test_corp_one(client1: MongoClient, code: str, driver: WebDriver = None, waiting_time: int = 10) -> Dict[str, list]:
    """
    종목 하나의 컬렉션의 유효성을 검사하여 부족한 컬렉션을 딕셔너리로 만들어서 반환한다.
    driver와 waiting_time은 본 함수에서 사용하지는 않으나 다른 함수와 인자를 맞추기위해 인자로 받아준다.
    리턴값 - {'005930': ['c104','c103'...]}
    """

    def is_same_count_of_docs(col_name1: str, col_name2: str) -> bool:
        logger.debug(f"In is_same_count_of_docs {code}/ {col_name1}, {col_name2}")
        corp_one.page = col_name1
        count_doc1 = corp_one.count_docs_in_col()
        corp_one.page = col_name2
        count_doc2 = corp_one.count_docs_in_col()
        if count_doc1 == count_doc2:
            return True
        else:
            return False

    proper_collections = {'c101', 'c104y', 'c104q', 'c106y', 'c106q', 'c103손익계산서q', 'c103재무상태표q',
                          'c103현금흐름표q', 'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y'}

    logger.debug('In test_corp_one function...')
    return_dict = {}

    logger.debug(f'return_dict is ... {return_dict}')
    # 한 종목의 유효성 검사코드
    corp_one = mongo.Corps(client1, code, 'c101')

    # 차집합을 사용해서 db내에 없는 컬렉션이 있는지 확인한다.
    set_deficient_collentions = set.difference(proper_collections, set(corp_one.list_collection_names()))

    logger.debug(f'After take a set of difference : {set_deficient_collentions}')

    return_dict[code] = set()
    # 컬렉션이 아예 없는 것이 있다면 falied_codes에 추가한다.
    if set_deficient_collentions != set():
        for item in set_deficient_collentions:
            # 컬렉션 이름 중 앞의 네글자만 추려서 추가해준다.(ex - c103손익계산서q -> c103)
            return_dict[code].add(item[:4])

    # 각 컬렉션의 q와 y의 도큐먼트 갯수를 비교하여 차이가 있는지 확인한다.
    if not is_same_count_of_docs('c104y', 'c104q'):
        return_dict[code].add('c104')
    if not is_same_count_of_docs('c106y', 'c106q'):
        return_dict[code].add('c106')
    if not is_same_count_of_docs('c103손익계산서q', 'c103손익계산서y') \
            or not is_same_count_of_docs('c103재무상태표q', 'c103재무상태표y') \
            or not is_same_count_of_docs('c103현금흐름표y', 'c103현금흐름표q'):
        return_dict[code].add('c103')

    # 집합을 리스트로 바꿔서 다시 저장한다.
    return_dict[code] = list(return_dict[code])
    logger.debug(f'Going out test_corp_one : {return_dict}')
    return return_dict


def test_corp_one_is_modified(client: MongoClient, code: str, driver: WebDriver, waiting_time: int) -> Dict[str, bool]:
    """
    웹에서 스크랩한 c103손익계산서y와 데이터베이스에 있는 c103손익계산서y를 비교하여 다른지 확인하여 업데이트 유무를 반환한다.
    리턴값 - (코드, bool-업데이트가필요한지)
    """
    df_online = nfsrun.scrape_c103_first_page(driver, code, waiting_time=waiting_time)
    df_mongo = mongo.C103(client, code=code, page='c103손익계산서y').load_df()

    logger.debug(df_online)
    logger.debug(df_mongo)

    return_dict = {code: not df_online.equals(df_mongo)}
    return return_dict


def working_with_parts(test_func: Callable[[MongoClient, str, WebDriver, int], dict], db_addr: str, divided_code_list: list, my_q: Queue, waiting_time: int):
    # 각 코어별로 디비 클라이언트를 만들어야만 한다. 안그러면 에러발생
    client = mongo.connect_to_mongo(db_addr)
    driver = utils.get_driver()
    t = len(divided_code_list)

    failed_dict_part = {}

    for i, code in enumerate(divided_code_list):
        try:
            failed_one_dict = test_func(client, code, driver, waiting_time)
        except Exception as e:
            print(f"{code} has a error : {e}", file=sys.stderr)
            continue
        print(f'{i + 1}/{t} {failed_one_dict}')
        if failed_one_dict[code]:
            # 빈리스트가 아니라면...또는 C103이 변화되었다면.. 큐에 추가한다.
            failed_dict_part.update(failed_one_dict)
    else:
        # 큐에서 put은 함수 리턴처럼 함수에서 한번만 한다.
        my_q.put(failed_dict_part)
        driver.close()


# 멀티프로세싱을 사용하기 위해서 독립된 함수로 제작하였음(피클링이 가능해야함)
def chk_integrity_corps(client: MongoClient, code: str = 'all') -> Dict[str, list]:
    """
    몽고 디비의 corps들의 integrity 검사후 이상이 있는 코드 리스트 반환
    이상을 찾는 방법 - 각 컬렉션이 다 있는가. 각 컬렉션에서 연도와 분기의 도큐먼트 갯수가 같은가
    return - {'코드': ['cxxx',...], '코드': ['cxxx',...]...}
    """
    failed_codes = {}
    codes_in_db = mongo.Corps.get_all_codes(client)
    if code == 'all':
        print('*' * 25, f"Check all Corp db integrity using multiprocess", '*' * 25)
        print(f'Total {len(codes_in_db)} items..')
        n, divided_list = utils.code_divider_by_cpu_core(codes_in_db)

        addr = mongo.extract_addr_from_client(client)

        start_time = time.time()
        q = Queue()
        ths = []
        for i in range(n):
            ths.append(Process(target=working_with_parts, args=(test_corp_one, addr, divided_list[i], q, 0)))
        for i in range(n):
            ths[i].start()

        for i in range(n):
            failed_codes.update(q.get())

        for i in range(n):
            ths[i].join()

        logger.debug(f"failed_codes : {failed_codes}")
        print(f'Total spent time : {round(time.time() - start_time, 2)} sec.')
    else:
        print('*' * 25, f"Check {code} db integrity", '*' * 25)
        if code in codes_in_db:
            result_dict = test_corp_one(client, code)
            print(f'{code} : {result_dict[code]}')
            if result_dict[code]:   # 빈리스트가 아니라면...
                failed_codes.update(result_dict)

        else:
            Exception(f'{code} is not in db..')
    return failed_codes


def chk_modifying_corps(client, code: str = 'all', waiting_time: int = 60) -> Dict[str, bool]:
    """
    각 종목의 웹과 DB의 C103손익계산서y를 비교하여 변화가 있어 refresh가 필요한지를 반환한다.
    """
    failed_codes = {}
    codes_in_db = mongo.Corps.get_all_codes(client)
    if code == 'all':
        print('*' * 25, f"Check all Corp db need for updating using multiprocess", '*' * 25)
        print(f'Total {len(codes_in_db)} items..')
        n, divided_list = utils.code_divider_by_cpu_core(codes_in_db)

        addr = mongo.extract_addr_from_client(client)

        start_time = time.time()
        q = Queue()
        ths = []
        for i in range(n):
            ths.append(Process(target=working_with_parts, args=(test_corp_one_is_modified, addr, divided_list[i], q, waiting_time)))
        for i in range(n):
            ths[i].start()

        for i in range(n):
            failed_codes.update(q.get())

        for i in range(n):
            ths[i].join()

        logger.debug(f"failed_codes : {failed_codes}")
        print(f'Total spent time : {round(time.time() - start_time, 2)} sec.')
    else:
        print('*' * 25, f"Check {code} db need for updating ", '*' * 25)
        driver = utils.get_driver()
        if code in codes_in_db:
            result_dict = test_corp_one_is_modified(client, code, driver)
            print(f'{code} : {result_dict[code]}')
            if result_dict[code]:
                failed_codes.update(result_dict)

        else:
            Exception(f'{code} is not in db..')
    return failed_codes


def sync_mongo_with_krx(client):
    print('*' * 20, 'Sync with krx and mongodb', '*' * 20)
    all_codes_in_db = mongo.Corps.get_all_codes(client)
    print('*' * 20, 'Refreshing krx.db...', '*' * 20)
    krx.make_db()
    print('*' * 80)
    all_codes_in_krx = krx.get_codes()
    print('\tThe number of codes in krx: ', len(all_codes_in_krx))
    logger.debug(all_codes_in_krx)
    try:
        print('\tThe number of dbs in mongo: ', len(all_codes_in_db))
        logger.debug(all_codes_in_db)
    except TypeError:
        err_msg = "Error while sync mongo data...it's possible mongo db doesn't set yet.."
        logger.error(err_msg)
        noti.telegram_to(botname='manager', text=err_msg)
        return
    del_targets = list(set(all_codes_in_db) - set(all_codes_in_krx))
    add_targets = list(set(all_codes_in_krx) - set(all_codes_in_db))
    print('\tDelete target: ', del_targets)
    print('\tAdd target: ', add_targets)

    for target in del_targets:
        mongo.Corps.del_db(client, target)

    if add_targets:
        print(f'Starting.. c10346 scraper.. items : {len(add_targets)}')
        addr = mongo.extract_addr_from_client(client)
        nfsrun.c103(add_targets, addr)
        nfsrun.c104(add_targets, addr)
        nfsrun.c108(add_targets, addr)
