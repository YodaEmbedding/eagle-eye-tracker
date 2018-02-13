#!/usr/bin/env python2

from time import gmtime, strftime

import nxt.bluesock

b = nxt.bluesock.BlueSock('00:16:53:01:B8:C3').connect()

# Port: usb
# Port: BTH::M1

# import nxt.locator
# b = nxt.locator.find_one_brick()

print 'Connected!'

# for box in range(10):
#     b.message_write(box, 'message test %d' % box)
# 
# for box in range(10):
#     local_box, message = b.message_read(box, box, True)
#     print local_box, message

box = 1

while True:
	msg = strftime("%H:%M:%S", gmtime())
	# message_write(inbox, message)
	b.message_write(box, msg)

while True:
	try:
		# message_read(remote_inbox, local_inbox, remove)
		local_box, message = b.message_read(1, 5, True)
		print local_box, message
		break
	except Exception:
		pass

print 'Test succeeded!'

