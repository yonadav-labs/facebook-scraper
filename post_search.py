#!/usr/bin/env python3.6
# Download selenium webdriver:
# https://chromedriver.storage.googleapis.com/index.html?path=2.41/

import time
import json
import re
import argparse
import datetime as dt
import database
import requests
import pdb

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dateutil.relativedelta import relativedelta

LOGIN_URL = 'https://www.facebook.com/'
THRESHOLD = 1000
N = 5

SCRAPE_POST = 1
SCRAPE_VIDEO = 1
PUT_DATABASE = 1

def wait_for_elem(driver, query, timeout=300):
    event = EC.element_to_be_clickable((By.CSS_SELECTOR, query))
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(event)
    return elem


def login(driver, username, password):
    driver.get(LOGIN_URL)

    elem = wait_for_elem(driver, '#email')
    elem.send_keys(username)

    elem = wait_for_elem(driver, '#pass')
    elem.send_keys(password)
    elem.submit()


def prepare_driver(*args, **kwargs):
    prof = webdriver.FirefoxProfile()
    prof.set_preference('dom.webnotifications.enabled', False)

    opts = webdriver.FirefoxOptions()
    opts.set_headless(headless=True)

    driver = webdriver.Firefox( 
            firefox_profile=prof,
            firefox_options=opts,
            executable_path='./geckodriver')

    return driver


def parse_counter(count):
    table = { 'k': 1000, 'm': 1000000, 'b': 1000000000 }
    count = count.lower()
    unit  = count[-1]

    try:
        num = re.sub(r'[^\d\.]', r'', count)
        val = float(num)
        return int(val * table.get(unit, 1))

    except ValueError:
        return 0

# Extract post data...
def post_data(post):
    data = {}
    data['title'] = post.select_one('._vwp').text if post.select_one('._vwp') else ''
    data['content'] = post.select_one('._5-jo').text if post.select_one('._5-jo') else ''

    reactions = post.select('._3emk')
    data['reactions'] = 0
    for reaction in reactions:
        data['reactions'] += parse_counter(reaction.text.casefold())

    anchor = post.select_one('.fsm a')
    if anchor: 
        href = anchor.get('href')
        data['url'] = urljoin('https://www.facebook.com', href)

        match = re.search(r'/[^/]+/[^/]+/([0-9]+)', href)
        print (href)
        if match:
            data['id'] = match.group(1) 
        else:
            match = re.search(r'story_fbid=([0-9]+)&', href)
            if match:
                data['id'] = match.group(1)

    abbr = post.select_one('.fsm a abbr')
    if abbr: 
        data['date'] = dt.datetime.utcfromtimestamp(int(abbr.get('data-utime'))).strftime('%Y-%m-%d %H:%M:%S')

    anchors = post.select('._ipo a')
    for anchor in anchors:
        if 'comment' in anchor.text.casefold(): 
            data['comment'] = parse_counter(anchor.text.split()[0].casefold())
        elif 'share' in anchor.text.casefold(): 
            data['share'] = parse_counter(anchor.text.split()[0].casefold())

    views = post.select_one('._ipo span')
    if views: data['views'] = parse_counter(views.text.split()[0].casefold())

    media = post.select_one('._5-0i img')
    data['media'] = media.get('src') if media else ''
    data['type'] = "post"

    # get poster info
    poster = post.select_one('a._vwp')
    if poster:
        data['poster_link'] = poster.get('href')
        data['poster_name'] = poster.text
        data['poster_image'] = post.select_one('img._s0._4ooo._tzw.img').get('src')

    return data


def video_data(post):
    data = {}
    data['title'] = post.select_one('._4ovi').text if post.select_one('._4ovi') else ''
    data['content'] = post.select_one('._4ovj').text if post.select_one('._4ovj') else ''

    anchor = post.select_one('._4ovv a')
    if anchor: 
        href = anchor.get('href')
        match = re.search(r'[^?]*',href)
        if match: 
            url = match.group(0)
            data['url'] = urljoin('https://www.facebook.com', url)
        else: 
            data['url'] = urljoin('https://www.facebook.com', href)

        match = re.search(r'/[^/]+/[^/]+/([0-9]+)', href)
        if match: data['id'] = match.group(1)

    abbr = post.select_one('._42b- abbr')
    if abbr: 
        data['date'] = dt.datetime.utcfromtimestamp(int(abbr.get('data-utime'))).strftime('%Y-%m-%d %H:%M:%S')

    views = post.select_one('.fsm.fwn.fcg')
    if views: data['views'] = parse_counter(views.text.split()[-2].casefold())

    media = post.select_one('._46-i.img')
    data['media'] = media.get('src') if media else ''
    data['type'] = "video"
    # get poster info
    poster = post.select_one('.fwb a')
    if poster:
        data['poster_link'] = poster.get('href')
        data['poster_name'] = poster.text
        data['poster_image'] = ' '

    return data

