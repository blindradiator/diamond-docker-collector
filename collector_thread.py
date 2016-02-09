import abc
import threading
from stats_processor import MemoryStatsProcessor, NetworkStatsProcessor, CpuStatsProcessor

class StatsCollectorThread(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, collector, client, container, path, processors):
        super(StatsCollectorThread, self).__init__()
        self._collector = collector
        self._client = client
        self._container = container
        self._path = path
        self._processors = processors

        return

    def run(self):
        metrics = self._client.stats(self._container.id, False, False)

        for processor in self._processors:
            processor.process(self._collector, self._path, metrics)


class NetworkPodStatsCollectorThread(StatsCollectorThread):
    def __init__(self, collector, client, container, path):
        super(NetworkPodStatsCollectorThread, self).__init__(collector, client, container, path,
                                                             [NetworkStatsProcessor])

class PodStatsCollectorThread(StatsCollectorThread):
    def __init__(self, collector, client, container, path):
        super(PodStatsCollectorThread, self).__init__(collector, client, container, path,
                                                      [MemoryStatsProcessor, CpuStatsProcessor])

class StandardStatsCollectorThread(StatsCollectorThread):
    def __init__(self, collector, client, container, path):
        super(StandardStatsCollectorThread, self).__init__(collector, client, container, path,
                                                           [MemoryStatsProcessor, CpuStatsProcessor,
                                                            NetworkStatsProcessor])
