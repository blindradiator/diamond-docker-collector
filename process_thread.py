import json
import abc
import threading
from stats_processor import *

class StatsProcessorThread(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, collector, client, container, path, processors):
        super(StatsProcessorThread, self).__init__()
        self.collector = collector
        self.client = client
        self.container = container
        self.path = path
        self.processors = processors

        return

    def run(self):
        data = self.client.stats(self.container.id)
        metrics = json.loads(data.next())

        for processor in self.processors:
            processor.process(self.collector, self.path, metrics)


class NetworkPodStatsProcessorThread(StatsProcessorThread):
    def __init__(self, collector, client, container, path):
        super(NetworkPodStatsProcessorThread, self).__init__(collector, client, container, path,
                                                             [NetworkStatsProcessor])

class PodStatsProcessorThread(StatsProcessorThread):
    def __init__(self, collector, client, container, path):
        super(PodStatsProcessorThread, self).__init__(collector, client, container, path,
                                                      [MemoryStatsProcessor, CpuStatsProcessor])

class StandardStatsProcessorThread(StatsProcessorThread):
    def __init__(self, collector, client, container, path):
        super(StandardStatsProcessorThread, self).__init__(collector, client, container, path,
                                                           [MemoryStatsProcessor, CpuStatsProcessor,
                                                            NetworkStatsProcessor])
