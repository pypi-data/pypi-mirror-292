"""
Configure your application's pages.
"""

import type_enforced

from itertools import chain
from cave_utils.api_utils.validator_utils import ApiValidator, CustomKeyValidator


@type_enforced.Enforcer
class pages(ApiValidator):
    """
    The pages are located under the path **`pages`**.
    """

    @staticmethod
    def spec(currentPage: [str, None] = None, data: dict = dict(), **kwargs):
        """
        Arguments:

        * **`current_page`**: `[str]` = `None` &rarr; The id of the current page that is being rendered.
        * **`data`**: `[dict]` = `{}` &rarr; The data to pass to `pages.data.*`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        data = self.data.get("data", {})
        CustomKeyValidator(
            data=data, log=self.log, prepend_path=["data"], validator=pages_data_star, **kwargs
        )
        currentPage = self.data.get("currentPage")
        if isinstance(currentPage, str):
            self.__check_subset_valid__(
                subset=[currentPage], valid_values=list(data.keys()), prepend_path=["currentPage"]
            )


@type_enforced.Enforcer
class pages_data_star(ApiValidator):
    """
    The pages data are located under the path **`pages.data`**.
    """

    @staticmethod
    def spec(pageLayout: list, lockedLayout: bool = False, **kwargs):
        """
        Arguments:

        * **`pageLayout`**: `[list]` = `{}` &rarr; The layout of the page.
            * **See**: `cave_utils.api.pages.pages_data_star_pageLayout`.
        * **`lockedLayout`**: `[bool]` = `False` &rarr; Whether or not the layout should be locked.
            * **See**: `cave_utils.api.pages.pages_data_star_pageLayout`.
        """
        return {"kwargs": kwargs, "accepted_values": {}}

    def __extend_spec__(self, **kwargs):
        for idx, pageLayout in enumerate(self.data.get("pageLayout", [])):
            pages_data_star_pageLayout(
                data=pageLayout,
                log=self.log,
                prepend_path=["pageLayout", idx],
                **kwargs,
            )


@type_enforced.Enforcer
class pages_data_star_pageLayout(ApiValidator):
    """
    The page layouts are located under the path **`pages.data.pageLayout`**.
    """

    @staticmethod
    def spec(
        type: str = "groupedOutput",
        variant: str = "bar",
        mapId: [str, None] = None,
        groupingId: [list, None] = None,
        sessions: [list, None] = None,
        globalOutput: [list, None] = None,
        groupingLevel: [list, None] = None,
        lockedLayout: bool = False,
        statAggregation: str = "sum",
        groupedOutputDataId: [str, list, None] = None,
        statId: [str, list, None] = None,
        showToolbar: bool = True,
        maximized: bool = False,
        defaultToZero: bool = False,
        distributionType: [str, None] = None,
        distributionYAxis: [str, None] = None,
        distributionVariant: [str, None] = None,
        showNA: bool = False,
        **kwargs,
    ):
        """
        Arguments:

        * **`type`**: `[str]` = `"groupedOutput"` &rarr; The type of the page layout.
            * **Accepted Values**:
                * `"groupedOutput"`: The `unit` appears after the value.
                * `"globalOutput"`: The `unit` appears after the value, separated by a space.
                * `"map"`: The `unit` appears before the value.
        * **`variant`**: `[str]` = `"bar"` &rarr; The variant of the page layout.
            * Accepted Values:
                * When **`type`** == `"groupedOutput"`:
                    * `"area"`: An [area chart][]
                    * `"bar"`: A [bar chart][]
                    * `"stacked_bar"`: A [stacked bar chart][]
                    * `"box_plot"`: A [box plot chart][]
                    * `"cumulative_line"`: A cumulative line chart
                    * `"gauge"`: A [gauge chart][]
                    * `"heatmap"`: A [heatmap chart][]
                    * `"line"`: A [line chart][]
                    * `"scatter"`: A [scatter chart][]
                    * `"stacked_area"`: An [stacked area chart][]
                    * `"stacked_waterfall"`: An [stacked waterfall chart][]
                    * `"sunburst"`: A [sunburst chart][]
                    * `"table"`: A table showing the aggregated values.
                    * `"treemap"`: A [treemap chart][]
                    * `"waterfall"`: A [waterfall chart][]
                    * `"distribution"`: A [distribution chart][]
                * When **`type`** == `"globalOutput"`:
                    * `"bar"`: A [bar chart][]
                    * `"line"`: A [line chart][]
                    * `"table"`: A [table chart][]
                    * `"overview"`: A summary of the global outputs presented in a KPI-like format
                * Otherwise:
                    * `None`
        * **`mapId`**: `[str]` = `None` &rarr; The id of the map to use.
        * **`groupingId`**: `[list]` = `None` &rarr; The ids of the grouping to use.
        * **`sessions`**: `[list]` = `None` &rarr; The ids of the sessions to use.
        * **`globalOutput`**: `[list]` = `None` &rarr; The ids of the global outputs to use.
        * **`groupingLevel`**: `[list]` = `None` &rarr; The ids of the grouping levels to use.
        * **`lockedLayout`**: `[bool]` = `False` &rarr; Whether or not the layout should be locked.
        * **`statAggregation`**: `[str]` = `"sum"` &rarr; A stat aggregation function to apply to the chart data.
            * **Accepted Values**:
                * `"sum"`: Add up aggregated data
                * `"mean"`: Calculate the mean of the aggregated data
                * `"min"`: Find the minimum values within the aggregated data
                * `"max"`: Find the maximum values the aggregated data
        * **`groupedOutputDataId`**: `[str | list]` = `None` &rarr; The id or list of ids representing the grouped output data to use.
        * **`statId`**: `[str | list]` = `None` &rarr; The id or list of ids corresponding to the stat(s) to be used.
        * **`showToolbar`**: `[bool]` = `None` &rarr; Whether or not the chart toolbar should be shown.
            * **Note**: If left unspecified (i.e., `None`), it will default to `settings.showToolbar`.
        * **`maximized`**: `[bool]` = `False` &rarr; Whether or not the layout should be maximized.
            * **Note**: If more than one chart belonging to the same page layout is set to `True`, the first one found in the list will take precedence.
        * **`defaultToZero`**: `[bool]` = `False` &rarr; Whether or not the chart should default missing values to zero.
        * **`distributionType`**: `[str]` = `None` &rarr; The type of distribution function displayed in distribution charts.
            * Accepted Values:
                * `"pdf"`: Uses the probability density function.
                * `"cdf"`: Uses the cumulative density function.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"pdf"`.
                * This attribute is applicable exclusively to the `"distribution"` variant.
        * **`distributionYAxis`**: `[str]` = `None` &rarr; The y-axis metric in distribution charts.
            * Accepted Values:
                * `"counts"`: Displays the y-axis as raw counts of occurrences.
                * `"density"`: Displays the y-axis as proportions of total counts.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"counts"`.
                * This attribute is applicable exclusively to the `"distribution"` variant.
        * **`distributionVariant`**: `[str]` = `None` &rarr; The chart type displayed in distribution charts.
            * Accepted Values:
                * `"bar"`: A bar chart.
                * `"line"`: A line chart.
            * **Notes**:
                * If left unspecified (i.e., `None`), it will default to `"bar"`.
                * This attribute is applicable exclusively to the `"distribution"` variant.
        * **`showNA`**: `[bool]` = `False` &rarr; Whether to display missing or filtered values in both the chart tooltip and the axis.

        [area chart]: https://en.wikipedia.org/wiki/Area_chart
        [bar chart]: https://en.wikipedia.org/wiki/Bar_chart
        [stacked bar chart]: https://en.wikipedia.org/wiki/Bar_chart
        [box plot chart]: https://en.wikipedia.org/wiki/Box_plot
        [cumulative line chart]: #
        [gauge chart]: https://echarts.apache.org/examples/en/index.html#chart-type-gauge
        [heatmap chart]: https://en.wikipedia.org/wiki/Heat_map
        [line chart]: https://en.wikipedia.org/wiki/Line_chart
        [scatter chart]: https://en.wikipedia.org/wiki/Scatter_plot
        [stacked area chart]: https://en.wikipedia.org/wiki/Area_chart
        [stacked waterfall chart]: https://en.wikipedia.org/wiki/Waterfall_chart
        [sunburst chart]: https://en.wikipedia.org/wiki/Pie_chart#Ring_chart,_sunburst_chart,_and_multilevel_pie_chart
        [table chart]: #
        [treemap chart]: https://en.wikipedia.org/wiki/Treemapping
        [waterfall chart]: https://en.wikipedia.org/wiki/Waterfall_chart
        [distribution chart]: https://en.wikipedia.org/wiki/Probability_distribution
        """
        if type == "globalOutput":
            variant_options = ["bar", "line", "table", "overview"]
        elif type == "groupedOutput":
            variant_options = [
                "area",
                "bar",
                "stacked_bar",
                "box_plot",
                "cumulative_line",
                "gauge",
                "heatmap",
                "line",
                "scatter",
                "distribution",
                "stacked_area",
                "stacked_waterfall",
                "sunburst",
                "table",
                "treemap",
                "waterfall",
                "distribution",
            ]
        else:
            variant_options = []
        return {
            "kwargs": kwargs,
            "accepted_values": {
                "type": ["groupedOutput", "globalOutput", "map"],
                "variant": variant_options,
                "statAggregation": ["sum", "mean", "min", "max"],
                "distributionType": ["pdf", "cdf"] if variant == "distribution" else [],
                "distributionYAxis": ["counts", "density"] if variant == "distribution" else [],
                "distributionVariant": ["bar", "line"] if variant == "distribution" else [],
            },
        }

    def __extend_spec__(self, **kwargs):
        pageLayout_type = self.data.get("type", "groupedOutput")
        # Validate globalOutput
        if pageLayout_type == "globalOutput":
            globalOutput = self.data.get("globalOutput")
            if globalOutput is not None:
                self.__check_subset_valid__(
                    subset=globalOutput,
                    valid_values=kwargs.get("globalOuputs_validPropIds", []),
                    prepend_path=["globalOutput"],
                )
            elif self.data.get("variant") != "overview":
                self.__error__(
                    msg="`globalOutput` is a required key for `globalOutput` type pageLayouts when variant is not `overview`.",
                    path=["globalOutput"],
                )
        # Validate map
        elif pageLayout_type == "map":
            mapId = self.data.get("mapId")
            if mapId is not None:
                self.__check_subset_valid__(
                    subset=[mapId],
                    valid_values=kwargs.get("maps_validMapIds", []),
                    prepend_path=["mapId"],
                )
            else:
                self.__error__(
                    msg="`mapId` is required for `map` type pageLayouts.",
                    prepend_path=["mapId"],
                )
        # Validate groupedOutput
        else:
            # Validate groupedOutputDataId
            groupedOutputDataId_raw = self.data.get("groupedOutputDataId")
            groupedOutputDataId = (
                [groupedOutputDataId_raw]
                if isinstance(groupedOutputDataId_raw, str)
                else groupedOutputDataId_raw
            )
            if groupedOutputDataId is not None:
                self.__check_type__(
                    groupedOutputDataId, (str, list), prepend_path=["groupedOutputDataId"]
                )
                # Ensure that the groupedOutputDataId is valid
                self.__check_subset_valid__(
                    subset=groupedOutputDataId,
                    valid_values=list(kwargs.get("groupedOutputs_validGroupIds", {}).keys()),
                    prepend_path=["groupedOutputDataId"],
                )
            # Validate statId
            statId_raw = self.data.get("statId")
            if statId_raw is not None:
                self.__check_type__(statId_raw, (str, list), prepend_path=["statId"])
                statId = statId_raw if isinstance(statId_raw, list) else [statId_raw]
                if len(groupedOutputDataId) != len(statId):
                    self.__error__(
                        msg="`groupingId` and `statId` must be the same length.",
                    )
                    return
                for idx, sid in enumerate(statId):
                    # Ensure that the statId is valid
                    self.__check_subset_valid__(
                        subset=[sid],
                        valid_values=list(
                            kwargs.get("groupedOutputs_validStatIds", {}).get(
                                groupedOutputDataId[idx], []
                            )
                        ),
                        prepend_path=["statId", idx],
                    )
            # Validate groupingId
            groupingId = self.data.get("groupingId")
            if groupingId is not None:
                self.__check_type__(groupingId, list, prepend_path=["groupingId"])
                all_valid_group_ids = chain.from_iterable([
                    kwargs.get("groupedOutputs_validGroupIds", {}).get(groupingId_item, [])
                    for groupingId_item in groupedOutputDataId
                ])
                valid_values = list(set(all_valid_group_ids))
                # Ensure that the groupingId is valid
                self.__check_subset_valid__(
                    subset=groupingId,
                    valid_values=valid_values,
                    prepend_path=["groupingId"],
                )
            # Validate groupingLevel
            groupingLevel = self.data.get("groupingLevel")
            if groupingLevel is not None:
                self.__check_type__(groupingLevel, list, prepend_path=["groupingLevel"])
                if len(groupingId) != len(groupingLevel):
                    self.__error__(
                        msg="`groupingId` and `groupingLevel` must be the same length.",
                    )
                    return
                for idx, groupingId_item in enumerate(groupingId):
                    groupingLevel_item = groupingLevel[idx]
                    self.__check_subset_valid__(
                        subset=[groupingLevel_item],
                        valid_values=list(
                            kwargs.get("groupedOutputs_validLevelIds", {}).get(groupingId_item, [])
                        ),
                        prepend_path=["groupingLevel", idx],
                    )
