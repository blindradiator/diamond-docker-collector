#!/usr/bin/env python
import re
import docker
import diamond.collector
from process_thread import StandardStatsProcessorThread, PodStatsProcessorThread, NetworkPodStatsProcessorThread
from container import ContainerListProvider


class KubernetesDockerCollector(diamond.collector.Collector):
    DOCKER_IMAGE_VERSION_PATTERN = re.compile('([^:/]+)$')
    DEFAULT_NAMESPACE = 'none'
    DEFAULT_POD = 'none'
    MAX_PATH_ID_LENGTH = 8

    def get_default_config_help(self):
        config_help = super(KubernetesDockerCollector, self).get_default_config_help()
        config_help.update({
            'socket': 'Docker socket path'
        })
        return config_help

    def get_default_config(self):
        config = super(KubernetesDockerCollector, self).get_default_config()
        config.update({
            'path': '.',
            'socket': 'unix://var/run/docker.sock'
        })
        return config

    def process_config(self):
        super(KubernetesDockerCollector, self).process_config()
        self.socket = self.config['socket']

    def collect(self):
        client = docker.Client(base_url=self.socket, version='auto')
        containers = ContainerListProvider.get(client)

        threads = []
        for id, container in containers.iteritems():
            container_threads = self._process_container(client, container)
            threads.extend(container_threads)

        map(lambda thread: thread.join(), threads)

    def _process_container(self, client, container):
        node = self._generate_path(container)

        threads = []
        if container.network:
            threads.append(PodStatsProcessorThread(self, client, container, node))
            threads.append(NetworkPodStatsProcessorThread(self, client, container.network, node))
        else:
            threads.append(StandardStatsProcessorThread(self, client, container, node))
        map(lambda thread: thread.start(), threads)

        return threads

    def _generate_path(self, container):
        def join(*nodes):
            def encode(string):
                return string.replace('.', '_').replace('/', '_')

            return '.'.join(map(encode, nodes))

        namespace = container.namespace if container.namespace else self.DEFAULT_NAMESPACE
        name = container.name if container.name else container.docker_name
        version = self.DOCKER_IMAGE_VERSION_PATTERN.search(container.image).group()
        pod = container.pod if container.pod else self.DEFAULT_POD
        id = container.id[0:self.MAX_PATH_ID_LENGTH]

        return join(namespace, name, version, pod, id)
