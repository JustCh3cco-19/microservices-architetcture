import pika


def produce(subject:str, 
			data:bytes, 
			connection = None,                  # put previous produce function call's return value here to use the same connection
			channel = None,                     # put previous produce function call's return value here to use the same channel
			close_channel = False,              # set True to close che channel
			close_connection = False,           # set True to close che connection
			broker_ip_addr = "message-broker",  # Must become docker env
			broker_amqp_port = 5672,            # Must become docker env
			broker_virtual_host = "/",          # Must become docker env
			broker_creds_user = "admin",        # Must become docker secrets
			broker_creds_pswd = "admin") -> (pika.BlockingConnection, pika.adapters.blocking_connection.BlockingChannel):                     

	try:

		# Connect to the Message Broker if not
		if not connection or not channel:
			credentials = pika.PlainCredentials(broker_creds_user, broker_creds_pswd)
			parameters  = pika.ConnectionParameters(broker_ip_addr, broker_amqp_port, broker_virtual_host, credentials)
			connection = pika.BlockingConnection(parameters)
			channel = connection.channel()

		# Declare queue to send frames to
		channel.queue_declare(queue = subject)

		# Data enqueing
		channel.basic_publish(exchange = '', routing_key = subject, body = data)
				
		if close_channel:
			channel.close()
		if close_connection:
			connection.close()
			
		return connection, channel

	# Close the connection in case of errors
	except:

		try:
			channel.close()
		except:
			pass

		try:
			connection.close()
		except:
			pass

		raise


def consume(subject:str,
			consumed_data:list[bytes], 
			amount:int = 1, 
			connection = None,                  # put previous consume function call's return value here to use the same connection
			channel = None,                     # put previous consume function call's return value here to use the same channel
			close_channel = False,              # set True to close che channel
			close_connection = False,           # set True to close che connection
			broker_ip_addr = "message-broker",  # Must become docker env
			broker_amqp_port = 5672,            # Must become docker env
			broker_virtual_host = "/",          # Must become docker env
			broker_creds_user = "admin",        # Must become docker secrets
			broker_creds_pswd = "admin") -> (pika.BlockingConnection, pika.adapters.blocking_connection.BlockingChannel):
	
	if not type(consumed_data) == list:
		raise TypeError("consumed_data must be a list object")
	
	if amount < 1:
		raise ValueError("amount must be greater than zero")

	try:

		# Connect to the Message Broker if not already connected
		if not connection or not channel:
			credentials = pika.PlainCredentials(broker_creds_user, broker_creds_pswd)
			parameters  = pika.ConnectionParameters(broker_ip_addr, broker_amqp_port, broker_virtual_host, credentials)
			connection = pika.BlockingConnection(parameters)
			channel = connection.channel()

		# Declare queue to send frames to
		channel.queue_declare(queue = subject)

		"""
		for method, properties, body in channel.consume(queue = subject, auto_ack = True):
			if len(consumed_data) < amount:
				consumed_data.append(body)
			else:
				channel.cancel()
		"""

		# Consume the provided amount of data 
		method, properties, body = True, True, True
		while (method, properties, body) != (None, None, None) and len(consumed_data) < amount:
			method, properties, body = channel.basic_get(queue = subject, auto_ack = True)
			consumed_data.append(body)

		if close_channel:
			channel.close()
		if close_connection:
			connection.close()
			
		return connection, channel
	
	except:

		try:
			channel.close()
		except:
			pass
		
		try:
			connection.close()
		except:
			pass

		consumed_data.append(None)
		return None, None
	
	