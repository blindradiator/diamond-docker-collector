from abc import ABCMeta, abstractmethod


class StatsProcessor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(collector, path, metrics):
        pass

    @staticmethod
    def _get_path(*nodes):
        return '.'.join(nodes)

    @staticmethod
    def _flatten(metrics):
        def items():
            for key, value in metrics.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in StatsProcessor._flatten(value).items():
                        yield StatsProcessor._get_path(key, sub_key), sub_value
                else:
                    yield key, value

        return dict(items())


class CpuStatsProcessor(StatsProcessor):
    @staticmethod
    def process(collector, path, metrics):
        cpu = CpuStatsProcessor._flatten(metrics['cpu_stats'])

        CpuStatsProcessor._process_cpu_percent(collector, path, cpu)

        for key, value in cpu.items():
            # all cores
            if type(value) == int:
                metric_path = StatsProcessor._get_path(path, 'cpu', key)
                collector.publish_counter(metric_path, value)

            # per core
            if type(value) == list:
                for i, core_value in enumerate(value):
                    metric_path = StatsProcessor._get_path(path, 'cpu', key + str(i))
                    collector.publish_counter(metric_path, core_value)

    @staticmethod
    def _process_cpu_percent(collector, node, cpu_metrics):
        system_usage_path = collector.get_metric_path(node + '.cpu.system_cpu_usage')
        container_usage_path = collector.get_metric_path(node + '.cpu.cpu_usage.total_usage')
        if system_usage_path in collector.last_values and container_usage_path in collector.last_values:
            container_usage = cpu_metrics['cpu_usage.total_usage'] - collector.last_values[container_usage_path]
            system_usage = cpu_metrics['system_cpu_usage'] - collector.last_values[system_usage_path]

            percent_usage = container_usage * 100 / system_usage
            metric_path = StatsProcessor._get_path(node, 'cpu', 'percent')
            collector.publish_gauge(metric_path, percent_usage)


class MemoryStatsProcessor(StatsProcessor):
    @staticmethod
    def process(collector, path, metrics):
        memory = StatsProcessor._flatten(metrics['memory_stats'])
        for key, value in memory.items():
            metric_path = StatsProcessor._get_path(path, 'memory', key)
            collector.publish_gauge(metric_path, value)


class NetworkStatsProcessor(StatsProcessor):
    @staticmethod
    def process(collector, path, metrics):
        network = StatsProcessor._flatten(metrics['network'])
        for key, value in network.items():
            metric_path = StatsProcessor._get_path(path, 'network', key)
            collector.publish_counter(metric_path, value)
