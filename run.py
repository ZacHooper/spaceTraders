from SpaceTraders import traders
import threading
import time

if __name__ == "__main__":
    ships = ['cknr0wynw51684015s6wvq7q1th', 'ckns6f0vj6131615s6144vlzxl', 
             'ckns6euib5837215s6tx8ahm0u', 'ckns6eyet6022415s65sct9f5h', 
             'ckns892le95346715s6wm366ox0', 'cknsiauip88812615s6lfu0r6wm',
             'cknsfbqt3126768315s6u89oe1nw', 'ckntq87y15674821cs61t5owe9s',
             'ckntq87y15674821cs61t5owe9s', 'ckntq9bfi5782741cs62igsgjyi',
             'ckntqg1iw6417731cs6hesu4pgc']
    ships2 = ['ckntq9bfi5782741cs62igsgjyi',
             'ckntqg1iw6417731cs6hesu4pgc']
    
    threads = []
    for i in range(len(ships)):
        thread = threading.Thread(target=traders.do_trading_run, args=(ships[i],100))
        threads.append(thread)
        thread.start()
        print("Starting the thread for " + ships[i])
        time.sleep(10)

    for t in threads:
        t.join()



    # traders.do_trading_run('ckns892le95346715s6wm366ox0', 100)