"""Feature views."""

from __future__ import annotations

import dataclasses
import functools
import uuid
from collections.abc import Iterable
from typing import Any, Final, TypeAlias

from more_itertools import flatten

from corvic import op_graph, orm, system
from corvic.model._defaults import get_default_client
from corvic.model._source import Source, SourceID
from corvic.model._wrapped_proto import WrappedProto
from corvic.result import BadArgumentError, NotFoundError, Ok
from corvic.table import (
    DataclassAsTypedMetadataMixin,
    RowFilter,
    Schema,
    Table,
    feature_type,
    row_filter,
)
from corvic_generated.model.v1alpha import models_pb2

FeatureViewID: TypeAlias = orm.FeatureViewID
FeatureViewSourceID: TypeAlias = orm.FeatureViewSourceID


class Column:
    """A logical representation of a column to use in filter predicates.

    Columns are identified by name.
    """

    _column_name: Final[str]

    def __init__(self, column_name: str):
        """Creates a new instance of Column.

        Args:
            column_name: Name of the column
        """
        self._column_name = column_name

    def eq(self, value: Any) -> RowFilter:
        """Return rows where column is equal to a value."""
        return row_filter.eq(column_name=self._column_name, literal=value)

    def ne(self, value: Any) -> RowFilter:
        """Return rows where column is not equal to a value."""
        return row_filter.ne(column_name=self._column_name, literal=value)

    def gt(self, value: Any) -> RowFilter:
        """Return rows where column is greater than a value."""
        return row_filter.gt(column_name=self._column_name, literal=value)

    def lt(self, value: Any) -> RowFilter:
        """Return rows where column is less than a value."""
        return row_filter.lt(column_name=self._column_name, literal=value)

    def ge(self, value: Any) -> RowFilter:
        """Return rows where column is greater than or equal to a value."""
        return row_filter.ge(column_name=self._column_name, literal=value)

    def le(self, value: Any) -> RowFilter:
        """Return rows where column is less than or equal to a value."""
        return row_filter.le(column_name=self._column_name, literal=value)

    def in_(self, value: list[Any]) -> RowFilter:
        """Return rows where column matches any in a list of values."""
        return row_filter.in_(column_name=self._column_name, literals=value)


@dataclasses.dataclass(frozen=True)
class FkeyRelationship:
    """A foreign key relationship between sources."""

    source_with_fkey: SourceID
    fkey_column_name: str
    referenced_source: SourceID
    pkey_column_name: str


@dataclasses.dataclass(frozen=True)
class Relationship:
    """A connection between two sources within a FeatureView."""

    from_feature_view_source: FeatureViewSource
    to_feature_view_source: FeatureViewSource

    fkey_relationship: FkeyRelationship

    @property
    def from_source(self) -> Source:
        return self.from_feature_view_source.source

    @property
    def to_source(self) -> Source:
        return self.to_feature_view_source.source

    @property
    def from_column_name(self) -> str:
        if self.from_source.id == self.fkey_relationship.source_with_fkey:
            return self.fkey_relationship.fkey_column_name
        return self.fkey_relationship.pkey_column_name

    @property
    def to_column_name(self) -> str:
        if self.to_source.id == self.fkey_relationship.source_with_fkey:
            return self.fkey_relationship.fkey_column_name
        return self.fkey_relationship.pkey_column_name

    @functools.cached_property
    def new_column_name(self) -> str:
        return f"join-{uuid.uuid4()}"

    def joined_table(self) -> Table:
        start_table = self.from_feature_view_source.table.rename_columns(
            {self.from_column_name: self.new_column_name}
        )
        end_table = self.to_feature_view_source.table.rename_columns(
            {self.to_column_name: self.new_column_name}
        )

        return start_table.join(
            end_table,
            left_on=self.new_column_name,
            right_on=self.new_column_name,
            how="inner",
        )

    def edge_list(self) -> Iterable[tuple[Any, Any]]:
        start_pk = self.from_feature_view_source.table.schema.get_primary_key()
        end_pk = self.to_feature_view_source.table.schema.get_primary_key()

        if not start_pk or not end_pk:
            raise BadArgumentError(
                "both sources must have a primary key to render edge list"
            )

        if self.from_column_name == start_pk.name:
            result_columns = (self.new_column_name, end_pk.name)
        else:
            result_columns = (start_pk.name, self.new_column_name)

        result = self.joined_table().select(result_columns)

        for batch in result.to_polars().unwrap_or_raise():
            for row in batch.rows(named=True):
                yield (row[result_columns[0]], row[result_columns[1]])


