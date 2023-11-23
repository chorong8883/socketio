import iosock
import signal
import threading
import time
import math

server = iosock.Server()

starter = b'%w$d#'
closer = b'&sa@f#d$'

def recv_threading():
    count = {}
    recv_data = {}
    time_recv_data = {}
    while True:
        recv_temp_data = server.recv()
        if not recv_temp_data:
            break
        
        fileno = recv_temp_data['fileno']
        data = recv_temp_data['data']
        if not fileno in count:
            count[fileno] = 0
    
        if fileno in recv_data:
            if recv_data[fileno] == b'':
                time_recv_data[fileno] = time.time()
            recv_data[fileno] += data
        else:
            recv_data[fileno] = data
            time_recv_data[fileno] = time.time()
        
        start_index = -1
        end_index = -1
        
        is_start = True
        is_len = True
        is_closer = True
        
        while is_start and is_len and is_closer:
            try:
                bit8_length = 1
                start_index = len(starter)
                end_index = len(starter)+bit8_length
                is_start = end_index <= len(recv_data[fileno]) and recv_data[fileno][:len(starter)] == starter
                length_of_length_bytes = recv_data[fileno][start_index:end_index]
                length_of_length = int.from_bytes(length_of_length_bytes, byteorder='little')
                
                start_index = end_index
                end_index = end_index + length_of_length
                is_len = end_index <= len(recv_data[fileno])
                
                length_bytes = recv_data[fileno][start_index:end_index]
                source_length = int.from_bytes(length_bytes, byteorder='little')
                
                start_index = end_index
                end_index = end_index+source_length
                is_closer = end_index+len(closer) <= len(recv_data[fileno]) and recv_data[fileno][end_index:end_index+len(closer)] == closer
            except IndexError:
                break
            
            if is_start and is_len and is_closer:
                recv_bytes:bytes = recv_data[fileno][start_index:end_index]
                recv_data[fileno] = recv_data[fileno][end_index+len(closer):]
                server.send(fileno, recv_bytes)
                end = time.time()
                
                recv_bytes_replaced = recv_bytes.replace(b'abcdefghijklmnop qrstuvwxyz', b'')
                
                text_print = f'[{fileno:2}][{count[fileno]:5}] recv {len(recv_bytes):7} bytes. over:{len(recv_data[fileno]):8} time elapsed: {math.floor((end - time_recv_data[fileno])*100000)/100000:.5f} replace:{recv_bytes_replaced}'
                print(text_print)
            else:
                count[fileno] += 1
                
def signal_handler(num_recv_signal, frame):
    print(f"\nGet Signal: {signal.Signals(num_recv_signal).name}")
    server.close()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server.start('218.55.118.203', 59012, 5)
    print("Server Start.")
    
    recv_thread = threading.Thread(target=recv_threading)
    recv_thread.start()
    recv_thread.join()
    
