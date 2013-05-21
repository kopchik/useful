#!/usr/bin/env python3
import time

class TimerError(Exception):
    pass


class Avg:
    def __init__(self, report=10, verbose=True, dimension=None):
        self.container = []
        self.report = report
        self.verbose = False
        self.dimension = dimension


    def append(self, item):
        if self.verbose:
            print("Adding item", item)

        if self.dimension:
             assert self.dimension == len(item)
        else:
            self.dimension = len(item)

        self.container.append(item)

        if self.report and len(self.container) == self.report:
            self.calc()
            self.container = []


    def calc(self):
        result = []
        data_dim = len(self.container[0])
        data_len = len(self.container)

        for i in range(data_dim):
            sum = 0
            for items in self.container:
                sum += items[i]
            #result.append(round(sum/data_len, 2))
            result.append(sum/data_len)
        if self.verbose:
            print("avg for last {0} values: {1}".format(data_len, ["{0:.2f}".format(r) for r in result]))
        return result




class StopWatch:
  def __init__(self):
    self.started = False
    self.cpu     = None
    self.time    = None

  def start(self):
    if self.started:
        raise TimerError("It's already started!")
    self.started = True
    self.cpu  = -time.clock()
    self.time = -time.time()

  def stop(self):
    if self.started is False:
        raise TimerError("It's already stopped!")
    self.started = False
    self.cpu  += time.clock()
    self.time += time.time()
    return(self.cpu_time, self.time)

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.stop()


if __name__ == '__main__':
    import numpy as np
    import gc; gc.disable()

    t = BasicTimer()
    size = 64
    repeats = 10
    for x in range(4):
        A=np.random.randn(size, size)
        B=np.random.randn(size, size)
        avg = Avg(report=repeats)
        print("for matrix {0}x{0}....".format(size))
        for y in range(repeats):
            t.start()
            np.dot(A, B)
            result = t.stop()
            #print("Matrices {0}x{0}: real: {1:.2f} cpu: {2:.2f}".format(size, result[0], result[1]))
            avg.append(result)
        size += 128
