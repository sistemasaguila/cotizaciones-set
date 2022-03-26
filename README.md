# cotizaciones-set
Api de cotizaciones basados en los datos publicados por la Subsecretaría de Estado de Tributación (SET)

[![](https://data.jsdelivr.com/v1/package/gh/sistemasaguila/cotizaciones-set/badge)](https://www.jsdelivr.com/package/gh/sistemasaguila/cotizaciones-set)
[![Update rates](https://github.com/sistemasaguila/cotizaciones-set/actions/workflows/run.yml/badge.svg)](https://github.com/sistemasaguila/cotizaciones-set/actions/workflows/run.yml)


## Estructura de URL

```
https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/{year}/{month}/{day}/rates.json
```

## Uso

### Recuperar cotizaciones de una fecha

Url: [https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/23/rates.json](https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/23/rates.json "https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/23/rates.json")

#### Respuesta

```json
{
  "2022-03-23": {
    "usd": {
      "purchase": 6957.05,
      "sale": 6965.87
    },
    "brl": {
      "purchase": 1431.93,
      "sale": 1434.04
    },
    ...
  }
}
```

### Recuperar cotizaciones de todo un mes

Url: [https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/rates.json](https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/rates.json "https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/03/rates.json")

#### Respuesta

```json
{
  "2022-03-01": {
    "usd": {
      "purchase": 6960.72,
      "sale": 6965.55
    },
    "brl": {
      "purchase": 1350.91,
      "sale": 1352.06
    },
    ...
  },
  "2022-03-02": {
    "usd": {
      "purchase": 6953.07,
      "sale": 6974.68
    },
    ...
  }
}
```

### Recuperar cotizaciones de todo un año

Url: [https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/rates.json](https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/rates.json "https://cdn.jsdelivr.net/gh/sistemasaguila/cotizaciones-set@main/data/2022/rates.json")

#### Respuesta

```json
{
  "2022-01-01": {
    "usd": {
      "purchase": 6870.81,
      "sale": 6887.4
    },
    "brl": {
      "purchase": 1227.68,
      "sale": 1230.82
    },
    ...
  },
  "2022-01-02": {
    "usd": {
      "purchase": 6870.81,
      "sale": 6887.4
    },
    "brl": {
      "purchase": 1227.68,
      "sale": 1230.82
    },
    ...
  }
}
```