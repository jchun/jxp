#! /usr/bin/env python3

'''
Created by Joseph Chun
December 1 2015
Updated: 2016
'''

import csv
import os
import smtplib
import time
from random import shuffle

pathToLogFile = 'assignmentLog_' + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime()) + '.txt'
logFile = os.path.normpath(pathToLogFile)
jxp_secret_santa_csv = 'JJXP 2016 Secret Santa Sign-Up (Responses) - Form Responses 1.tsv'
secret_santa_db = {}
assignments_db = {}
guest_names = []

'''
Following functions create, populate, and assign the secret santa databases
'''

def parseCSV(fileName):
    '''
    Parse fileName arg and place information into secret_santa_db and guest_names
    '''
    with open(fileName, 'rt') as csvfile:
        next(csvfile)
        secretSantaCSV = csv.reader(csvfile, dialect="excel-tab")
        for row in secretSantaCSV:
            timestamp, name, email, color, size, movie, magicSB, allergies, notes = row
            if not allergies:
                allergies = 'None'
            if not notes:
                notes = 'None'
            if name == 'N/A':
                continue
            secret_santa_db[name] = (email, color, size,\
                                     movie, magicSB, allergies,\
                                     notes)
            guest_names.append(name)

def assignNames(source_db):
    '''
    Shuffle guest names, then put assignments in assignments_db
    '''
    shuffle(guest_names)
    for index in range(0, len(guest_names)):
        if index == len(guest_names) - 1:
            assignments_db[guest_names[index]] = guest_names[0]
            continue
        assignments_db[guest_names[index]] = guest_names[index+1]

'''
Helper functions to print contents of databases
'''

def printDB(database):
    for key, value in database.items():
        print('***')
        print(key)
        email, color, size, movie, magicSB, allergies, notes \
                = value
        print('email:       ' + email)
        print('color:       ' + color)
        print('size:        ' + size)
        print('movie:       ' + movie)
        print('magicSB:     ' + magicSB)
        print('allergies:   ' + allergies)
        print('notes:       ' + notes)
        print('***')

def logAssignments(database):
    with open(logFile, "a") as f:
        f.write('Start Secret Santa Log ***\n')
        for key, value in database.items():
            f.write('***\n')
            f.write(key + '\t : \t' +  value + '\n')

'''
Following functions to email assigned secret santa info
'''
def sendEmail(giver, receiver):
    to = 'joeyeatsspam@gmail.com' #@TODO replace with secret_santa_db[giver][0]
    gmail_user = 'joeyalerter@gmail.com'
    gmail_pwd = '***'
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    # identify ourselves to smtp gmail client
    smtpserver.ehlo()
    # secure our email with tls encryption
    smtpserver.starttls()
    # re-identify ourselves as an ecrypted connection
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: JJXP 2016 Secret Santa Assignment!\n'
    
    msg_intro = 'Hi ' + giver + ',\n\nYou have been assigned ' + receiver + '!\n'
    msg_info = 'Here is some more info about ' + receiver + '...\n\n'
    
    email, color, size, movie, magicSB, allergies, notes = secret_santa_db[receiver]

    color_info =        'Favorite color: ' + color + '\n'
    size_info =         'Shirt size: ' + size + '\n'
    movie_info =        'Likes movies: ' + movie + '\n'
    magicSB_info =      'Most similar to: ' + magicSB + '\n'
    allergies_info =    'Allergies: ' + allergies + '\n'
    notes_info =        'Additional notes: ' + notes + '\n\n'

    receiver_info = color_info + size_info + movie_info + \
                    magicSB_info +allergies_info + notes_info

    rules = 'Gift range is $20-30. Do NOT reveal your Secret Santa identity to your giftee OR to other participants, including your significant other! If you need more information about your giftee, try to be discrete. Good luck and have fun!\n\nMerry Christmas!\nJXP-bot\n'

    content =  msg_intro + msg_info + receiver_info + rules
    
    msg = header + '\n' + content

    print(msg) #@TODO comment out
    #smtpserver.sendmail(gmail_user, to, msg) #@TODO uncomment 
    smtpserver.close()

def sendAssignments():
    for giver, receiver  in assignments_db.items():
        sendEmail(giver, receiver)

def main():
    parseCSV(jxp_secret_santa_csv)
    assignNames(secret_santa_db)
    logAssignments(assignments_db)
    sendAssignments()

if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Time taken: ' + str(time.time()-startTime) + ' secs')
