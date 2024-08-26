from typing import List
from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models.partition.partition_create_request import PartitionCreateRequest
from ..models.partition.partition_drop_request import PartitionDropRequest
from ..models.partition.partition_get_stats_request import PartitionGetStatsRequest
from ..models.partition.partition_has_request import PartitionHasRequest
from ..models.partition.partition_list_request import PartitionListRequest
from ..models.partition.partition_load_request import PartitionLoadRequest
from ..models.partition.partition_release_request import PartitionReleaseRequest


class PartitionsService(BaseService):

    @cast_models
    def create(self, collection_name: str, partition_name: str):
        """Creates a new partition inside your collection.

        :param collection_name: The name of the collection to create the partition inside.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: The name of the created partition.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionCreateRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_name=partition_name,
        )

        Validator(PartitionCreateRequest).validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/partitions/create", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def drop(self, collection_name: str, partition_name: str):
        """Drops a specific partition inside your collection. Ensure that the partition is released before dropping.

        :param collection_name: The name of the collection where the specified partition is.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: The name of the partition to drop.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionDropRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_name=partition_name,
        )

        Validator(PartitionDropRequest).validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/partitions/drop", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def get_stats(self, collection_name: str, partition_name: str):
        """Returns the number of rows in the given partition inside your collection.

        :param collection_name: The name of the collection where the specified partition is.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: The name of the partition to get the number of entities of.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionGetStatsRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_name=partition_name,
        )

        Validator(PartitionGetStatsRequest).validate(request_body)

        serialized_request = (
            Serializer(
                f"{self.base_url}/partitions/get_stats", self.get_default_headers()
            )
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def has(self, collection_name: str, partition_name: str):
        """Returns whether the given partition exist inside your collection.

        :param collection_name: The name of the collection where the specified partition is.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: The name of the partition to check whether it exits.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionHasRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_name=partition_name,
        )

        Validator(PartitionHasRequest).validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/partitions/has", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def list(self, collection_name: str):
        """Returns the list of the partitions inside your collection.

        :param collection_name: The name of the collection to list the partitions inside it.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionListRequest(
            collection_name=collection_name, project_id=self.project_id
        )

        Validator(PartitionListRequest).validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/partitions/list", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def load(
        self,
        collection_name: str,
        partition_names: List[str],
    ):
        """Loads the data of the given partitions into memory.

        :param collection_name: The name of the collection where the partitions is.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: Names of the partitions to load into memory.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionLoadRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_names=partition_names,
        )

        Validator(PartitionLoadRequest).validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/partitions/load", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response

    @cast_models
    def release(
        self,
        collection_name: str,
        partition_names: List[str],
    ):
        """Releases the data of the given partitions from memory.

        :param collection_name: The name of the collection where the partitions is.
        :type collection_name: str
        :param project_id: ID of the project where the collection is.

        :param partition_name: Names of the partitions to release from memory.
        :type partition_name: str
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        """

        request_body = PartitionReleaseRequest(
            collection_name=collection_name,
            project_id=self.project_id,
            partition_names=partition_names,
        )

        Validator(PartitionReleaseRequest).validate(request_body)

        serialized_request = (
            Serializer(
                f"{self.base_url}/partitions/release", self.get_default_headers()
            )
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return response
