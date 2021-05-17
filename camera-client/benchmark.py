import argparse
import numpy as np
import time, random, string, signal, sys, json
import paho.mqtt.client as mqtt
from camera import *
from utils import *
from multiprocessing import Process, Value, Lock, Event

def rand_color():
    r = lambda: random.randint(0,255)
    return "#%02X%02X%02X" % (r(),r(),r())

# root mean squared deviation
def rmsd(arr):
    avg = np.mean(arr)
    diffs_sq = np.square(np.array(arr) - avg)
    rmsd = np.mean(diffs_sq)
    return rmsd

class GracefulKiller:
    def __init__(self):
        self.kill_now = Value("i", 0)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now.value = 1

class Benchmark(object):
    def __init__(self, name, num_cams, timeout, brokers, ports, scene):
        self.name = name
        self.num_cams = num_cams
        self.brokers = [broker for broker in brokers if broker is not None]
        self.ports = [ports[i] for i in range(len(brokers)) if brokers[i] is not None]
        self.scene = scene
        self.timeout = timeout

        self.start_flag = Event()
        self.killer = GracefulKiller()

        self.dropped_clients = 0

        self.drop_lock = Lock()

    def run(self):
        ps = [Process(target=self.move_cam, args=(i,)) for i in range(self.num_cams)]
        for p in ps:
            p.daemon = True
            p.start()

        time.sleep(0.5)

        print(f"Started! Scene is {self.scene}")
        self.start_flag.set()

        start_t = time_ms()
        self.collect()

        time.sleep(0.5)

        # print("waiting for processes to finish")
        for p in ps: p.join()

        print("done!")

    def collect(self):
        iters = 0
        start_t = time_s()
        prev_t = 0
        while True:
            now_t = time_s()
            if (now_t - prev_t) >= 1.0/10.0: # 10 Hz
                prev_t = now_t

                iters += 1
                if iters % 100 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()

            if (now_t - start_t) >= self.timeout:
                self.killer.kill_now.value = 1
                print("Timeout reached, exiting...")
                break

            if self.killer.kill_now.value:
                if input("End Benchmark [y/n]? ") == "y":
                    break
                self.killer.kill_now.value = 0

            time.sleep(0.001)

    def create_cam(self, i):
        cam = Camera(f"cam{rand_num(5)}", self.scene, rand_color())
        cam.connect(self.brokers[i%len(self.brokers)], self.ports[i%len(self.ports)])
        return cam

    def move_cam(self, i):
        try:
            cam = self.create_cam(i)
        except:
            self.drop_lock.acquire()
            self.dropped_clients=self.dropped_clients+1
            self.drop_lock.release()
            return

        self.start_flag.wait()
        iters = 0

        prev_t = 0
        while True:
            now_t = time_s()
            if (now_t - prev_t) >= 1.0/10.0: # 10 Hz
                prev_t = now_t
                iters += 1

                cam.move()

            if self.killer.kill_now.value:
                break

            time.sleep(0.001)

        cam.disconnect()

    def get_dropped_clients(self):
        return self.dropped_clients

def main(num_cams, timeout, broker, port, broker2, port2, name):
    print()
    print(f"----- Running benchmark with {num_cams} clients -----")

    test = Benchmark(f"{name}_c{num_cams}", num_cams, timeout*60, (broker, broker2), (port, port2), "benchmark_"+rand_str(5))
    test.run()

    dropped_clients = test.get_dropped_clients()

    print("----- Summary -----")
    if not broker2:
        print(f"{num_cams} Clients connecting to {broker}:{port} with {timeout} sec timeout:")
    else:
        print(f"{num_cams} Clients connecting to {broker}:{port} and {broker2}:{port2} with {timeout} sec timeout:")

    print(f"  {dropped_clients} clients dropped ")
    print("------------------------------------------------------")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("ARENA MQTT broker benchmarking"))

    parser.add_argument("-c", "--num_cams", type=int, help="Number of clients to spawn",
                        default=1)
    parser.add_argument("-b", "--broker", type=str, help="Broker to connect to",
                        default="arena0.andrew.cmu.edu")
    parser.add_argument("-p", "--port", type=int, help="Port to connect to",
                        default=18883)
    parser.add_argument("-b2", "--broker2", type=str, help="Second broker to connect to. For broker-broker",
                        default=None)
    parser.add_argument("-p2", "--port2", type=int, help="Second port to connect to. For broker-broker",
                        default=18884)
    parser.add_argument("-n", "--name", type=str, help="Optional name for saved plot",
                        default="benchmark")
    parser.add_argument("-t", "--timeout", type=float, help="Amount of mins to wait before ending data collection",
                        default=2.0) # default is 2 mins

    args = parser.parse_args()

    main(**vars(args))
