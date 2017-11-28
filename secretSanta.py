#! /usr/bin/env python3

'''
Created by Joseph Chun
December 1 2015
Updated: 2017
'''

import csv
import os
import smtplib
import time
import random 
import emoji
import unicodedata

pathToLogFile = 'assignmentLog_' + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime()) + '.txt'
logFile = os.path.normpath(pathToLogFile)
jxp_secret_santa_csv = 'JJXP 2017 Secret Santa Sign-Up (Responses) - Form Responses 1.tsv'
secret_santa_db = {}
assignments_db = {}
guest_names = []

'''
Following functions create, populate, and assign the secret santa databases
'''
def sanitizeText(item):
    sanitizedString = ""
    for character in item:
        if character in emoji.UNICODE_EMOJI:
            sanitizedString += "[" + unicodedata.name(character) + "]"
        else:
            sanitizedString += character
    return sanitizedString

def parseCSV(fileName):
    '''
    Parse fileName arg and place information into 
    secret_santa_db and guest_names
    '''
    with open(fileName, 'rt') as csvfile:
        next(csvfile)
        secretSantaCSV = csv.reader(csvfile, dialect="excel-tab")
        for row in secretSantaCSV:
            timestamp, name, email, color, sizeM, sizeF, \
            magazine, cereal, allergies, notes = row
            if not allergies:
                allergies = 'None'
            if not notes:
                notes = 'None'
            if name == 'N/A':
                continue
            ''' 
            People started including emojis 
            We can not send emails with them, so need to convert them
            For now: only sanitize the unverified, user-defined text
            '''
            name = sanitizeText(name)
            allergies = sanitizeText(allergies)
            notes = sanitizeText(notes)
            ''' Store all info in database, indexed by name '''
            secret_santa_db[name] = (email, color, sizeM, sizeF,\
                                     magazine, cereal, allergies,\
                                     notes)
            guest_names.append(name)

def assignNames(source_db):
    '''
    Shuffle guest names, then put assignments in assignments_db
    '''
    redo = False
    givers = random.sample(guest_names, len(guest_names))
    receivers = random.sample(guest_names, len(guest_names))
    for index in range(len(guest_names)):
        if givers[index] == receivers[index]:
            print("Self assignment detected! Starting over assignments!")
            redo = True
            break
        assignments_db[givers[index]] = receivers[index]
    '''
    Lets assume that we won't hit the recursion limit here 
    What are the chances of that happening over and over again right??
    '''
    if redo:
        assignNames(source_db)

'''
Helper functions to print contents of databases
'''
def printDB(database):
    for key, value in database.items():
        print('***')
        print(key)
        email, color, sizeM, sizeF, magazine, cereal, allergies, notes \
                = value
        print('email:       ' + email)
        print('color:       ' + color)
        print('sizeM:       ' + sizeM)
        print('sizeF:       ' + sizeF)
        print('magazine:    ' + magazine)
        print('cereal:      ' + cereal)
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
def constructEmail(giver, receiver, to, gmail_user):
    header = 'To:' + to + '\n' + \
             'From: ' + gmail_user + '\n' + \
             'Subject: JJXP 2017 Secret Santa Assignment!\n'
    msg_intro = 'Hi ' + giver + \
                ',\n\nYou have been assigned ' + receiver + '!\n'
    msg_info = 'Here is some more info about ' + receiver + '...\n\n'

    email, color, sizeM, sizeF, magazine, cereal, allergies, notes \
            = secret_santa_db[receiver]
    color_info =        'Favorite color: ' + color + '\n'
    size_info = ''
    if sizeM:
        size_info += str('Men shirt size: ' + sizeM + '\n')
    if sizeF:
        size_info += str('Women shirt size: ' + sizeF + '\n')
    magazine_info =     'Likes magazines: ' + magazine + '\n'
    cereal_info =       'Cereal life philosophy: ' + cereal + '\n'
    allergies_info =    'Allergies: ' + allergies + '\n'
    notes_info =        'Additional notes: ' + notes + '\n\n'

    receiver_info = color_info + size_info + magazine_info + \
                    cereal_info + allergies_info + notes_info

    rules = 'Recommended gift range is $20-25, with absolute max of $30. Do NOT reveal your Secret Santa identity to your giftee OR to other participants! If you need more information about your giftee, try to be discreet. Good luck and have fun!\n\nMerry Christmas!\nJXP-bot\n'

    signature = '\n\nSent from an unmonitored email address. Joey will not check this email inbox until after JJXP!'

    content =  msg_intro + msg_info + receiver_info + rules + signature
    
    msg = header + '\n' + content
   
    return msg

def sendEmail(giver, receiver):
    to = 'joeyeatsspam@gmail.com' #@TODO replace with secret_santa_db[giver][0]
    gmail_user = 'joeyalerter@gmail.com'
    gmail_pwd = '***' #@TODO replace with real password
    msg = constructEmail(giver, receiver, to, gmail_user)
    #print(msg) #@DEBUG
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    # identify ourselves to smtp gmail client
    smtpserver.ehlo()
    # secure our email with tls encryption
    smtpserver.starttls()
    # re-identify ourselves as an ecrypted connection
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_pwd)
    #smtpserver.sendmail(gmail_user, to, msg) #@TODO uncomment 
    smtpserver.close()

def sendAssignments():
    for giver, receiver in assignments_db.items():
        sendEmail(giver, receiver)

def main():
    parseCSV(jxp_secret_santa_csv)
    assignNames(secret_santa_db)
    #printDB(secret_santa_db) #@DEBUG
    logAssignments(assignments_db)
    sendAssignments()

if __name__ == '__main__':
    startTime = time.time()
    main()
    print('Time taken: ' + str(time.time()-startTime) + ' secs')
