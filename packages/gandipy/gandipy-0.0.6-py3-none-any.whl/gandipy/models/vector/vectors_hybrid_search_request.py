from typing import List, Any
from ..utils.json_map import JsonMap
from ..base import BaseModel


@JsonMap({})
class Params(BaseModel):
    """Params

    :param radius: radius, defaults to None
    :type radius: int, optional
    :param range_filter: range_filter, defaults to None
    :type range_filter: int, optional
    """

    def __init__(self, radius: int = None, range_filter: int = None):
        if radius is not None:
            self.radius = radius
        if range_filter is not None:
            self.range_filter = range_filter


@JsonMap(
    {
        "anns_field": "annsField",
        "grouping_field": "groupingField",
        "metric_type": "metricType",
        "ignore_growing": "ignoreGrowing",
    }
)
class Search(BaseModel):
    """SearchItem

    :param data: data, defaults to None
    :type data: List[Any], optional
    :param anns_field: anns_field, defaults to None
    :type anns_field: str, optional
    :param filter: filter, defaults to None
    :type filter: str, optional
    :param grouping_field: grouping_field, defaults to None
    :type grouping_field: str, optional
    :param metric_type: metric_type, defaults to None
    :type metric_type: str, optional
    :param limit: limit, defaults to None
    :type limit: int, optional
    :param offset: offset, defaults to None
    :type offset: int, optional
    :param ignore_growing: ignore_growing, defaults to None
    :type ignore_growing: bool, optional
    :param params: params, defaults to None
    :type params: Params, optional
    """

    def __init__(
        self,
        data: List[Any] = None,
        anns_field: str = None,
        filter: str = None,
        grouping_field: str = None,
        metric_type: str = None,
        limit: int = None,
        offset: int = None,
        ignore_growing: bool = None,
        params: Params = None,
    ):
        if data is not None:
            self.data = data
        if anns_field is not None:
            self.anns_field = anns_field
        if filter is not None:
            self.filter = filter
        if grouping_field is not None:
            self.grouping_field = grouping_field
        if metric_type is not None:
            self.metric_type = metric_type
        if limit is not None:
            self.limit = limit
        if offset is not None:
            self.offset = offset
        if ignore_growing is not None:
            self.ignore_growing = ignore_growing
        if params is not None:
            self.params = self._define_object(params, Params)


@JsonMap({})
class Ranker(BaseModel):
    """Ranker

    :param strategy: strategy, defaults to None
    :type strategy: str, optional
    :param k: k, defaults to None
    :type k: str, optional
    """

    def __init__(
        self, strategy: str = None, k: str = None, weights: List[float] = None
    ):
        if strategy is not None:
            self.strategy = strategy
        self.params = dict()
        if k is not None:
            self.params["k"] = k
        if weights is not None:
            self.params["weights"] = weights


@JsonMap(
    {
        "collection_name": "collectionName",
        "partition_names": "partitionNames",
        "output_fields": "outputFields",
    }
)
class VectorsHybridSearchRequest(BaseModel):
    """VectorsHybridSearchRequest

    , defaults to None

    :param collection_name: collection_name
    :type collection_name: str
    :param partition_names: partition_names, defaults to None
    :type partition_names: List[str], optional
    :param search: search, defaults to None
    :type search: List[Search], optional
    :param rerank: rerank, defaults to None
    :type rerank: str, optional
    :param limit: limit, defaults to None
    :type limit: int, optional
    :param output_fields: output_fields, defaults to None
    :type output_fields: List[str], optional
    """

    def __init__(
        self,
        collection_name: str,
        project_id: str = None,
        partition_names: List[str] = None,
        search: List[Search] = None,
        rerank: Ranker = None,
        limit: int = None,
        output_fields: List[str] = None,
    ):
        self.collection_name = collection_name
        self.project_id = project_id
        if partition_names is not None:
            self.partition_names = partition_names
        if search is not None:
            self.search = self._define_list(search, Search)
        if rerank is not None:
            self.rerank = self._define_object(rerank, Ranker)
        if limit is not None:
            self.limit = limit
        if output_fields is not None:
            self.output_fields = output_fields
