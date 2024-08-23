

# Novum API Library

This library contains the basic api functions for [Novum Service Center](https://novum-batteries.com). 
Check some examples at [Novum - GitHub](https://github.com/novum-engineering/novum-cloud-api-examples)


## Installation

Use pip to install:

```shell
pip install novum_api_client
```

# Release Notes

## Version 3.0.0
- Release Date: 2024-08-19

### Enhancements
- Typing for NovumAPIClient Class
- Change typing structure of all entities into Optional, Reading, Writing and Essential
- Auxiliary methods to convert types
- New functions for timeseries data

# Changelog

## [2.0.1] - 2024-04-30
- Extended class arguments from base client.
- SSL_VERIFY optional for HTTP requests.
- Tests follow some order.


## [2.0.0] - 2024-04-29
- Added dataclass_json to easy the types.
- Rename types.
- Added Docstring.
- Rename functions "get_capacity_measurement" and "get_capacity_measurement_count".
- API Client available for Python > 3.8.1


## [1.1.1] - 2024-04-11
- Added new functions (get_user_documents and get_user_document_by_id).
- Forced typing for Reports.

## [1.0.1] - 2023-12-12
- Prettier added
- Most of the function have "fields" as an argument.
- Made Reports Section available. 
- Added Error/Exception messages.


## [1.0.0] - 2023-12-12
- First release of the library.