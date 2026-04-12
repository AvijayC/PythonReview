import collections.abc as C
import typing as T

import pydantic
import pytest
import sqlglot
import sqlglot.errors
import sqlglot.lineage
import sqlglot.optimizer.qualify
import sqlglot.optimizer.scope
from beartype import beartype
from sqlglot import exp


SQL_DIALECT = "snowflake"
AUTO_ALIAS_PREFIX = "_col_"


class TableSchema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    table_name: str
    columns: list[str] = pydantic.Field(min_length=1)

    @pydantic.field_validator("table_name")
    @classmethod
    def _validate_table_name(cls, value: T.Any) -> str:
        if not isinstance(value, str):
            raise TypeError("table_name must be a string.")
        return normalize_fully_qualified_table_name(value)

    @pydantic.field_validator("columns")
    @classmethod
    def _validate_columns(cls, value: T.Any) -> list[str]:
        if not isinstance(value, list):
            raise TypeError("columns must be a list of column names.")

        normalized_columns: list[str] = []
        for column_name in value:
            if not isinstance(column_name, str):
                raise TypeError("Every column name must be a string.")
            normalized_columns.append(normalize_column_name(column_name))

        if len(set(normalized_columns)) != len(normalized_columns):
            raise ValueError("columns must not contain duplicates after normalization.")

        return normalized_columns


