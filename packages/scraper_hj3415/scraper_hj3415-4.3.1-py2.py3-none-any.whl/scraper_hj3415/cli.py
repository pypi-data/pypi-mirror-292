import sys

from scraper_hj3415.krx import krx300
from utils_hj3415 import utils, noti
import argparse


def nfs():
    from scraper_hj3415.nfscraper import run
    spiders = {
        'c101': run.c101,
        'c106': run.c106,
        'c103y': run.c103y,
        'c103q': run.c103q,
        'c104y': run.c104y,
        'c104q': run.c104q,
        'c108': run.c108,
        'all_spider': run.all_spider
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('spider', help=f"Spiders - {spiders.keys()}")
    parser.add_argument('targets', nargs='+', type=str, help="원하는 종류의 코드를 나열하세요.")
    parser.add_argument('--noti', action='store_true', help='작업완료후 메시지 전송여부')

    args = parser.parse_args()

    if args.spider in spiders.keys():
        if len(args.targets) == 1 and args.targets[0] == 'all':
            #x = input("It will take a long time. Are you sure? (y/N)")
            #if x == 'y' or x == 'Y':
            # krx300 에서 전체코드리스트를 가져와서 섞어준다.
            import random
            all_codes = krx300.get()
            random.shuffle(all_codes)
            spiders[args.spider](*all_codes)
            if args.noti:
                noti.telegram_to('manager', f"{len(all_codes)}개 종목의 {args.spider}를 저장했습니다.")
        else:
            # args.targets의 코드 유효성을 검사한다.
            is_valid = True
            for code in args.targets:
                # 하나라도 코드 형식에 이상 있으면 에러
                is_valid = utils.is_6digit(code)
            if is_valid:
                spiders[args.spider](*args.targets)
                if args.noti:
                    noti.telegram_to('manager', f"{len(args.targets)}개 종목의 {args.spider}를 저장했습니다.")
            else:
                print(f"{args.targets} 종목 코드의 형식은 6자리 숫자입니다.")
    else:
        print(f"The spider should be in {list(spiders.keys())}")


def mis():
    from scraper_hj3415.miscraper import run
    commands = {
        'mi': run.mi,
        'mihistory': run.mihistory,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help=f"Commands - {commands.keys()}")
    parser.add_argument('--noti', action='store_true', help='작업완료후 메시지 전송여부')

    args = parser.parse_args()

    if args.command in commands.keys():
        if args.command == 'mi':
            commands['mi']()
            if args.noti:
                noti.telegram_to('manager', "오늘의 Market Index를 저장했습니다.")
        elif args.command == 'mihistory':
            years = 3
            commands['mihistory'](years)
            if args.noti:
                noti.telegram_to('manager', f"과거 {years}년치 Market Index를 저장했습니다.")
    else:
        print(f"The command should be in {list(commands.keys())}")
