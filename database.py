#!/usr/bin/env python3.6
# Your not so pretty module

import mysql.connector as sql
import json
import datetime


config = {
    'user': 'orchid_staging',
    'password': 'q5W[Wg?9x6*1',
    'database': 'orchid_staging',
    'charset': 'utf8',
    'use_unicode': True,
    'unix_socket': '/var/lib/mysql/mysql.sock'
}

ADD_POST = \
    "INSERT INTO FB_Post " \
    "(FB_ID, Link, Post_Date, Content, Main_Image, Post_Type, Title, Poster_Name, Poster_Link, Poster_Img, Created_Date, Update_Date) " \
    "VALUES " \
    "(%(FB_ID)s, %(Link)s, %(Post_Date)s, %(Content)s, %(Main_Image)s, %(Type)s, %(Title)s, %(Poster_Name)s, %(Poster_Link)s, %(Poster_Img)s, %(Created_Date)s, %(Update_Date)s) " \
    "ON DUPLICATE KEY UPDATE " \
    "Content=VALUES(Content), Update_Date=VALUES(Update_Date)"

ADD_TRACK = \
    "INSERT INTO FB_Track " \
    "(FB_ID, Views, Comments, Shares, Reactions, Clicks, Update_Date) " \
    "VALUES " \
    "(%(FB_ID)s, %(Views)s, %(Comments)s, %(Shares)s, %(Reactions)s, %(Clicks)s, %(Update_Date)s) " \
    "ON DUPLICATE KEY UPDATE " \
    "Views=VALUES(Views), " \
    "Comments=VALUES(Comments), " \
    "Shares=VALUES(Shares), " \
    "Update_Date=VALUES(Update_Date), " \
    "Reactions=VALUES(Reactions) "

ADD_TREND = "INSERT IGNORE INTO FB_Trends (FB_ID) VALUES  (%(FB_ID)s)"

def prepare_post_frame(post):
    keys = { 'id': 'FB_ID', 'url': 'Link', 'date': 'Post_Date', 'title': 'Title',
             'content': 'Content', 'media': 'Main_Image', 'type': 'Type', 
             'poster_name': 'Poster_Name', 'poster_link': 'Poster_Link', 'poster_image': 'Poster_Img' 
            }

    post = { c: post.get(k) for k, c in keys.items() }
    post['Created_Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    post['Update_Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return post

def prepare_track_frame(track):

    keys = { 'id': 'FB_ID', 'views': 'Views', 'comment': 'Comments', 
        'share': 'Shares', 'reactions': 'Reactions', 'clicks': 'Clicks' }
    track = { c: track.get(k) for k, c in keys.items() }
    track['Update_Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return track

def insert_post_db(data):

    # Error printing data?

    post  = prepare_post_frame(data)
    track = prepare_track_frame(data)

    cnx = sql.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SET NAMES utf8mb4;") 
    cursor.execute(ADD_POST, post)
    cursor.execute(ADD_TREND, { 'FB_ID': data['id'] })
    cursor.execute(ADD_TRACK, track)

    print('Inserted post', cursor.lastrowid)
    cnx.commit()

    cursor.close()
    cnx.close()

def main():
    cnx = sql.connect(**config)
    print('Works...')
    cnx.close()

if __name__ == '__main__':
    main()

