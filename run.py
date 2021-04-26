from SpaceTraders import traders
import threading
import time

if __name__ == "__main__":
    ships = ['cknxw0jyz10305031bs6rdlv226q']
    
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