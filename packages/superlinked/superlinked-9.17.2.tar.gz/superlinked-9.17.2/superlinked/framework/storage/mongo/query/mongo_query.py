# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from beartype.typing import Any, Iterable, Sequence, cast
from typing_extensions import Self

from superlinked.framework.common.interface.comparison_operand import (
    ComparisonOperand,
    ComparisonOperation,
)
from superlinked.framework.common.interface.comparison_operation_type import (
    ITERABLE_COMPARISON_OPERATION_TYPES,
    ComparisonOperationType,
)
from superlinked.framework.common.storage.field import Field
from superlinked.framework.common.storage.field_data import FieldData
from superlinked.framework.common.storage.query.vdb_filter import VDBFilter
from superlinked.framework.storage.mongo.mongo_field_encoder import (
    MongoEncodedTypes,
    MongoFieldEncoder,
)
from superlinked.framework.storage.mongo.query.mongo_vdb_knn_search_params import (
    MongoVDBKNNSearchParams,
)

# For more info on this check:
# https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
# paragraph Fields, 'numCandidates' definition.
VECTOR_SCORE_ALIAS = "__vector_score"
SUPPORTED_FILTER_DICT = {
    ComparisonOperationType.EQUAL: "$eq",
    ComparisonOperationType.NOT_EQUAL: "$ne",
    ComparisonOperationType.GREATER_THAN: "$gt",
    ComparisonOperationType.GREATER_EQUAL: "$gte",
    ComparisonOperationType.LESS_THAN: "$lt",
    ComparisonOperationType.LESS_EQUAL: "$lte",
    ComparisonOperationType.IN: "$in",
    ComparisonOperationType.NOT_IN: "$nin",
}


class MongoQuery:
    def __init__(self, encoder: MongoFieldEncoder) -> None:
        self._encoder = encoder
        self.__query = list[dict[str, dict[str, Any]]]()

    @property
    def query(self) -> Sequence[dict[str, dict[str, Any]]]:
        return self.__query

    # TODO FAI-1931: use pydantic for `query_parts`!
    def __add_query_part(self, query_part: dict[str, dict[str, Any]]) -> Self:
        if query_part:
            self.__query.append(query_part)
        return self

    def add_vector_search_dict(
        self,
        search_params: MongoVDBKNNSearchParams,
    ) -> Self:
        filters: dict[str, Any] = self._get_filters_dict(search_params.filters)
        return self.__add_query_part(
            {
                "$vectorSearch": {
                    "index": search_params.index_name,
                    "path": search_params.vector_field.name,
                    "queryVector": self._encoder.encode_field(
                        search_params.vector_field
                    ),
                    "numCandidates": search_params.num_candidates,
                    "limit": search_params.limit,
                    "filter": filters,
                }
            }
        )

    def add_radius_filter_dict(self, radius: float | None) -> Self:
        if radius is None:
            return self
        return self.__add_query_part(
            {"$match": {VECTOR_SCORE_ALIAS: {"$gt": 1 - radius}}}
        )

    def add_projection_dict(
        self,
        returned_fields: Sequence[Field],
    ) -> Self:
        field_set_dict: dict[str, Any] = {
            returned_field.name: 1 for returned_field in returned_fields
        }
        field_set_dict.update(
            {"_id": 1, VECTOR_SCORE_ALIAS: {"$meta": "vectorSearchScore"}}
        )
        return self.__add_query_part({"$project": field_set_dict})

    def _get_filters_dict(
        self, filters: Sequence[ComparisonOperation[Field]] | None
    ) -> dict[str, Any]:
        vdb_filters = self._compile_filters(filters or [])
        if len(vdb_filters) > 1:
            return {
                "$and": [
                    MongoQuery._vdb_filters_to_dict(filter_) for filter_ in vdb_filters
                ]
            }
        if vdb_filters:
            return MongoQuery._vdb_filters_to_dict(vdb_filters[0])
        return {}

    def _compile_filters(
        self, filters: Sequence[ComparisonOperation[Field]]
    ) -> Sequence[VDBFilter]:
        return [self._compile_filter(filter_) for filter_ in filters]

    def _compile_filter(self, filter_: ComparisonOperation[Field]) -> VDBFilter:
        field_value = (
            self._encode_iterable_field(filter_._operand, filter_._other)
            if filter_._op in ITERABLE_COMPARISON_OPERATION_TYPES
            else self._encode_field(filter_._operand, filter_._other)
        )
        return VDBFilter(cast(Field, filter_._operand), field_value, filter_._op)

    def _encode_iterable_field(
        self, operand: ComparisonOperand, other: Any
    ) -> list[MongoEncodedTypes]:
        if not isinstance(other, Iterable):
            raise ValueError("Operand must be iterable.")
        return [self._encode_field(operand, other) for other in other]

    def _encode_field(
        self, operand: ComparisonOperand, other: object
    ) -> MongoEncodedTypes:
        return self._encoder.encode_field(
            FieldData.from_field(cast(Field, operand), other)
        )

    @staticmethod
    def _vdb_filters_to_dict(
        vdb_filter: VDBFilter,
    ) -> dict[str, dict[str, Any]]:
        if vdb_filter.op not in SUPPORTED_FILTER_DICT:
            raise NotImplementedError(
                f"Unsupported filter operation type: {vdb_filter.op.value}"
            )
        return {
            vdb_filter.field.name: {
                SUPPORTED_FILTER_DICT[vdb_filter.op]: vdb_filter.field_value
            }
        }