@dataclasses.dataclass(frozen=True)
class FeatureViewSource(
    WrappedProto[FeatureViewSourceID, models_pb2.FeatureViewSource]
):
    """A table from a source with some extra operations defined by a feature view."""

    source: Source

    def _sub_orm_objects(self, orm_object: orm.FeatureViewSource) -> Iterable[orm.Base]:
        _ = (orm_object,)
        return []

    @functools.cached_property
    def table(self):
        return Table.from_ops(
            self.client, op_graph.op.from_proto(self.proto_self.table_op_graph)
        )


@dataclasses.dataclass(kw_only=True)
class FeatureViewEdgeTableMetadata(DataclassAsTypedMetadataMixin):
    """Metadata attached to edge tables; notes important columns and provenance."""

    @classmethod
    def metadata_key(cls):
        return "space-edge_table-metadata"

    start_source_name: str
    end_source_name: str
    start_source_column_name: str
    end_source_column_name: str


@dataclasses.dataclass(kw_only=True)
class FeatureViewRelationshipsMetadata(DataclassAsTypedMetadataMixin):
    """Metadata attached to relationship path for feature view edge tables."""

    @classmethod
    def metadata_key(cls):
        return "space-relationships-metadata"

    relationship_path: list[str]


@dataclasses.dataclass(kw_only=True)
class FeatureViewSourceColumnRenames(DataclassAsTypedMetadataMixin):
    """Metadata attached to feature space source tables to remember renamed columns."""

    @classmethod
    def metadata_key(cls):
        return "space_source-column_renames-metadata"

    column_renames: dict[str, str]