def post_criteria(d, keyword, comment, shares, views, reactions, startdate, enddate):
    if d['type'] == 'post':
        if comment and d.get('comment', -1) < comment: 
            return False
        elif shares and d.get('share', -1) < shares: 
            return False
        elif reactions and d.get('reactions', -1) < reactions: 
            return False
    else:
        if views and d.get('views', -1) < views: 
            return False

    if not d.get('id'): 
        return False

    date = d.get('date')

    if date:
        parsed = dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        parsed = parsed.date()
        if startdate and parsed < startdate or enddate and parsed > enddate:
            return False

    return True

# Be careful!
# If you change any parameter name
# The argument parser function 
# would need to be changed too!

def scrape(driver, keyword=[], comments=None, 
        shares=None, views=None, reactions=None, 
        limit=None, startdate=None, enddate=None):
    args  = ( keyword, comments, shares, views, reactions, startdate, enddate )
    time.sleep(5)
    ids = []

    if SCRAPE_POST:
        # search post
        count = 0   
        SEARCH_URL = 'https://www.facebook.com/search/str/{}/stories-keyword/stories-public'.format(keyword)
        driver.get(SEARCH_URL)
        count_ = []
        finish_flag = False

        while True:
            soup  = BeautifulSoup(driver.page_source, 'html.parser')
            posts = soup.select('._401d')
            print(len(posts), 'Posts found inside html!')

            count_.append(len(posts))
            if len(count_) > N and sum(count_[-N:]) == N * count_[-1]:
                # no more new posts
                break

            for i in range(count, len(posts)):

                data = post_data(posts[i])
                if post_criteria(data, *args):
                    if data['id'] not in ids:
                        ids.append(data['id'])
                        count += 1
                        yield data
                        if count == THRESHOLD or limit and count == limit: 
                            finish_flag = True
                            break

            if finish_flag: 
                break

            if len(posts) > 0:
                script = 'window.scrollTo(0, document.body.scrollHeight);'
                driver.execute_script(script)

            time.sleep(0.5)

    if SCRAPE_VIDEO:
        # search video
        count = 0   
        SEARCH_URL = 'https://www.facebook.com/search/videos/?q=' + keyword
        driver.get(SEARCH_URL)
        count_ = []
        finish_flag = False

        while True:
            soup  = BeautifulSoup(driver.page_source, 'html.parser')
            videos = soup.select('._6rba')
            print(len(videos), 'Videos found inside html!')

            count_.append(len(videos))
            if len(count_) > N and sum(count_[-N:]) == N * count_[-1]:
                # no more new videos
                break

            for i in range(count, len(videos)):

                data = video_data(videos[i])
                if post_criteria(data, *args):
                    if data['id'] not in ids:
                        ids.append(data['id'])
                        count += 1
                        yield data
                        if count == THRESHOLD or limit and count == limit: 
                            finish_flag = True
                            break

            if finish_flag: 
                break

            if len(videos) > 0:
                script = 'window.scrollTo(0, document.body.scrollHeight);'
                driver.execute_script(script)

            time.sleep(0.5)


