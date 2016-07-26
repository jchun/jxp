#! /usr/bin/env python

'''
Created by Joseph Chun
December 1 2015
'''

import csv
import os
import smtplib
import time
from random import shuffle

pathToLogFile = 'assignmentLog_' + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime()) + '.txt'
logFile = os.path.normpath(pathToLogFile)
jxp_secret_santa_csv = 'JXP 2015 Secret Santa Sign-Up (Responses) - Form Responses 1.tsv'
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
    with open(fileName, 'rb') as csvfile:
        next(csvfile)
        secretSantaCSV = csv.reader(csvfile, dialect="excel-tab")
        for row in secretSantaCSV:
            timestamp, color, interests, allergies, notes, name, email = row
            if not allergies:
                allergies = 'None'
            if not notes:
                notes = 'None'
            if name == 'N/A':
                continue
            secret_santa_db[name] = (email, color, \
                                    interests, allergies, notes)
            guest_names.append(name)

def assignNames(source_db):
    '''
    Shuffle guest names, then put assignments in assignments_db
    '''
    shuffle(guest_names)
    for index in xrange(0, len(guest_names)):
        if index == len(guest_names) - 1:
            assignments_db[guest_names[index]] = guest_names[0]
            continue
        assignments_db[guest_names[index]] = guest_names[index+1]

'''
Helper functions to print contents of databases
'''

def printDB(database):
    for key, value in database.iteritems():
        print '***'
        print key
        email, color, interests, allergies, notes = value
        print 'email:       ' + email
        print 'interests:   ' + interests
        print 'allergies:   ' + allergies
        print 'notes:       ' + notes
        print '***'

def logAssignments(database):
    with open(logFile, "a") as f:
        f.write('Start Secret Santa Log ***\n')
        for key, value in database.iteritems():
            f.write('***\n')
            f.write(key + '\t : \t' +  value + '\n')

'''
Following functions to email assigned secret santa info
'''
def sendEmail(giver, receiver):
    to = 'joeyeatsspam@gmail.com' #@TODO replace with secret_santa_db[giver][0]
    gmail_user = 'joeyalerter@gmail.com'
    gmail_pwd = '*'
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: JXP 2015 Secret Santa Assignment!\n'
    
    msg_intro = 'Hi ' + giver + ',\n\nYou have been assigned ' + receiver + '!\n'
    msg_info = 'Here is some more info about ' + receiver + '...\n\n'
    
    email, color, interests, allergies, notes = secret_santa_db[receiver]

    color_info =        'Favorite color: ' + color + '\n'
    interests_info =    'Interests: ' + interests + '\n'
    allergies_info =    'Allergies: ' + allergies + '\n'
    notes_info =        'Additional notes: ' + notes + '\n\n'

    receiver_info = color_info + interests_info + allergies_info + notes_info

    rules = 'Gift range is $20-30, but try to keep it at less than $25. Do NOT reveal your Secret Santa identity to your giftee OR to other participants. If you need more information about your giftee, try to be discrete. Good luck and have fun!\n\nMerry Christmas!\nJXP-bot\n'

    content =  msg_intro + msg_info + receiver_info + rules
    
    msg = header + '\n' + content

    print msg #@TODO comment out
    #@TODO uncomment smtpserver.sendmail(gmail_user, to, msg)
    smtpserver.close()

def sendAssignments():
    for giver, receiver  in assignments_db.iteritems():
        sendEmail(giver, receiver)

def main():
    parseCSV(jxp_secret_santa_csv)
    assignNames(secret_santa_db)
    logAssignments(assignments_db)
    sendAssignments()

if __name__ == '__main__':
    startTime = time.time()
    main()
    print 'Time taken: ' + str(time.time()-startTime) + ' secs'