class QueryLineageRequest(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    query: str = pydantic.Field(min_length=1)
    table_schemas: list[TableSchema] = pydantic.Field(min_length=1)

    @pydantic.field_validator("query")
    @classmethod
    def _validate_query(cls, value: T.Any) -> str:
        if not isinstance(value, str):
            raise TypeError("query must be a string.")
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("query must not be empty.")
        return stripped_value

    @pydantic.model_validator(mode="after")
    def _validate_unique_tables(self) -> "QueryLineageRequest":
        table_names = [table_schema.table_name for table_schema in self.table_schemas]
        duplicate_names = sorted(
            {
                table_name
                for table_name in table_names
                if table_names.count(table_name) > 1
            }
        )
        if duplicate_names:
            duplicate_display = ", ".join(duplicate_names)
            raise ValueError(
                f"table_schemas contains duplicate table definitions: {duplicate_display}."
            )
        return self


class LineageError(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, T.Any] = pydantic.Field(default_factory=dict)


class SourceColumn(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    table_name: str
    column_name: str


class OutputColumnLineage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    output_position: int
    output_name: str
    expression_sql: str
    source_columns: list[SourceColumn] = pydantic.Field(default_factory=list)


class QueryLineageResult(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    success: bool
    normalized_query: str | None = None
    output_columns: list[OutputColumnLineage] = pydantic.Field(default_factory=list)
    errors: list[LineageError] = pydantic.Field(default_factory=list)


@beartype
def split_identifier_path(raw_identifier: str) -> list[str]:
    stripped_identifier = raw_identifier.strip()
    if not stripped_identifier:
        raise ValueError("Identifier must not be empty.")

    parts: list[str] = []
    current_part: list[str] = []
    in_quotes = False
    index = 0

    while index < len(stripped_identifier):
        character = stripped_identifier[index]

        if character == '"':
            if in_quotes and index + 1 < len(stripped_identifier) and stripped_identifier[index + 1] == '"':
                current_part.append('"')
                index += 2
                continue

            in_quotes = not in_quotes
            current_part.append(character)
            index += 1
            continue

        if character == "." and not in_quotes:
            part = "".join(current_part).strip()
            if not part:
                raise ValueError(
                    f"Identifier '{raw_identifier}' contains an empty path segment."
                )
            parts.append(part)
            current_part = []
            index += 1
            continue

        current_part.append(character)
        index += 1

    if in_quotes:
        raise ValueError(f"Identifier '{raw_identifier}' has an unmatched quote.")

    final_part = "".join(current_part).strip()
    if not final_part:
        raise ValueError(f"Identifier '{raw_identifier}' contains an empty path segment.")
    parts.append(final_part)
    return parts


@beartype
def normalize_identifier_name(raw_identifier: str) -> str:
    parts = split_identifier_path(raw_identifier)
    if len(parts) != 1:
        raise ValueError(
            f"Identifier '{raw_identifier}' must be a single identifier, not a dotted path."
        )

    identifier = parts[0]
    if identifier.startswith('"') and identifier.endswith('"'):
        normalized = identifier[1:-1].replace('""', '"').strip().lower()
    else:
        normalized = identifier.strip().lower()

    if not normalized:
        raise ValueError(f"Identifier '{raw_identifier}' must not be empty.")
    return normalized


@beartype
def normalize_column_name(raw_column_name: str) -> str:
    return normalize_identifier_name(raw_column_name)


@beartype
def normalize_fully_qualified_table_name(raw_table_name: str) -> str:
    parts = split_identifier_path(raw_table_name)
    if len(parts) != 3:
        raise ValueError(
            "Fully qualified table names must use exactly three segments: database.schema.table."
        )
    return ".".join(normalize_identifier_name(part) for part in parts)


@beartype
def make_error(
    code: str,
    message: str,
    details: dict[str, T.Any] | None = None,
) -> LineageError:
    return LineageError(code=code, message=message, details=details or {})


@beartype
def build_sqlglot_schema(
    table_schemas: C.Sequence[TableSchema],
) -> dict[str, dict[str, dict[str, dict[str, str]]]]:
    schema: dict[str, dict[str, dict[str, dict[str, str]]]] = {}
    for table_schema in table_schemas:
        database_name, schema_name, table_name = table_schema.table_name.split(".")
        schema.setdefault(database_name, {}).setdefault(schema_name, {})[table_name] = {
            column_name: "TEXT" for column_name in table_schema.columns
        }
    return schema


@beartype
def build_schema_lookup(
    table_schemas: C.Sequence[TableSchema],
) -> dict[str, TableSchema]:
    return {table_schema.table_name: table_schema for table_schema in table_schemas}


@beartype
def parse_select_query(
    query: str,
) -> tuple[exp.Query | None, list[LineageError]]:
    try:
        statements = sqlglot.parse(query, dialect=SQL_DIALECT)
    except sqlglot.errors.ParseError as exc:
        return None, [
            make_error(
                code="invalid_sql",
                message=f"Query could not be parsed as Snowflake SQL: {exc}.",
            )
        ]

    if len(statements) != 1:
        return None, [
            make_error(
                code="invalid_sql",
                message=(
                    "Expected exactly one SQL statement. "
                    f"Received {len(statements)} statements."
                ),
                details={"statement_count": len(statements)},
            )
        ]

    expression = statements[0]
    if not isinstance(expression, exp.Query):
        return None, [
            make_error(
                code="unsupported_statement",
                message=(
                    "Only SELECT-style queries are supported. "
                    f"Received a {type(expression).__name__} statement."
                ),
            )
        ]

    return expression, []


@beartype
def iter_scopes(
    root_scope: sqlglot.optimizer.scope.Scope,
) -> C.Iterator[sqlglot.optimizer.scope.Scope]:
    yielded_scope_ids: set[int] = set()
    for scope in [root_scope, *root_scope.traverse()]:
        if id(scope) in yielded_scope_ids:
            continue
        yielded_scope_ids.add(id(scope))
        yield scope


@beartype
def collect_base_tables(expression: exp.Expression) -> list[exp.Table]:
    root_scope = sqlglot.optimizer.scope.build_scope(expression)
    if root_scope is None:
        return []

    tables_by_id: dict[int, exp.Table] = {}
    for scope in iter_scopes(root_scope):
        for source in scope.sources.values():
            if isinstance(source, exp.Table):
                tables_by_id[id(source)] = source
    return list(tables_by_id.values())


@beartype
def normalize_table_expression(table_expression: exp.Table) -> str:
    identifier_parts = [
        normalize_identifier_name(identifier.sql(dialect=SQL_DIALECT))
        for identifier in table_expression.parts
        if isinstance(identifier, exp.Identifier)
    ]

    if len(identifier_parts) != 3:
        raise ValueError(
            f"Table '{table_expression.sql(dialect=SQL_DIALECT)}' is not fully qualified."
        )

    return ".".join(identifier_parts)


@beartype
def validate_base_tables(
    base_tables: C.Sequence[exp.Table],
    schema_lookup: C.Mapping[str, TableSchema],
) -> list[LineageError]:
    invalid_tables: list[str] = []
    missing_tables: list[str] = []

    for table_expression in base_tables:
        try:
            normalized_table_name = normalize_table_expression(table_expression)
        except ValueError:
            invalid_tables.append(table_expression.sql(dialect=SQL_DIALECT))
            continue

        if normalized_table_name not in schema_lookup:
            missing_tables.append(normalized_table_name)

    errors: list[LineageError] = []

    if invalid_tables:
        unique_invalid_tables = sorted(set(invalid_tables))
        errors.append(
            make_error(
                code="non_fully_qualified_table",
                message=(
                    "Every physical table reference must be fully qualified as "
                    "database.schema.table. Found non-fully-qualified tables: "
                    f"{', '.join(unique_invalid_tables)}. CTE names and subquery aliases may "
                    "be short, but base tables may not."
                ),
                details={"tables": unique_invalid_tables},
            )
        )

    if missing_tables:
        unique_missing_tables = sorted(set(missing_tables))
        errors.append(
            make_error(
                code="table_not_found",
                message=(
                    "Missing table schema definitions for: "
                    f"{', '.join(unique_missing_tables)}. Provide a TableSchema entry for each "
                    "referenced fully qualified table, including all of its columns, before "
                    "running lineage analysis."
                ),
                details={
                    "missing_tables": unique_missing_tables,
                    "available_tables": sorted(schema_lookup),
                },
            )
        )

    return errors


@beartype
def qualify_query(
    expression: exp.Query,
    schema: dict[str, T.Any],
) -> exp.Query:
    qualified_expression = sqlglot.optimizer.qualify.qualify(
        expression.copy(),
        dialect=SQL_DIALECT,
        schema=schema,
        identify=False,
        quote_identifiers=False,
        allow_partial_qualification=False,
        validate_qualify_columns=True,
        expand_stars=True,
    )
    if not isinstance(qualified_expression, exp.Query):
        raise TypeError(
            "Expected sqlglot qualification to return a Query expression."
        )
    return qualified_expression


@beartype
def normalize_lineage_leaf_column_name(raw_leaf_name: str) -> str:
    parsed_column = sqlglot.parse_one(raw_leaf_name, into=exp.Column, dialect=SQL_DIALECT)
    return normalize_column_name(parsed_column.name)


@beartype
def extract_source_columns(lineage_node: sqlglot.lineage.Node) -> list[SourceColumn]:
    source_columns_by_key: dict[tuple[str, str], SourceColumn] = {}

    for node in lineage_node.walk():
        if node.downstream:
            continue
        if not isinstance(node.expression, exp.Table):
            continue

        table_name = normalize_table_expression(node.expression)
        column_name = normalize_lineage_leaf_column_name(node.name)
        source_key = (table_name, column_name)
        source_columns_by_key[source_key] = SourceColumn(
            table_name=table_name,
            column_name=column_name,
        )

    return [
        source_columns_by_key[source_key]
        for source_key in sorted(source_columns_by_key)
    ]


@beartype
def select_expression_sql(select_expression: exp.Expression) -> str:
    if isinstance(select_expression, exp.Alias):
        return select_expression.this.sql(dialect=SQL_DIALECT)
    return select_expression.sql(dialect=SQL_DIALECT)


@beartype
def select_output_name(select_expression: exp.Expression) -> str:
    alias_or_name = select_expression.alias_or_name or ""
    if alias_or_name and not (
        alias_or_name.startswith(AUTO_ALIAS_PREFIX)
        and alias_or_name[len(AUTO_ALIAS_PREFIX) :].isdigit()
    ):
        return normalize_identifier_name(alias_or_name)
    return select_expression_sql(select_expression).lower()


@beartype
def build_output_columns(
    qualified_expression: exp.Query,
) -> tuple[list[OutputColumnLineage], list[LineageError]]:
    root_scope = sqlglot.optimizer.scope.build_scope(qualified_expression)
    if root_scope is None:
        return [], [
            make_error(
                code="lineage_internal_error",
                message="Could not build a SQL scope for the qualified query.",
            )
        ]

    output_columns: list[OutputColumnLineage] = []
    errors: list[LineageError] = []

    for output_index, select_expression in enumerate(qualified_expression.selects, start=1):
        try:
            lineage_node = sqlglot.lineage.to_node(
                output_index - 1,
                scope=root_scope,
                dialect=SQL_DIALECT,
                trim_selects=True,
            )
        except Exception as exc:
            errors.append(
                make_error(
                    code="lineage_resolution_error",
                    message=(
                        f"Could not build lineage for output column {output_index}: {exc}."
                    ),
                    details={"output_position": output_index},
                )
            )
            continue

        source_columns = extract_source_columns(lineage_node)
        if not source_columns:
            errors.append(
                make_error(
                    code="lineage_resolution_error",
                    message=(
                        f"Lineage for output column {output_index} did not resolve to any "
                        "base table columns."
                    ),
                    details={"output_position": output_index},
                )
            )
            continue

        output_columns.append(
            OutputColumnLineage(
                output_position=output_index,
                output_name=select_output_name(select_expression),
                expression_sql=select_expression_sql(select_expression),
                source_columns=source_columns,
            )
        )

    return output_columns, errors


@beartype
def analyze_select_lineage_request(
    request: QueryLineageRequest,
) -> QueryLineageResult:
    schema_lookup = build_schema_lookup(request.table_schemas)
    expression, parse_errors = parse_select_query(request.query)
    if parse_errors:
        return QueryLineageResult(success=False, errors=parse_errors)
    assert expression is not None

    base_tables = collect_base_tables(expression)
    table_validation_errors = validate_base_tables(base_tables, schema_lookup)
    if table_validation_errors:
        return QueryLineageResult(success=False, errors=table_validation_errors)

    sqlglot_schema = build_sqlglot_schema(request.table_schemas)

    try:
        qualified_expression = qualify_query(expression, sqlglot_schema)
    except sqlglot.errors.SqlglotError as exc:
        return QueryLineageResult(
            success=False,
            errors=[
                make_error(
                    code="lineage_resolution_error",
                    message=(
                        "Query parsing succeeded, but column lineage resolution failed: "
                        f"{exc}."
                    ),
                )
            ],
        )

    output_columns, output_errors = build_output_columns(qualified_expression)
    success = not output_errors
    return QueryLineageResult(
        success=success,
        normalized_query=qualified_expression.sql(dialect=SQL_DIALECT),
        output_columns=output_columns,
        errors=output_errors,
    )


@beartype
def analyze_select_lineage(
    query: str,
    table_schemas: C.Sequence[TableSchema],
) -> QueryLineageResult:
    try:
        request = QueryLineageRequest(
            query=query,
            table_schemas=list(table_schemas),
        )
    except pydantic.ValidationError as exc:
        return QueryLineageResult(
            success=False,
            errors=[
                make_error(
                    code="invalid_request",
                    message="Input validation failed for the lineage request.",
                    details={"validation_errors": exc.errors()},
                )
            ],
        )

    return analyze_select_lineage_request(request)


@beartype
def build_northwind_table_schemas() -> list[TableSchema]:
    return [
        TableSchema(
            table_name="northwind.public.categories",
            columns=["category_id", "category_name", "description", "picture"],
        ),
        TableSchema(
            table_name="northwind.public.customer_demographics",
            columns=["customer_type_id", "customer_desc"],
        ),
        TableSchema(
            table_name="northwind.public.customers",
            columns=[
                "customer_id",
                "company_name",
                "contact_name",
                "contact_title",
                "address",
                "city",
                "region",
                "postal_code",
                "country",
                "phone",
                "fax",
            ],
        ),
        TableSchema(
            table_name="northwind.public.customer_customer_demo",
            columns=["customer_id", "customer_type_id"],
        ),
        TableSchema(
            table_name="northwind.public.employees",
            columns=[
                "employee_id",
                "last_name",
                "first_name",
                "title",
                "title_of_courtesy",
                "birth_date",
                "hire_date",
                "address",
                "city",
                "region",
                "postal_code",
                "country",
                "home_phone",
                "extension",
                "photo",
                "notes",
                "reports_to",
                "photo_path",
            ],
        ),
        TableSchema(
            table_name="northwind.public.suppliers",
            columns=[
                "supplier_id",
                "company_name",
                "contact_name",
                "contact_title",
                "address",
                "city",
                "region",
                "postal_code",
                "country",
                "phone",
                "fax",
                "homepage",
            ],
        ),
        TableSchema(
            table_name="northwind.public.products",
            columns=[
                "product_id",
                "product_name",
                "supplier_id",
                "category_id",
                "quantity_per_unit",
                "unit_price",
                "units_in_stock",
                "units_on_order",
                "reorder_level",
                "discontinued",
            ],
        ),
        TableSchema(
            table_name="northwind.public.region",
            columns=["region_id", "region_description"],
        ),
        TableSchema(
            table_name="northwind.public.shippers",
            columns=["shipper_id", "company_name", "phone"],
        ),
        TableSchema(
            table_name="northwind.public.orders",
            columns=[
                "order_id",
                "customer_id",
                "employee_id",
                "order_date",
                "required_date",
                "shipped_date",
                "ship_via",
                "freight",
                "ship_name",
                "ship_address",
                "ship_city",
                "ship_region",
                "ship_postal_code",
                "ship_country",
            ],
        ),
        TableSchema(
            table_name="northwind.public.territories",
            columns=["territory_id", "territory_description", "region_id"],
        ),
        TableSchema(
            table_name="northwind.public.employee_territories",
            columns=["employee_id", "territory_id"],
        ),
        TableSchema(
            table_name="northwind.public.order_details",
            columns=["order_id", "product_id", "unit_price", "quantity", "discount"],
        ),
        TableSchema(
            table_name="northwind.public.us_states",
            columns=["state_id", "state_name", "state_abbr", "state_region"],
        ),
    ]


NORTHWIND_TABLE_SCHEMAS = build_northwind_table_schemas()


@beartype
def source_pairs(output_column: OutputColumnLineage) -> set[tuple[str, str]]:
    return {
        (source_column.table_name, source_column.column_name)
        for source_column in output_column.source_columns
    }


@beartype
def assert_successful_result(result: QueryLineageResult) -> None:
    assert result.success, result.model_dump()
    assert not result.errors, result.model_dump()


@beartype
def assert_failed_result(
    result: QueryLineageResult,
    expected_error_code: str,
) -> None:
    assert not result.success, result.model_dump()
    assert any(error.code == expected_error_code for error in result.errors), result.model_dump()


@beartype
def test_direct_passthrough_single_table() -> None:
    result = analyze_select_lineage(
        query="SELECT order_id, customer_id FROM northwind.public.orders",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert [output.output_name for output in result.output_columns] == ["order_id", "customer_id"]
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "order_id")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.orders", "customer_id")}


@beartype
def test_unique_unqualified_columns_are_inferred_from_joined_tables() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT company_name, ship_name
        FROM northwind.public.customers c
        JOIN northwind.public.orders o
          ON c.customer_id = o.customer_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.customers", "company_name")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.orders", "ship_name")}


@beartype
def test_computed_expression_collects_all_base_columns() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT od.unit_price * od.quantity * (1 - od.discount) AS line_total
        FROM northwind.public.order_details od
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert result.output_columns[0].output_name == "line_total"
    assert source_pairs(result.output_columns[0]) == {
        ("northwind.public.order_details", "unit_price"),
        ("northwind.public.order_details", "quantity"),
        ("northwind.public.order_details", "discount"),
    }


@beartype
def test_top_level_star_expands_from_single_table() -> None:
    result = analyze_select_lineage(
        query="SELECT * FROM northwind.public.shippers",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert [output.output_name for output in result.output_columns] == [
        "shipper_id",
        "company_name",
        "phone",
    ]
    assert source_pairs(result.output_columns[1]) == {("northwind.public.shippers", "company_name")}


@beartype
def test_cte_passthrough_tracks_back_to_base_table() -> None:
    result = analyze_select_lineage(
        query="""
        WITH recent_orders AS (
            SELECT order_id, customer_id
            FROM northwind.public.orders
        )
        SELECT customer_id
        FROM recent_orders
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "customer_id")}


@beartype
def test_nested_ctes_can_shadow_the_same_name() -> None:
    result = analyze_select_lineage(
        query="""
        WITH orders AS (
            WITH orders AS (
                SELECT order_id, customer_id
                FROM northwind.public.orders
            )
            SELECT order_id, customer_id
            FROM orders
        )
        SELECT customer_id
        FROM orders
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "customer_id")}


@beartype
def test_subqueries_can_reuse_alias_names_without_breaking_lineage() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT o.order_id
        FROM (
            SELECT o.order_id, o.customer_id
            FROM northwind.public.orders o
        ) o
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "order_id")}


