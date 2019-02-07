# Smart City Parking API (Iteration 1)

The Smart City Parking API is part of my graduation thesis. It gives users greater control over their Smart City Parking sensors. This is very much a prototype and a work in progress.

## Response Structure

All responses are contained by an envelope. These are mostly the same among all methods. The envelope contains the following:

```json
'data': {
    ...
},
'metadata': {
    ...
},
'pagination': {
    ...
}
```

### Data

This is where the actual requested data is located.