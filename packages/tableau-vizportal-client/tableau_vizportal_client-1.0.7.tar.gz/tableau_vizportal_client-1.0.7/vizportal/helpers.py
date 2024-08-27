from typing import Union, List, Dict, Any
import urllib.parse as urlparse
from urllib.parse import parse_qs

from vizportal.pager import VizportalPager
from vizportal.payload import PayloadBuilder, FilterClauseBuilder, SortBuilder


def merge_results_by_keys(
    results: Union[VizportalPager, List[Dict[str, Union[List, Dict]]]],
    keys: Union[str, List[str]],
) -> Dict[str, List]:
    """Merges paged results by key.
    This is useful for combining nested lists from multiple page results into a single object.

    Args:
        results (Union[VizportalPager, List[Dict[str, Union[List, Dict]]]]):
            The results to merge.
        keys (Union[str, List[str]]):
            The keys to merge.

    Returns:
        Dict[str, List]: The merged results.

    Example:
    --------
        merge_results_by_keys(results, ["workbooks", "projects", "users"])
        >>> {"workbooks": [...], "projects": [...], "users": [...]}
    """
    merged_results: Dict[str, List] = {}
    if isinstance(keys, str):
        keys = [keys]
    if isinstance(results, VizportalPager):
        results = list(results)

    for key in keys:
        # Initialize a new list for this key.
        merged_results[key] = []
        for result in results:
            if len(result.keys()) > 2:
                if not isinstance(result, dict):
                    raise TypeError(f"Result is not a dict. Found type: {type(result)}")
                # Check that the key exists.
                if key not in list(result.keys()):
                    raise ValueError(
                        f"Key {key} not found in result. Found Keys: {list(result.keys())}"
                    )
                key_results = result[key]
                if isinstance(key_results, list):
                    merged_results[key].extend(key_results)
                else:
                    merged_results[key].append(key_results)
    # Return the merged results.
    return merged_results


def tableau_url_to_vizportal_api(url: str) -> Dict[str, Any]:
    """Converts a Tableau URL to a Vizportal API payload.

    Args:
        url (str): The Tableau URL to convert.

    Returns:
        Dict[str, Any]: The Vizportal API payload.
    
    Example:
    --------
        tableau_url_to_vizportal_api("https://example.tableau.com/#/datasources?hasPassword=true&order=name%3Aasc&owner=12345")
        >>> {
                "method": "getDatasources",
                "params": {
                    "filter": {
                        "clauses": [
                            {
                                "operator": "eq",
                                "field": "hasPassword",
                                "value": "true"
                            },
                            {
                                "operator": "eq",
                                "field": "owner",
                                "value": "12345"
                            }
                        ]
                    },
                    "order": [
                        {
                            "field": "name",
                            "direction": "asc"
                        }
                    ]
                }
            }
    """

    # Parse the URL
    parsed_url = urlparse.urlparse(url)
    url_fragment = parsed_url.fragment
    
    payload_builder = PayloadBuilder()
    filter_clause_builder = FilterClauseBuilder()

    # Extract the resource type from the path (e.g., "workbooks", "datasources", etc.)
    url_args = url_fragment.split('?') if url_fragment else []
    resource_type = url_args[0].split('/')[-1] if url_args else parsed_url.fragment.split('/')[-1]

    payload_builder.add_method(f"get{resource_type.capitalize()}")

    if len(url_args) > 1:
        # Dynamically process query parameters to build the payload
        url_args = parse_qs(url_args[1])
        
        for key, values in url_args.items():
            if key == 'order':
                # Handle sorting parameters
                for value in values:
                    field, direction = value.split(':')
                    sort_builder = SortBuilder(field=field, direction=direction)
                    payload_builder.add_order(sort_builder)
            else:
                # Assume any other parameters are filters
                for value in values:
                    filter_clause_builder.add_clause(operator='eq', field=key, value=value)
        
        payload_builder.add_filter(filter_clause_builder)

    return payload_builder.payload