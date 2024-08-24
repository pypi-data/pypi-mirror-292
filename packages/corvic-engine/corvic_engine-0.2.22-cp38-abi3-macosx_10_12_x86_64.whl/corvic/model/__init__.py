"""Data modeling objects for creating corvic pipelines."""

import corvic.model._feature_type as feature_type
from corvic.model._feature_view import (
    Column,
    FeatureView,
    FeatureViewEdgeTableMetadata,
    FeatureViewRelationshipsMetadata,
)
from corvic.model._resource import (
    Resource,
    ResourceID,
)
from corvic.model._source import Source, SourceID, SourceType
from corvic.model._space import (
    ConcatAndEmbedParameters,
    Node2VecParameters,
    RelationalSpace,
    SemanticSpace,
    Space,
)

FeatureType = feature_type.FeatureType

__all__ = [
    "Column",
    "ConcatAndEmbedParameters",
    "FeatureType",
    "FeatureView",
    "FeatureViewEdgeTableMetadata",
    "FeatureViewRelationshipsMetadata",
    "Node2VecParameters",
    "RelationalSpace",
    "Resource",
    "ResourceID",
    "SemanticSpace",
    "Source",
    "SourceID",
    "SourceType",
    "Space",
    "feature_type",
]