@dataclasses.dataclass(frozen=True)
class FeatureView(WrappedProto[FeatureViewID, models_pb2.FeatureView]):
    """FeatureViews describe how Sources should be modeled to create a feature space.

    Example:
    >>> FeatureView.create()
    >>>    .with_source(
    >>>        customer_source,
    >>>        row_filter=Column("customer_name").eq("Denis").or_(Column("id").lt(3)),
    >>>        drop_disconnected=True,
    >>>    )
    >>>    .with_source(
    >>>        order_source,
    >>>        include_columns=["id", "ordered_item"],
    >>>    )
    >>>    .wth_relationship(customer_source, order_source, directional=False)
    """

    source_id_to_feature_view_source: dict[SourceID, FeatureViewSource]
    output_sources: set[SourceID]
    relationships: list[Relationship]

    def _sub_orm_objects(self, orm_object: orm.FeatureView) -> Iterable[orm.Base]:
        _ = (orm_object,)
        return []

    def _resolve_source(
        self, source: Source | SourceID
    ) -> Ok[Source] | NotFoundError | BadArgumentError:
        match source:
            case Source():
                return Ok(source)
            case SourceID():
                return Source.from_id(source, self.client)

    def _get_feature_view_source(
        self, source: Source | SourceID | str
    ) -> Ok[FeatureViewSource] | NotFoundError | BadArgumentError:
        # accessor that implements the common logic for handling the different ways
        # users might talk about sources
        if isinstance(source, str):
            source_name = source
            val = next(
                (
                    val
                    for val in self.source_id_to_feature_view_source.values()
                    if val.source.name == source
                ),
                None,
            )
            if not val:
                return BadArgumentError(
                    "feature view does not reference source with given name",
                    given_name=source_name,
                )
            return Ok(val)

        match self._resolve_source(source):
            case NotFoundError() | BadArgumentError() as err:
                return err
            case Ok(source):
                pass

        val = self.source_id_to_feature_view_source.get(source.id)
        if not val:
            return BadArgumentError(
                "feature view does not reference source with given id",
                given_id=str(source.id),
            )
        return Ok(val)

    @functools.cached_property
    def sources(self) -> list[Source]:
        return [
            feature_view_source.source
            for feature_view_source in self.source_id_to_feature_view_source.values()
        ]

    def _calculate_paths_to_outputs(self, output: SourceID, rels: list[Relationship]):
        paths: list[list[Relationship]] = []
        for rel in rels:
            if rel.from_source.id == output:
                if rel.to_source.id in self.output_sources:
                    paths.append([rel])
                else:
                    child_paths = self._calculate_paths_to_outputs(
                        rel.to_source.id,
                        [  # we only want to use a fkey relationship once per path
                            next_rel
                            for next_rel in rels
                            if next_rel.fkey_relationship != rel.fkey_relationship
                        ],
                    )
                    paths.extend([rel, *child_path] for child_path in child_paths)
        return paths

    @staticmethod
    def _find_start_end_columns(rels: list[Relationship]) -> tuple[str, str]:
        if not rels:
            raise BadArgumentError("must provide at least one relationship")
        if rels[0].fkey_relationship.source_with_fkey == rels[0].from_source.id:
            start_field = rels[
                0
            ].from_feature_view_source.table.schema.get_primary_key()
            if not start_field:
                raise BadArgumentError(
                    "configuration requires column to have a primary key",
                    source_name=rels[0].from_feature_view_source.source.name,
                )
            start_col = start_field.name
        else:
            start_col = rels[0].new_column_name

        if rels[-1].fkey_relationship.source_with_fkey == rels[-1].to_source.id:
            end_field = rels[-1].to_feature_view_source.table.schema.get_primary_key()
            if not end_field:
                raise BadArgumentError(
                    "configuration requires source to have primary key",
                    source_name=rels[-1].to_feature_view_source.source.name,
                )
            end_col = end_field.name
        else:
            end_col = rels[-1].new_column_name

        return start_col, end_col

    def output_edge_tables(self) -> list[Table]:
        paths_between_outputs = list(
            flatten(
                self._calculate_paths_to_outputs(output, self.relationships)
                for output in self.output_sources
            )
        )

        def update_renames(new_rel: Relationship, column_renames: dict[str, str]):
            column_renames[new_rel.from_column_name] = new_rel.new_column_name
            column_renames[new_rel.to_column_name] = new_rel.new_column_name

        def find_latest_name(name: str, column_renames: dict[str, str]):
            while name in column_renames:
                new_name = column_renames[name]
                if new_name == name:
                    break
                name = new_name
            return name

        edge_tables = list[Table]()
        for path in paths_between_outputs:
            start_col, end_col = self._find_start_end_columns(path)
            path_itr = iter(path)
            rel = next(path_itr)
            table = rel.joined_table()
            column_renames = dict[str, str]()

            new_start_col = f"start-{uuid.uuid4()}"
            column_renames[start_col] = new_start_col
            table = table.rename_columns({start_col: new_start_col})
            start_col = new_start_col

            update_renames(rel, column_renames)
            for rel in path_itr:
                latest_from_name = find_latest_name(
                    rel.from_column_name, column_renames
                )
                table = table.rename_columns(
                    {latest_from_name: rel.new_column_name}
                ).join(
                    rel.to_feature_view_source.table.rename_columns(
                        {rel.to_column_name: rel.new_column_name}
                    ),
                    left_on=rel.new_column_name,
                    right_on=rel.new_column_name,
                    suffix=f"_{rel.to_feature_view_source.source.name}",
                )
                update_renames(rel, column_renames)

            # update end column name
            new_end_col = f"end-{uuid.uuid4()}"
            column_renames[end_col] = new_end_col
            table = table.rename_columns({end_col: new_end_col})
            end_col = new_end_col

            relationship_path = [
                path[0].from_source.name,
                *(p.to_source.name for p in path),
            ]

            table = table.update_typed_metadata(
                FeatureViewEdgeTableMetadata(
                    start_source_name=path[0].from_feature_view_source.source.name,
                    end_source_name=path[-1].to_feature_view_source.source.name,
                    start_source_column_name=start_col,
                    end_source_column_name=end_col,
                ),
                FeatureViewRelationshipsMetadata(
                    relationship_path=list(relationship_path)
                ),
            ).select([start_col, end_col])
            edge_tables.append(table)
        return edge_tables

    @classmethod
    def create(cls, client: system.Client | None = None) -> FeatureView:
        """Create a FeatureView."""
        proto_feature_view = models_pb2.FeatureView()
        client = client or get_default_client()
        return FeatureView(
            client,
            proto_feature_view,
            FeatureViewID(),
            source_id_to_feature_view_source={},
            relationships=[],
            output_sources=set(),
        )

    @property
    def feature_view_sources(self) -> list[FeatureViewSource]:
        return list(self.source_id_to_feature_view_source.values())

    @staticmethod
    def _unique_name_for_key_column(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4()}"

    def _sanitize_keys(self, new_schema: Schema):
        renames = dict[str, str]()
        for field in new_schema:
            match field.ftype:
                case feature_type.PrimaryKey():
                    renames[field.name] = self._unique_name_for_key_column(
                        f"{field.name}_pk"
                    )
                case feature_type.ForeignKey():
                    renames[field.name] = self._unique_name_for_key_column(
                        f"{field.name}_fk"
                    )
                case _:
                    pass
        return renames

    def with_source(
        self,
        source: SourceID | Source,
        *,
        row_filter: RowFilter | None = None,
        drop_disconnected: bool = False,
        include_columns: list[str] | None = None,
        output: bool = False,
    ) -> FeatureView:
        """Add a source to to this FeatureView.

        Args:
            source: The source to be added
            row_filter: Row level filters to be applied on source
            drop_disconnected: Filter orphan nodes in source
            include_columns: Column level filters to be applied on source
            output: Set to True if this should should be an entity in the ourput

        Example:
        >>> with_source(
        >>>     customer_source_id,
        >>>     row_filter=Column("customer_name").eq("Denis"),
        >>>     drop_disconnected=True,
        >>>     include_columns=["id", "customer_name"],
        >>> )
        """
        source = self._resolve_source(source).unwrap_or_raise()
        new_table = source.table
        if row_filter:
            new_table = new_table.filter_rows(row_filter)
        if include_columns:
            new_table = new_table.select(include_columns)

        renames = self._sanitize_keys(new_table.schema)

        if renames:
            new_table = new_table.rename_columns(renames).update_typed_metadata(
                FeatureViewSourceColumnRenames(column_renames=renames)
            )

        proto_feature_view_source = models_pb2.FeatureViewSource(
            table_op_graph=new_table.op_graph.to_proto(),
            drop_disconnected=drop_disconnected,
        )

        source_id_to_feature_view_source = self.source_id_to_feature_view_source.copy()
        source_id_to_feature_view_source.update(
            {
                source.id: FeatureViewSource(
                    self.client,
                    proto_feature_view_source,
                    FeatureViewSourceID(),
                    source,
                )
            }
        )

        output_sources = self.output_sources
        if output:
            primary_key = source.table.schema.get_primary_key()
            if not primary_key:
                raise BadArgumentError(
                    "source must have a primary key to part of the output"
                )
            output_sources = output_sources.union({source.id})

        return dataclasses.replace(
            self,
            source_id_to_feature_view_source=source_id_to_feature_view_source,
            output_sources=output_sources,
        )

    @staticmethod
    def _verify_fk_reference(
        fv_source: FeatureViewSource,
        foreign_key: str | None,
        expected_refd_source_id: SourceID,
    ) -> Ok[str | None] | BadArgumentError:
        if not foreign_key:
            return Ok(None)
        renames = (
            fv_source.table.get_typed_metadata(
                FeatureViewSourceColumnRenames
            ).column_renames
            if fv_source.table.has_typed_metadata(FeatureViewSourceColumnRenames)
            else dict[str, str]()
        )
        renamed_foreign_key = renames.get(foreign_key, foreign_key)
        match fv_source.table.schema[renamed_foreign_key].ftype:
            case feature_type.ForeignKey(referenced_source_id):
                if referenced_source_id != expected_refd_source_id:
                    return BadArgumentError(
                        "foreign_key does not reference expected source_id",
                        source_with_forien_key=str(fv_source.source.id),
                        referenced_source_id=str(expected_refd_source_id),
                    )
            case _:
                return BadArgumentError(
                    "the provided from_foreign_key is not a ForeignKey feature"
                )
        return Ok(renamed_foreign_key)

    def _check_or_infer_foreign_keys(
        self,
        from_fv_source: FeatureViewSource,
        to_fv_source: FeatureViewSource,
        from_foreign_key: str | None,
        to_foreign_key: str | None,
    ) -> Ok[tuple[str | None, str | None]] | BadArgumentError:
        match self._verify_fk_reference(
            from_fv_source, from_foreign_key, to_fv_source.source.id
        ):
            case BadArgumentError() as err:
                return err
            case Ok(new_fk):
                from_foreign_key = new_fk

        match self._verify_fk_reference(
            to_fv_source, to_foreign_key, from_fv_source.source.id
        ):
            case BadArgumentError() as err:
                return err
            case Ok(new_fk):
                to_foreign_key = new_fk

        if not from_foreign_key and not to_foreign_key:
            from_foreign_keys = [
                field.name
                for field in from_fv_source.table.schema.get_foreign_keys(
                    to_fv_source.source.id
                )
            ]
            to_foreign_keys = [
                field.name
                for field in to_fv_source.table.schema.get_foreign_keys(
                    from_fv_source.source.id
                )
            ]

            if (
                (from_foreign_keys and to_foreign_keys)
                or len(from_foreign_keys) > 1
                or len(to_foreign_keys) > 1
            ):
                raise BadArgumentError(
                    "relationship is ambiguous:"
                    + "provide from_foreign_key or to_foreign_key to disambiguate",
                    from_foreign_keys=from_foreign_keys,
                    to_foreign_keys=to_foreign_keys,
                )
            if from_foreign_keys:
                from_foreign_key = from_foreign_keys[0]
            if to_foreign_keys:
                to_foreign_key = to_foreign_keys[0]

        return Ok((from_foreign_key, to_foreign_key))

    def _make_foreign_key_relationship(
        self,
        source_with_fkey: SourceID,
        fkey_column_name: str,
        refd_fv_source: FeatureViewSource,
    ):
        pk = refd_fv_source.table.schema.get_primary_key()
        if not pk:
            return BadArgumentError(
                "source has no primary key, "
                + "so it cannot be referenced by foreign key",
                source_id=str(refd_fv_source.source.id),
            )

        return Ok(
            FkeyRelationship(
                source_with_fkey=source_with_fkey,
                fkey_column_name=fkey_column_name,
                referenced_source=refd_fv_source.source.id,
                pkey_column_name=pk.name,
            )
        )

    def with_all_implied_relationships(self) -> FeatureView:
        """Automatically define non-directional relationships based on foreign keys."""
        new_feature_view = self
        for feature_view_source in self.feature_view_sources:
            for field in feature_view_source.source.table.schema:
                match field.ftype:
                    case feature_type.ForeignKey(referenced_source_id):
                        referenced_source = self.source_id_to_feature_view_source.get(
                            referenced_source_id
                        )
                        if referenced_source:
                            # We don't know the intended direction, add both directions
                            new_feature_view = new_feature_view.with_relationship(
                                referenced_source.source,
                                feature_view_source.source,
                                to_foreign_key=field.name,
                                directional=False,
                            )
                    case _:
                        pass
        return new_feature_view

    def with_relationship(
        self,
        from_source: SourceID | Source | str,
        to_source: SourceID | Source | str,
        *,
        from_foreign_key: str | None = None,
        to_foreign_key: str | None = None,
        directional: bool = False,
    ) -> FeatureView:
        """Define relationship between two sources.

        Args:
            from_source: The source on the "from" side (if dircectional)
            to_source: The source on the "to" side (if dircectional)
            from_foreign_key: The foreign key to use to match on the "from"
                source. Required if there is more than one foreign key relationship
                linking the sources. Cannot be used with "to_foreign_key".
            to_foreign_key: The foreign key to use to match on the "to"
                source. Required if there is more than one foreign key relationship
                linking the sources. Cannot be used with "from_foreign_key"
            directional: Whether to load graph as directional

        Example:
        >>> with_relationship(customer_source, order_source, directional=False)
        """
        match self._get_feature_view_source(from_source):
            case Ok(from_feature_view_source):
                pass
            case BadArgumentError() | NotFoundError():
                raise BadArgumentError(
                    "from_source does not match any source in this feature view",
                )

        match self._get_feature_view_source(to_source):
            case Ok(to_feature_view_source):
                pass
            case BadArgumentError() | NotFoundError():
                raise BadArgumentError(
                    "to_source does not match any source in this feature view",
                )

        if from_foreign_key and to_foreign_key:
            raise BadArgumentError(
                "only one of from_foreign_key and to_foreign_key may be provided",
            )

        from_foreign_key, to_foreign_key = self._check_or_infer_foreign_keys(
            from_feature_view_source,
            to_feature_view_source,
            from_foreign_key,
            to_foreign_key,
        ).unwrap_or_raise()

        if from_foreign_key:
            fkey_relationship = self._make_foreign_key_relationship(
                from_feature_view_source.source.id,
                from_foreign_key,
                to_feature_view_source,
            ).unwrap_or_raise()
        elif to_foreign_key:
            fkey_relationship = self._make_foreign_key_relationship(
                to_feature_view_source.source.id,
                to_foreign_key,
                from_feature_view_source,
            ).unwrap_or_raise()
        else:
            raise BadArgumentError(
                "foreign key relationship was not provided and could not be inferred"
            )

        relationships = [dataclasses.replace(val) for val in self.relationships]

        relationships.append(
            Relationship(
                from_feature_view_source=from_feature_view_source,
                to_feature_view_source=to_feature_view_source,
                fkey_relationship=fkey_relationship,
            )
        )
        if not directional:
            relationships.append(
                Relationship(
                    from_feature_view_source=to_feature_view_source,
                    to_feature_view_source=from_feature_view_source,
                    fkey_relationship=fkey_relationship,
                )
            )

        return dataclasses.replace(
            self,
            relationships=relationships,
        )