@beartype
def test_multi_join_cte_combination_resolves_non_aliased_columns() -> None:
    result = analyze_select_lineage(
        query="""
        WITH order_lines AS (
            SELECT o.order_id, o.customer_id, od.product_id, quantity
            FROM northwind.public.orders o
            JOIN northwind.public.order_details od
              ON o.order_id = od.order_id
        )
        SELECT company_name, product_name, quantity
        FROM order_lines ol
        JOIN northwind.public.customers c
          ON ol.customer_id = c.customer_id
        JOIN northwind.public.products p
          ON ol.product_id = p.product_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.customers", "company_name")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.products", "product_name")}
    assert source_pairs(result.output_columns[2]) == {("northwind.public.order_details", "quantity")}


@beartype
def test_case_expression_collects_every_branch_column() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT CASE
            WHEN shipped_date IS NULL THEN required_date
            ELSE shipped_date
        END AS fulfillment_date
        FROM northwind.public.orders
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {
        ("northwind.public.orders", "required_date"),
        ("northwind.public.orders", "shipped_date"),
    }


@beartype
def test_union_all_collects_sources_from_both_branches() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT customer_id
        FROM northwind.public.orders
        UNION ALL
        SELECT customer_id
        FROM northwind.public.customers
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {
        ("northwind.public.orders", "customer_id"),
        ("northwind.public.customers", "customer_id"),
    }


@beartype
def test_self_join_keeps_both_aliases_mapped_to_the_same_base_table() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT manager.last_name AS manager_last_name, staff.last_name AS staff_last_name
        FROM northwind.public.employees staff
        LEFT JOIN northwind.public.employees manager
          ON staff.reports_to = manager.employee_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.employees", "last_name")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.employees", "last_name")}


@beartype
def test_quoted_fully_qualified_table_names_are_supported() -> None:
    quoted_schemas = [
        TableSchema(
            table_name='"NORTHWIND"."PUBLIC"."ORDERS"',
            columns=["ORDER_ID", "CUSTOMER_ID"],
        )
    ]
    result = analyze_select_lineage(
        query='SELECT "ORDER_ID" FROM "NORTHWIND"."PUBLIC"."ORDERS"',
        table_schemas=quoted_schemas,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "order_id")}


@beartype
def test_missing_table_returns_descriptive_error() -> None:
    result = analyze_select_lineage(
        query="SELECT order_id FROM northwind.public.invoices",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "table_not_found")
    assert "northwind.public.invoices" in result.errors[0].message


@beartype
def test_non_fully_qualified_table_returns_error() -> None:
    result = analyze_select_lineage(
        query="SELECT order_id FROM orders",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "non_fully_qualified_table")
    assert "orders" in result.errors[0].message.lower()


@beartype
def test_invalid_sql_with_multiple_statements_returns_error() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT order_id FROM northwind.public.orders;
        SELECT customer_id FROM northwind.public.customers
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "invalid_sql")


@beartype
def test_non_select_statement_returns_error() -> None:
    result = analyze_select_lineage(
        query="DELETE FROM northwind.public.orders",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "unsupported_statement")


@beartype
def test_ambiguous_unqualified_column_returns_resolution_error() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT customer_id
        FROM northwind.public.orders o
        JOIN northwind.public.customers c
          ON o.customer_id = c.customer_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "lineage_resolution_error")


@beartype
def test_unknown_column_returns_resolution_error() -> None:
    result = analyze_select_lineage(
        query="SELECT does_not_exist FROM northwind.public.orders",
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_failed_result(result, "lineage_resolution_error")


@beartype
def test_duplicate_schema_entries_are_rejected_after_normalization() -> None:
    result = analyze_select_lineage(
        query="SELECT order_id FROM northwind.public.orders",
        table_schemas=[
            TableSchema(
                table_name="northwind.public.orders",
                columns=["order_id", "customer_id"],
            ),
            TableSchema(
                table_name='"NORTHWIND"."PUBLIC"."ORDERS"',
                columns=["order_id", "customer_id"],
            ),
        ],
    )
    assert_failed_result(result, "invalid_request")


@beartype
def test_star_through_cte_expands_and_resolves_to_base_table_columns() -> None:
    result = analyze_select_lineage(
        query="""
        WITH shipper_subset AS (
            SELECT shipper_id, company_name
            FROM northwind.public.shippers
        )
        SELECT *
        FROM shipper_subset
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert [output.output_name for output in result.output_columns] == ["shipper_id", "company_name"]
    assert source_pairs(result.output_columns[0]) == {("northwind.public.shippers", "shipper_id")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.shippers", "company_name")}


@beartype
def test_nested_cte_and_subquery_combo_with_reused_names_resolves_correctly() -> None:
    result = analyze_select_lineage(
        query="""
        WITH customer_rollup AS (
            WITH customer_rollup AS (
                SELECT c.customer_id, c.company_name, o.order_id
                FROM northwind.public.customers c
                JOIN northwind.public.orders o
                  ON c.customer_id = o.customer_id
            )
            SELECT customer_id, company_name, order_id
            FROM customer_rollup
        )
        SELECT customer_id, company_name
        FROM (
            SELECT customer_id, company_name
            FROM customer_rollup
        ) customer_rollup
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.customers", "customer_id")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.customers", "company_name")}


@beartype
def test_coalesce_across_join_collects_sources_from_both_tables() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT COALESCE(c.region, o.ship_region) AS region_for_reporting
        FROM northwind.public.customers c
        JOIN northwind.public.orders o
          ON c.customer_id = o.customer_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {
        ("northwind.public.customers", "region"),
        ("northwind.public.orders", "ship_region"),
    }


@beartype
def test_deep_join_chain_resolves_each_output_to_the_correct_table() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT category_name, company_name, quantity
        FROM northwind.public.order_details od
        JOIN northwind.public.products p
          ON od.product_id = p.product_id
        JOIN northwind.public.categories c
          ON p.category_id = c.category_id
        JOIN northwind.public.suppliers s
          ON p.supplier_id = s.supplier_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert source_pairs(result.output_columns[0]) == {("northwind.public.categories", "category_name")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.suppliers", "company_name")}
    assert source_pairs(result.output_columns[2]) == {("northwind.public.order_details", "quantity")}


@beartype
def test_reused_duplicate_output_names_are_handled_by_position() -> None:
    result = analyze_select_lineage(
        query="""
        SELECT o.customer_id, c.customer_id
        FROM northwind.public.orders o
        JOIN northwind.public.customers c
          ON o.customer_id = c.customer_id
        """,
        table_schemas=NORTHWIND_TABLE_SCHEMAS,
    )
    assert_successful_result(result)
    assert result.output_columns[0].output_position == 1
    assert result.output_columns[1].output_position == 2
    assert source_pairs(result.output_columns[0]) == {("northwind.public.orders", "customer_id")}
    assert source_pairs(result.output_columns[1]) == {("northwind.public.customers", "customer_id")}


@beartype
def test_schema_model_rejects_invalid_table_name() -> None:
    with pytest.raises(pydantic.ValidationError):
        TableSchema(table_name="northwind.orders", columns=["order_id"])


@beartype
def test_schema_model_rejects_duplicate_columns() -> None:
    with pytest.raises(pydantic.ValidationError):
        TableSchema(
            table_name="northwind.public.orders",
            columns=["order_id", '"ORDER_ID"'],
        )
