#!/usr/bin/python -tt
"""Notification classes for implementing Long View functionality"""

# Copyright (c) 2004, The Long Now Foundation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = "Dan Mosedale <timeline@list.longnow.org>"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2004 The Long Now Foundation"
__license__ = "BSD-style"

import os
import datetime
import csv
import smtplib
import tempfile
import textwrap

import lvutils


def init(filename):
    """Execute filename in the lvnotify module global namespace.

    filename -- file to execute.   Normally this is the template file.

    This allows any symbols in the lvnotify namespace to be overridden
    or extended.  Intended mostly for people who want to replace or extend
    the default notification/notifier classes.
    """

    execfile(filename, globals())
    return


class DefaultNotification:
    """Default notification class"""
    
    def __init__(self, row, date, whom, text, status, index):
        """Initialize a DefaultNotification object

        row -- timeline row that this is associated with, if any (may be None)
        date -- LVDate of when the notification should happen
        whom -- string representing who should be notified
        text -- text of the notification
        status -- field starts with one of ("Unsent", "Sent", "Retrying")
        index -- index into the notifications array where this is stored
        """

        self.row = row
        self.date = date
        self.whom = whom
        self.text = text
        self.status = status
        self.index = index

        return


class DefaultNotifier:
    """Default notifier class used by longview.py.  Reads notifications
    from a CSV file.  Each line in the file has four fields: date, whom to
    notify, notification text, and status.   An empty or non-existent status
    field is assumed to be equivalent to "Unsent".  After updateFile() is
    called, a newly written version of the file replaces the existing one.
    """
    
    def __init__(self, filename, fromString, smtpServer="localhost",
                 alwaysPrint5DigitYears=True):
        """Initialize a DefaultNotifier object.

        filename -- name of CSV file to read notifications from (and later
                    rewritten to)
        fromString -- notifications should appear to come from this address
        smtpServer -- SMTP server name to use (default: localhost)
        alwaysPrint5DigitYears -- zero pad all years to 5 digits long?
        """

        # initialize variables
        self.__fromString = fromString
        self.__filename = filename
        self.__smtpServer = smtpServer
        self.__smtpObject = None
        self.__alwaysPrint5DigitYears = alwaysPrint5DigitYears
        
        self.subject = "Long View Notification"
        """Subject field for notification mails"""

        self.notificationClass = DefaultNotification
        """Class to be used to represent notification event"""

        self.notifications = []
        """List of all notification events"""
        
        # read the data file into memory
        reader = csv.reader(file(self.__filename))
        index = 0
        for row in reader:
            if len(row) == 5:
                self.notifications.append(
                    self.notificationClass(eval(row[0]),
                                           lvutils.LVDate(row[1]), row[2],
                                           row[3], row[4], index))
            else:
                self.notifications.append(
                    self.notificationClass(eval(row[0]),
                                           lvutils.LVDate(row[1]), row[2],
                                           row[3], "Unsent", index))
            index += 1

        return

        
    def getPendingNotifications(self):
        """Returns an array containing all notifications which should
        now be processed.  Each notification is represented as an array
        of the form (date, whom-to-notify string, notification-text string).
        """

        pending = []
        
        # get the current date
        nowDate = self.__getCurrentLVDate()

        # iterate through the notifications
        for notification in self.notifications:

            # if this matches the current date, and the notification
            # has not already been sent...
            if notification.date == nowDate and \
                   not notification.status.startswith('Sent'):
                pending.append(notification)

        return pending


    def notify(self, notification):
        """Send out a notification.

        notification -- the notification to be sent
        """

        try:
            # construct and send the message
            message = self.__buildNotificationMail(self.__fromString,
                                                   notification.whom,
                                                   self.subject,
                                                   notification.text)

            # lazily initialize, otherwise we would end up with unnecessary
            # server connections
            if self.__smtpObject is None:
                self.__smtpObject = smtplib.SMTP(self.__smtpServer)
                
            self.__smtpObject.sendmail(self.__fromString,
                                       notification.whom.split(","), message)

            # Create a sent string with a displayable date
            dateSent = datetime.date.today()
            if self.__alwaysPrint5DigitYears:
                sentString = 'Sent ' + dateSent.strftime("%B %d, %05Y")
            else:
                sentString = 'Sent ' + dateSent.strftime("%B %d, %Y")

            # update our internal table
            self.notifications[notification.index].status = sentString
            

        except Exception, ex:
            # try again on the next run, and propagate the failure up
            self.notifications[notification.index].status = 'Retrying';
            raise ex
        
        return
    

    def updateDataFile(self):
        """Write updated data file and move it into place"""

        # write out the updated data file
        tempFile, tempName = tempfile.mkstemp(".tmp", "notify",
                                              os.path.dirname(self.__filename))
        writer = csv.writer(os.fdopen(tempFile, "w"),
                            lineterminator=os.linesep)
        for notification in self.notifications:
            writer.writerow(
                [repr(notification.row),
                 notification.date.toString(resolutionInYears=False),
                 notification.whom, notification.text, notification.status])
        del writer # force the writer to close the file

        # keep the existing file around, just in case
        os.rename(self.__filename, self.__filename + ".old")

        # move the new file into place
        try:
            os.rename(tempName, self.__filename)
        except Exception, ex:
            # if we fail, move the .old file back and propagate the error up
            os.rename(self.__filename + ".old", self.__filename)
            raise ex
        
        return


    def getLastNotified(self):
        """Return the last successful notification."""

        # sort the notifications by reverse-date
        reversed = self.notifications
        reversed.sort(self.__compare)
        reversed.reverse()

        # find the last sent successfully
        last = None
        for notification in reversed:
            if notification.status.startswith("Sent"):
                last = notification
                break

        return last


    def getNextUpcoming(self):
        """Return the next upcoming notification"""

        # sort the notifications by date
        sorted = self.notifications
        sorted.sort(self.__compare)

        # find the first Retrying or Unsent
        next = None
        for notification in sorted:
            if not notification.status.startswith("Sent"):
                next = notification
                break

        return next
    
    
    def __getCurrentLVDate(self):
        """Return the current date as an LVDate object."""

        today = datetime.date.today()

        return lvutils.LVDate(today.year*12 + today.month-1)


    def __buildNotificationMail(self, fromString, toString, subject, body):
        """Return the SMTP message to be sent

        fromString -- the sender
        toString -- string containing the comma-separated list of recipients
        subject -- the subject
        body -- string to be wrapped and used as the message body
        """

        return "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (
            fromString, toString, subject, textwrap.fill(body))


    def __compare(self, a, b):
        """Used to sort the array of notifications by date."""

        return cmp(a.date, b.date)

