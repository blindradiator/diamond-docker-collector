import re


class Container:
    def __init__(self, id, docker_name, image, name=None, pod=None, namespace=None, hash=None, uid=None, network=None):
        self.id = id
        self.docker_name = docker_name
        self.image = image
        self.name = name
        self.pod = pod
        self.namespace = namespace
        self.hash = hash
        self.uid = uid
        self.network = network


class ContainerListProvider:
    NETWORK_CONTAINER_NAME = 'POD'
    DOCKER_NAME_PATTERN = re.compile(
        'k8s_' +
        '(?P<name>[^_\.]+)\.(?P<hash>[^_\.]+)_' +
        '(?P<pod>[^_]+)_' +
        '(?P<namespace>[^_]+)_' +
        '(?P<uid>[^_]+).*'
    )

    @staticmethod
    def get(docker_client):
        containers = {}
        network_containers = {}

        for container_data in docker_client.containers():
            container = ContainerListProvider._get_container(container_data)

            if ContainerListProvider._is_network_container(container):
                network_containers[container.uid] = container
            else:
                containers[container.id] = container

        ContainerListProvider._assign_network_containers(containers, network_containers)

        return containers

    @staticmethod
    def _get_container(container_data):
        id = container_data['Id']
        docker_name = container_data['Names'][0][1:]
        image = container_data['Image']
        match = ContainerListProvider.DOCKER_NAME_PATTERN.match(docker_name)
        attributes = match.groupdict() if match else {}

        return Container(id, docker_name, image, **attributes)

    @staticmethod
    def _is_network_container(container):
        return container.name == ContainerListProvider.NETWORK_CONTAINER_NAME

    @staticmethod
    def _assign_network_containers(containers, network_containers):
        for id, container in containers.iteritems():
            if container.uid in network_containers:
                container.network = network_containers[container.uid]
