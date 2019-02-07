# Smart City Parking API (Iteration 1)

The Smart City Parking API is part of my graduation thesis. It gives users greater control over their Smart City Parking sensors. This is very much a prototype and a work in progress.

##### Table of Contents  
## [Response Structure](#responsestructure)  
    [Data](#data)
    [Metadata](#metadata)
    [Pagination](#pagination)
## [Endpoints](#endpoints)
    [/sectors](#sectors)
    [/sector/{id}](#sector)
    [/history/{id}](#history)
    [/distance](#distance)
    [/grid](#grid)

<a name="responsestructure"/>

## Response Structure

All responses are contained by an envelope. These are mostly the same among all methods. The envelope contains the following:

    'data': {
        ...
    },
    'metadata': {
        ...
    },
    'pagination': {
        ...
    }

<a name="data"/>

### Data

This is where the actual requested data is located. The information contained depends on the method, but it usually looks like this:

    'data': [
        {
            'sector_id': 0,
            'occupance_percentage: 0.5,
            'timestamp': 1547643589,
            'date': '2019-01-16T13:59:49',
            ...
        },
        {
            'sector_id': 1,
            'occupance_percentage: 0.7,
            'timestamp': 1547643589,
            'date': '2019-01-16T13:59:49',
            ...
        },
    ]

<a name="metadata"/>

### Metadata

This is where all metadata is located. It contains the time the request was made and the status code:

    'metadata': {
        'status_code': 200,
        'current_timestamp': 1549531467,
        'current_date': '2019-02-07T10:24:27'
    }

<a name="pagination"/>

### Pagination

Pagination is not included in all kinds of requests. Sometimes a method returns a lot of entries. To preserve fast loading, pagination is used. To access the next page of responses, simply call the 'next_url' parameter. Pagination takes into account your own set parameters.

    'pagination': {
        'next_url': 'URL to next page',
        'prev_url': 'URL to previous page
    }

<a name="endpoints"/>

## Endpoints

| Method    | Endpoint      | Returns                                                       |
| --------- | ------------- | --------------------------------------------------------------|
| GET       | /sectors      | A list of all sectors                                         |
| GET       | /sector/{id}  | Detailed data of a given sector                               |
| GET       | /history{id}  | Detailed history of a given sector                            |
| GET       | /distance     | List of sectors within certain distance from coordinates      |
| GET       | /grid         | List of sectors within bounds of given coordinates            |

<a name="sectors"/>

## /sectors

This method yields a list of all sectors

### Path Parameters

None

### Query Parameters

None

### Response object

| Key                       | Value                                                                 |
|---------------------------|-----------------------------------------------------------------------|
| 'sector_id'               | The id of the sector                                                  |
| 'occupance_percentage'    | The occupance of a sector as a float (1 equals 100%)                  |
| 'timestamp'               | Timestamp of the last sensor measurement                              |
| 'date'                    | Date of the last request in ISO 8601 format                           |
| 'self_links'              | Object with links to both history and details of sector               |

<a name="sector"/>

## /sector/{id}

This method yields detailed data of a given sector

### Path Parameters

| Parameter | Value                                 |
|-----------|---------------------------------------|
| id        | _Required._ The id of the sector      |

### Query Parameters

None

### Response object

| Key                       | Value                                                                             |
|---------------------------|-----------------------------------------------------------------------------------|
| 'sector_id'               | The id of the sector                                                              |
| 'occupance_percentage'    | The occupance of a sector as a float (1 equals 100%)                              |
| 'timestamp'               | Timestamp of the last sensor measurement                                          |
| 'date'                    | Date of the last request in ISO 8601 format                                       |
| 'coordinates'             | Array of latitude and longitude objects containing the location of the sector     |
| 'sensors'                 | Array of objects containing the id and occupancy of specific sensors              |

<a name="history"/>

## /history/{id}

This method yields a detailed history of a given sector

### Path Parameters

| Parameter | Value                                 |
|-----------|---------------------------------------|
| id        | _Required._ The id of the sector      |

### Query Parameters

| Parameter         | Value                                                                                                 |
|-------------------|-------------------------------------------------------------------------------------------------------|
| limit             | _Optional._ Limits the total amount of returned entries to set number (over multiple pages)           |
| start             | _Optional._ UNIX Timestamp where the data should start                                                |
| end               | _Optional._ UNIX Timestamp where the data should end                                                  |
| interval          | _Optional._ The interval between measurements in seconds (defaults to 1 hour, minimum of 3 minutes)   |
| page              | _Optional._ Page of the data. New pages are generated in the response object                          |

### Response object

| Key                       | Value                                                                             |
|---------------------------|-----------------------------------------------------------------------------------|
| 'sector_id'               | The id of the sector                                                              |
| 'entries'                 | Array of objects including entries, containing the following responses:           |
| 'occupance_percentage'    | The occupance of a sector as a float (1 equals 100%)                              |
| 'average_percentage'      | The average occupance of the sector in the given interval                         |
| 'timestamp'               | Timestamp of the last sensor measurement in the given interval                    |
| 'date'                    | Date of the last request in ISO 8601 format for the given interval                |

<a name="responsestructure"/>

## /distance

This method yields a list of sectors within certain distance from coordinates

### Path Parameters

None

### Query Parameters

| Parameter         | Value                                                                                                 |
|-------------------|-------------------------------------------------------------------------------------------------------|
| latitude          | _Required._ Latitude coordinate for search point                                                      |
| longitude         | _Required._ Longitude coordinate for search point                                                     |
| range             | _Optional._ The range in meters to look for sectors (when not set, defaults to 500)                   |

### Response object

| Key                       | Value                                                                             |
|---------------------------|-----------------------------------------------------------------------------------|
| 'sector_id'               | The id of the sector                                                              |
| 'distance'                | The distance from the given coordinates to the sector in meters                   |
| 'occupance_percentage'    | The occupance of a sector as a float (1 equals 100%)                              |
| 'destination'             | Coordinates (latitude and longitude) to the target sector                         |

<a name="grid"/>

## /grid

This method yields a ist of sectors within bounds of given coordinates 

### Path Parameters

None

### Query Parameters

| Parameter         | Value                                                                                                                                                             |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| grid              | _Required._ A multidimensional array of latitude and longitude coordinates to compare to sector coordinates. Needs at least 3 latitude and longitude sets to work |

### Grid Parameter example:

Example array:

    [
        [51.910131,4.5320465],
        [51.9065121,4.544804],
        [51.9059752,4.5440652]
    ]

Example url:

'/grid?grid=[[51.910131,4.5320465],[51.9065121,4.544804],[51.9059752,4.5440652]]'

