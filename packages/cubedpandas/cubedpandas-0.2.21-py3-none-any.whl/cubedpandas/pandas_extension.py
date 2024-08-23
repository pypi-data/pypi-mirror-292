# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

import pandas as pd
from cubedpandas.cube import Cube
from cubedpandas.context.context import Context
from cubedpandas.settings import CachingStrategy, EAGER_CACHING_THRESHOLD


@pd.api.extensions.register_dataframe_accessor("cubed")
class CubedPandasAccessor:
    """
    A Pandas extension that provides the CubedPandas 'cubed' accessor for Pandas dataframes.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._df: pd.DataFrame = pandas_obj

    @staticmethod
    def _validate(df: pd.DataFrame):
        # Dataframe need to be non-empty
        if len(df) == 0:
            raise AttributeError("Method 'cubed' not provided for empty dataframe objects.")

    def __getattr__(self, item) -> Context:
        return Cube(self._df)[item]

    def __getitem__(self, address) -> Context:
        return Cube(self._df)[address]

    def __setitem__(self, address, value):
        Cube(self._df)[address] = value

    def __delitem__(self, address):
        del Cube(self._df)[address]

    @property
    def cube(self, schema=None,
             infer_schema: bool = True,
             exclude: str | list | tuple | None = None,
             read_only: bool = True,
             ignore_member_key_errors: bool = True,
             ignore_case: bool = True,
             ignore_key_errors: bool = True,
             caching: CachingStrategy = CachingStrategy.LAZY,
             caching_threshold: int = EAGER_CACHING_THRESHOLD,
             eager_evaluation: bool = True):
        """
         Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
        to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
        data manipulation and write back.

        Args:
            df:
                The Pandas dataframe to be wrapped into the CubedPandas `Cube` object.

            schema:
                (optional) A schema that defines the dimensions and measures of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter `infer_schema` is set to `True`. For further details please refer to the documentation of the
                `Schema` class.
                Default value is `None`.

            infer_schema:
                (optional) If no schema is provided and `infer_schema` is set to True, a suitable
                schema will be inferred from the unerlying dataframe. All numerical columns will
                be treated as measures, all other columns as dimensions. If this behaviour is not
                desired, a schema must be provided.
                Default value is `True`.

            exclude:
                (optional) Defines the columns that should be excluded from the cube if no schema is provied.
                If a column is excluded, it will not be part of the schema and can not be accessed through the cube.
                Excluded columns will be ignored during schema inference. Default value is `None`.

            read_only:
                (optional) Defines if write backs to the underlying dataframe are permitted.
                If read_only is set to `True`, write back attempts will raise an `PermissionError`.
                If read_only is set to `False`, write backs are permitted and will be pushed back
                to the underlying dataframe.
                Default value is `True`.

            ignore_case:
                (optional) If set to `True`, the case of member names will be ignored, 'Apple' and 'apple'
                will be treated as the same member. If set to `False`, member names are case-sensitive,
                'Apple' and 'apple' will be treated as different members.
                Default value is `True`.

            ignore_key_errors:
                (optional) If set to `True`, key errors for members of dimensions will be ignored and
                cell values will return 0.0 or `None` if no matching record exists. If set to `False`,
                key errors will be raised as exceptions when accessing cell values for non-existing members.
                Default value is `True`.

            caching:
                (optional) A caching strategy to be applied for accessing the cube. recommended
                value for almost all use cases is `CachingStrategy.LAZY`, which caches
                dimension members on first access. Caching can be beneficial for performance, but
                may also consume more memory. To cache all dimension members eagerly (on
                initialization of the cube), set this parameter to `CachingStrategy.EAGER`.
                Please refer to the documentation of 'CachingStrategy' for more information.
                Default value is `CachingStrategy.LAZY`.

            caching_threshold:
                (optional) The threshold as 'number of members' for EAGER caching only. If the number of
                distinct members in a dimension is below this threshold, the dimension will be cached
                eargerly, if caching is set to `CacheStrategy.EAGER` or `CacheStrategy.FULL`. Above this
                threshold, the dimension will be cached lazily.
                Default value is `EAGER_CACHING_THRESHOLD`, equivalent to 256 unique members per dimension.

            eager_evaluation:
                (optional) If set to `True`, the cube will evaluate the context eagerly, i.e. when the context
                is created. Eager evaluation is recommended for most use cases, as it simplifies debugging and
                error handling. If set to `False`, the cube will evaluate the context lazily, i.e. only when
                the value of a context is accessed/requested.

        Returns:
            A new Cube object that wraps the dataframe.

        Raises:
            PermissionError:
                If writeback is attempted on a read-only Cube.

            ValueError:
                If the schema is not valid or does not match the dataframe or if invalid
                dimension, member, measure or address agruments are provided.

        Examples:
            >>> df = pd.value([{"product": ["A", "B", "C"]}, {"value": [1, 2, 3]}])
            >>> cdf = cubed(df)
            >>> cdf["product:B"]
        """
        return Cube(df=self._df,
                    schema=schema, infer_schema=infer_schema,
                    exclude=exclude,
                    read_only=read_only,
                    ignore_member_key_errors=ignore_member_key_errors,
                    ignore_case=ignore_case,
                    ignore_key_errors=ignore_key_errors,
                    caching=caching,
                    caching_threshold=caching_threshold,
                    eager_evaluation=eager_evaluation)
