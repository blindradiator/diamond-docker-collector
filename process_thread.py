import json
import abc
import threading
from stats_processor import MemoryStatsProcessor, NetworkStatsProcessor, CpuStatsProcessor

class StatsProcessorThread(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, collector, client, container, path, processors):
        super(StatsProcessorThread, self).__init__()
        self._collector = collector
        self._client = client
        self._container = container
        self._path = path
        self._processors = processors

        return

    def run(self):
        data = self._client.stats(self._container.id)
        metrics = json.loads(data.next())

        for processor in self._processors:
            processor.process(self._collector, self._path, metrics)


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
