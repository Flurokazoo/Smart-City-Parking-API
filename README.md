# Smart City Parking API (Iteration 1)

The Smart City Parking API is part of my graduation thesis. It gives users greater control over their Smart City Parking sensors. This is very much a prototype and a work in progress.

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

### Metadata

This is where all metadata is located. It contains the time the request was made and the status code:

    'metadata': {
        'status_code': 200,
        'current_timestamp': 1549531467,
        'current_date': '2019-02-07T10:24:27'
    }

### Pagination

Pagination is not included in all kinds of requests. Sometimes a method returns a lot of entries. To preserve fast loading, pagination is used. To access the next page of responses, simply call the 'next_url' parameter. Pagination takes into account your own set parameters.

    'pagination': {
        'next_url': 'URL to next page',
        'prev_url': 'URL to previous page
    }

## Endpoints

| Method    | Endpoint      | Returns                                                       |
| --------- | ------------- | --------------------------------------------------------------|
| GET       | /sectors      | A list of all sectors                                         |
| GET       | /sector/{id}  | Detailed data of a given sector                               |
| GET       | /history{id}  | Detailed history of a given sector                            |
| GET       | /distance     | List of sectors within certain distance from coordinates      |
| GET       | /grid         | List of sectors within bounds of given coordinates            |

### /sectors

This method yields a list of all sectors

#### Parameters

None

#### Response object

| Key                       | Value                                                                 |
|---------------------------|-----------------------------------------------------------------------|
| 'sector_id'               | The id of the sector                                                  |
| 'occupance_percentage'    | The occupance of a sector as a float (1 equals 100%)                  |
| 'timestamp'               | Timestamp of the last sensor measurement                              |
| 'date'                    | Date of the last request in ISO 8601 format                           |
| 'self_links'              | Object with links to both history and details of sector               |

### /sector{id}
