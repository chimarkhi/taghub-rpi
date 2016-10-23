from apscheduler.schedulers.blocking import BlockingScheduler
import os
import bleadv
import bledb
import time
import datetime

sched = BlockingScheduler()
printdata = range(0,20)

@sched.scheduled_job('interval',seconds = 10)
def TaskOne():
	print 1,datetime.datetime.now()
		
@sched.scheduled_job('interval',seconds = 5)
def TaskTwo():
	print 2,datetime.datetime.now()

sched.start()