def prepare_args():

    parser = argparse.ArgumentParser(
            description='Extract data from facebook newsfeed')

    parser.add_argument('--chrome-path', type=str, metavar='PATH',
            default='./chromedriver', help='Specify chromedriver path')

    parser.add_argument('-k', '--keyword', 
            type=str, help='Add keyword to filter results')

    parser.add_argument('-u', '--username', 
            type=str, help='User name on facebook')

    parser.add_argument('-p', '--password', 
            type=str, help='Password')

    parser.add_argument('-c', '--comments', 
            type=int, metavar='N', help='Number of comments')

    parser.add_argument('-s', '--shares', 
            type=int, metavar='N', help='Number of shares')

    parser.add_argument('-v', '--views', 
            type=int, metavar='N', help='Number of views')

    parser.add_argument('-r', '--reactions', 
            type=int, metavar='N', help='Number of reactions')

    parser.add_argument('-l', '--limit', 
            type=int, metavar='N', help='Number of posts')

    dargs = parser.add_argument_group('Date arguments')

    dargs.add_argument('-y', '--years', 
            type=int, metavar='N', help='Filter post from N years ago')

    dargs.add_argument('-m', '--months', 
            type=int, metavar='N', help='Filter post from N months ago')

    dargs.add_argument('-d', '--days', 
            type=int, metavar='N', help='Filter post from N days ago')

    dargs.add_argument('-t', '--today', 
            action='store_true', help='Filter only today posts')

    # Parse arguments for start date and end date
    args = parser.parse_args()
    return args

def kwargs_from_cmd(args):

    keys = ('keyword', 'comments', 'shares', 'views', 'reactions', 'limit')
    kwargs = { k: getattr(args, k) for k in keys }

    # Calcute start date from arguments
    acum = dt.date.today()
    date  = None

    if args.years is not None:
        acum -= relativedelta(years=args.years)
        date = acum

    if args.months is not None:
        acum -= relativedelta(months=args.months)
        date = acum

    if args.days is not None:
        acum -= relativedelta(days=args.days)
        date = acum

    if args.today:
        date = dt.date.today()

    kwargs['startdate'] = date
    kwargs['enddate']   = None # Always undefined?

    return kwargs

def main():
    args = prepare_args()

    print('Starting selenium...')
    driver = prepare_driver(executable_path=args.chrome_path)

    # Login into facebook
    print('Login into facebook...')
    login(driver, args.username, args.password)

    kwargs = kwargs_from_cmd(args)

    results = {
        'post': [],
        'video': []    
    }

    click_links = [ 'bit.ly', 'goo.gl', 'bitly.com' ]
    headers = { 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36' }

    for data in scrape(driver, **kwargs):
        try:
            results[data['type']].append(data)
            print('Posts: {}, Videos: {} found'.format(len(results['post']), len(results['video'])))

            # get clicks
            for ii in click_links:
                try:
                    rr = r'[\s+/+]{}/[^\s]+'.format(ii)
                    match = re.search(rr, data.get('content'))
                    url = match.group(0).strip().strip('/')
                    url = 'https://{}+'.format(url)

                    if ii == 'goo.gl':
                        driver.get(url)
                        soup  = BeautifulSoup(driver.page_source, 'html.parser')
                        count = soup.select_one('.count')
                        data['clicks'] = count.text
                        break
                    else:
                        page_source = requests.get(url, headers=headers).text
                        match = re.search(r'\{.+user_clicks.+\}', page_source)
                        data['clicks'] = json.loads(match.group(0))['user_clicks']
                        break
                except Exception as e:
                    pass

        except KeyboardInterrupt: 
            break

    for video in results['post'] + results['video']:
        driver.get(video['url'])
        soup  = BeautifulSoup(driver.page_source, 'html.parser')

        if video['type'] == 'post':
            pdb.set_trace()
            post = soup.select_one('._1dwg')
            if post:
                img = post.select_one('.uiScaledImageContainer img')
                if img:
                    video['media'] = img.get('src')
                else:
                    img = post.select_one('img._3chq')
                    if img:
                        video['media'] = img.get('src')
        else:
            post = soup.select_one('._437j')

            # get poster info
            poster = post.select_one('img._s0._4ooo._44ma._54ru.img')
            if poster:
                video['poster_image'] = poster.get('src')

            reactions = post.select('._3emk')
            video['reactions'] = 0
            for reaction in reactions:
                video['reactions'] += parse_counter(reaction.text.casefold())

            anchors = post.select('._ipo a')
            for anchor in anchors:
                if 'comment' in anchor.text.casefold(): 
                    video['comment'] = parse_counter(anchor.text.split()[0].casefold())
                elif 'share' in anchor.text.casefold(): 
                    video['share'] = parse_counter(anchor.text.split()[0].casefold())

        if PUT_DATABASE:
            database.insert_post_db(video)
        
    with open('results.json','w') as fp:
        json.dump(results['post']+results['video'], fp, indent=2)

    driver.close()

if __name__ == '__main__':
    main()
