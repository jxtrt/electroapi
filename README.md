# Electroapi
Simple, quick-to-use, public API to access Spanish electricity pricing.

## Functionalities

- `/areas`: Get a list of accepted areas, with redundant identifiers. List dug out from the original public code.
- `/today`: Fetch today's prices.
- `/schedule`: Given a number of hours of "power on", and an optional number of maximum consecutive blocks, returns the optimal schedule for a powered on appliance.
