import urllib.request
from urllib.error import URLError

from subprocess import run
import os
import sqlite3

import cv2
import numpy as np


def create_db():
    """
    Create SQlite Database and table, that containe:
    "USER_ID" - Telegram user id
    "VOICE_ID" - Current number of audio file
    "PHOTO_ID" - Current number of photo file
    """
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect("data/database.sqlite")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE "USERS" (
                   "USER_ID"    INTEGER NOT NULL,
                   "VOICE_ID"   INTEGER DEFAULT 0,
                   "PHOTO_ID"   INTEGER DEFAULT 0,
                   PRIMARY KEY("USER_ID"))
                   """)
    conn.close()
    print('DataBase created')


def create_user(id):
    """
    Create new user PATH if it doesn't exist
    and make new record in database.
    """
    if not os.path.exists(f'data/{id}'):
        conn = sqlite3.connect("data/database.sqlite")
        with conn:
            cursor = conn.cursor()

            os.makedirs(f'data/{id}/voices')
            os.makedirs(f'data/{id}/photos')

            cursor.execute(
                "INSERT OR IGNORE INTO USERS (USER_ID) VALUES (?)", (id,))
            conn.commit()

            cursor.execute(
                "UPDATE USERS SET VOICE_ID = 0, PHOTO_ID = 0 WHERE USER_ID = ?",
                (id,))
            conn.commit()

            print('User created')


def save_voice(url, id=0):
    """
    Load voice message file from URL, convert to WAV format
    and save in user directory on index number.
    """
    result = {'returncode': -1, 'voice_id': -1}

    try:
        buf = urllib.request.urlopen(url).read()
    except URLError:
        print('URLError')
        return result

    conn = sqlite3.connect("data/database.sqlite")
    with conn:
        cursor = conn.cursor()

        cursor.execute("SELECT VOICE_ID FROM USERS WHERE USER_ID = ?", (id,))

        voice_id = cursor.fetchone()[0]
        result['voice_id'] = voice_id

        # run ffmpeg library
        p = run(["ffmpeg", "-loglevel", "level+warning",
                 "-f", "ogg", "-i", "-",
                 "-acodec", "pcm_s16le", "-ar", "16000",
                 f"data/{id}/voices/voice_massage_{voice_id}.wav",
                 "-y"], input=buf)

        if not p.returncode:
            result['returncode'] = 0
            voice_id += 1
            cursor.execute("UPDATE USERS SET VOICE_ID = ? WHERE USER_ID = ?",
                           (voice_id, id,))
            conn.commit()
    
    return result


def save_photo(url, id=0):
    """
    Load photo file from URL and find faces on it
    with detector base on Haar-like feature.
    Save file in user directory in face was found.
    """
    try:
        buf = urllib.request.urlopen(url).read()
    except URLError:
        print('URLError')
        return -1

    #load img file and detect faces
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    nparr = np.fromstring(buf, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.2, 4)

    if faces != ():
        conn = sqlite3.connect("data/database.sqlite")
        with conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT PHOTO_ID FROM USERS WHERE USER_ID = ?", (id,))
            photo_id = cursor.fetchone()[0]

            p = cv2.imwrite(
                f"data/{id}/photos/photo_{photo_id}.jpg", img)
            if p:
                photo_id += 1
                cursor.execute("UPDATE USERS SET PHOTO_ID = ? WHERE USER_ID = ?",
                               (photo_id, id,))
                conn.commit()
                return 0

    return -1
