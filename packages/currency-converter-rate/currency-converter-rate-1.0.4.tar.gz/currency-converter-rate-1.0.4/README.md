# Currency Converter

A simple Python package for fetching real-time currency conversion rates to help the many developers issue and simply they can use it without using any third party resource


## Features

- Converts between any two currencies.
- Caches conversion rates for efficient subsequent requests.
- Handles various error cases such as invalid currency codes.

## Installation

You can install the package via pip:

```bash
pip install currency-converter-rate

```

## Usage
```bash

from currency.converter import conversion_rate

print(conversion_rate("USD",'PKR'))

```