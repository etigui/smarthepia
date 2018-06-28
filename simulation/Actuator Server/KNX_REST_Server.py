# -*- coding: utf-8 -*-
import socket,sys
from knxnet import *
from flask import Flask, jsonify, request

app = Flask(__name__)


IDs=["4/1","4/2","4/3","4/10","4/11","4/12"]


udp_ip = "127.0.0.1"
udp_port = 3671


#### Standard route. Not to be used by students. Instead use next routes ####

@app.route("/cmd/<addr1>/<addr2>/<addr3>/<data>/<data_size>/<apci>")
def hello(addr1,addr2,addr3,data,data_size,apci):
	# sending a command
	addr=addr1+"/"+addr2+"/"+addr3
	dest_addr = knxnet.GroupAddress.from_str(addr)
	result    = send_data_to_group_addr(dest_addr, int(data), int(data_size), int(apci) ) 
	print(result)
	return jsonify(result=result)

#### Routes to be used by students ####
# Status define
# 0 => success
# 1 => error (404, 500, other actuator function)

@app.route("/", methods=['GET'],strict_slashes=False)
def root():
	return jsonify(status=0, result="success")

@app.errorhandler(500)
def internal_error(error):
	return jsonify(status=1, result=f"Server internal error")

@app.errorhandler(404)
def not_found(error):
	return jsonify(status=1, result=f"Route not found")

@app.route("/v0/blind/write/<floor>/<id>/<value>", methods=['GET'],strict_slashes=False)
def blind_write(floor, id, value):
	if request.method=='GET':
		address = f"{floor}/{id}"
		if (address not in IDs):
			return jsonify(status=1, result="Wrong blind ID")
		if (int(value) < 0) or (int(value) > 255):
			return jsonify(status=1, result="Wrong value... Keep it between 0 and 255")	
		dest_addr = knxnet.GroupAddress.from_str(f"3/{address}")
		result = send_data_to_group_addr(dest_addr, int(value), 2, 2 ) 
		print(result)
		return jsonify(status=0, result=result)
	return jsonify(status=1, result='use GET method')


@app.route("/v0/blind/read/<floor>/<id>")
def blind_read(floor, id):
	# sending a command
	address = f"{floor}/{id}"
	if (address not in IDs):
		return jsonify(status=1, result="Wrong blind ID")
	dest_addr = knxnet.GroupAddress.from_str(f"4/{address}")
	result = send_data_to_group_addr(dest_addr, 0, 2, 0) 
	print(result)
	return jsonify(status=0, result=result)


@app.route("/v0/valve/write/<floor>/<id>/<value>", methods=['GET'],strict_slashes=False)
def valve_write(floor, id, value):
	if request.method=='GET':
		address = f"{floor}/{id}"
		if (address not in IDs):
			return jsonify(status=1, result="Wrong valve ID")
		if (int(value) < 0) or (int(value) > 255):
			return jsonify(status=1, result="Wrong value... Keep it between 0 and 255")	
		dest_addr = knxnet.GroupAddress.from_str(f"0/{address}")
		result = send_data_to_group_addr(dest_addr, int(value), 2, 2 ) 
		print(result)
		return jsonify(status=0, result=result)
	return jsonify(status=1, result='use GET method')


@app.route("/v0/valve/read/<floor>/<id>")
def radiator_read(floor, id):
	# sending a command
	address = f"{floor}/{id}"
	if (address not in IDs):
		return jsonify(status=1, result="Wrong valve ID")
	dest_addr = knxnet.GroupAddress.from_str(f"0/{address}")
	result = send_data_to_group_addr(dest_addr, 0, 2, 0 ) 
	print(result)
	return jsonify(status=0, result=result)


def send_data_to_group_addr(dest_group_addr, data, data_size, apci ):
	data_endpoint = ('0.0.0.0', 0)  
	control_enpoint = ('0.0.0.0', 0)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('',3672))
	
	
	# -> Connection request
	conn_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
								   control_enpoint,
								   data_endpoint)
	sock.sendto(conn_req.frame, (udp_ip, udp_port))

	# <- Connection response
	data_recv, addr = sock.recvfrom(1024)
	conn_resp = knxnet.decode_frame(data_recv)
	print(conn_resp.status)
	
	if conn_resp.status == 0x0:
			# -> Connection state request
			conn_state_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
												 conn_resp.channel_id,
												 control_enpoint)
			sock.sendto(conn_state_req.frame, (udp_ip, udp_port))

			# <- Connection state response
			data_recv, addr = sock.recvfrom(1024)
			conn_state_resp = knxnet.decode_frame(data_recv)
			print(conn_state_resp.status)
			
			if conn_state_resp.status == 0x0:
				# -> Tunnel request ##################
				tunnel_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
												 dest_group_addr,
												 conn_resp.channel_id,
												 data,
												 data_size,
												 apci)
				sock.sendto(tunnel_req.frame, (udp_ip, udp_port))

				# <- Tunnel ack
				data_recv, addr = sock.recvfrom(1024)
				ack = knxnet.decode_frame(data_recv)
				print(ack.status)
				
				if ack.status == 0x0:
					####### <- Tunnel Request
					data_recv, addr = sock.recvfrom(1024)
					tunnel_req_recv = knxnet.decode_frame(data_recv)
					
					####### -> Tunnel ack
					if tunnel_req_recv.data_service == 0x2e:
						status_error = 0x00
					else:
						status_error = 0x01
					tunnel_ack = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_ACK,
													 conn_resp.channel_id,
													 status_error,
													 tunnel_req_recv.sequence_counter)
					sock.sendto(tunnel_ack.frame, (udp_ip, udp_port))

					
					if apci == 0x0: # if apci == 0x0 then the command sent was a read command we get an extra Tunnel Request datagram containing the value
					
						####### <- Tunnel Request (Last Response from read)
						data_recv, addr = sock.recvfrom(1024)
						tunnel_req_recv_bis = knxnet.decode_frame(data_recv)
				
				
			# Disconnect request
			disconnect_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST,
												 conn_resp.channel_id,
												 control_enpoint)
			sock.sendto(disconnect_req.frame, (udp_ip, udp_port))

			# Disconnect response
			data_recv, addr = sock.recvfrom(1024)
			disconnect_resp = knxnet.decode_frame(data_recv)
		
	if apci == 0x0: # if the command sent was a read command we return the value else we return a confirmation message
		if tunnel_req_recv_bis is not None:
			return str(tunnel_req_recv_bis.data)
	elif ((tunnel_ack is not None) and (tunnel_ack.status == 0x0)):
		return 'Command sent'
	else:
		return 'Error'
	
	
	
	
	
	

if __name__ == "__main__":


    	app.run('0.0.0.0')
	#addr      = '3/4/9' # store address
"""	data      = sys.argv[1]   
	data_size = int(sys.argv[2])
	apci      = sys.argv[3]   # we put apci == 2 to write the data into the actuator, apci == 0 to read from it
	addr      = sys.argv[4]   # group address
            
	# sending a command
	dest_addr = knxnet.GroupAddress.from_str(addr)
	result    = send_data_to_group_addr(dest_addr, int(data), data_size, int(apci) ) 
	print(result)
"""


