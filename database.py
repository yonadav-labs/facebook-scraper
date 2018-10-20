#!/usr/bin/env python3.6
# Your not so pretty module

import mysql.connector as sql
import json

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
    "(FB_ID, Link, Post_Date, Content, Main_Image, Post_Type, Title, Poster_Name, Poster_Link, Poster_Img) " \
    "VALUES " \
    "(%(FB_ID)s, %(Link)s, %(Post_Date)s, %(Content)s, %(Main_Image)s, %(Type)s, %(Title)s, %(Poster_Name)s, %(Poster_Link)s, %(Poster_Img)s) " \
    "ON DUPLICATE KEY UPDATE " \
    "Content=VALUES(Content)"

ADD_TRACK = \
    "INSERT INTO FB_Track " \
    "(FB_ID, Views, Comments, Shares, Reactions, Clicks) " \
    "VALUES " \
    "(%(FB_ID)s, %(Views)s, %(Comments)s, %(Shares)s, %(Reactions)s, %(Clicks)s) " \
    "ON DUPLICATE KEY UPDATE " \
    "Views=VALUES(Views), " \
    "Comments=VALUES(Comments), " \
    "Shares=VALUES(Shares), " \
    "Reactions=VALUES(Reactions) "

ADD_TREND = "INSERT IGNORE INTO FB_Trends (FB_ID) VALUES  (%(FB_ID)s)"

def prepare_post_frame(post):
    keys = { 'id': 'FB_ID', 'url': 'Link', 'date': 'Post_Date', 'title': 'Title',
             'content': 'Content', 'media': 'Main_Image', 'type': 'Type', 
             'poster_name': 'Poster_Name', 'poster_link': 'Poster_Link', 'poster_image': 'Poster_Img' 
            }
    # Created_Date
    # Updated_Date
    return { c: post.get(k) for k, c in keys.items() }

def prepare_track_frame(track):

    keys = { 'id': 'FB_ID', 'views': 'Views', 'comment': 'Comments', 
        'share': 'Shares', 'reactions': 'Reactions', 'clicks': 'Clicks' }
    # Updated_Date
    return { c: track.get(k) for k, c in keys.items() }

def insert_post_db(data):

    # Error printing data?

    post  = prepare_post_frame(data)
    track = prepare_track_frame(data)

    cnx = sql.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SET NAMES utf8mb4;") 
    cursor.execute(ADD_POST, post)
    cursor.execute(ADD_TRACK, track)
    cursor.execute(ADD_TREND, { 'FB_ID': data['id'] })

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

