[![Python package](https://github.com/AlekseiPrishchepo/pysophisthse/actions/workflows/python-package.yml/badge.svg)](https://github.com/AlekseiPrishchepo/pysophisthse/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/AlekseiPrishchepo/pysophisthse/actions/workflows/python-publish.yml/badge.svg)](https://github.com/AlekseiPrishchepo/pysophisthse/actions/workflows/python-publish.yml)

# sophisthse

**sophisthse** is a Python library that is a port of the `sophisthse` R package. This library allows you to download timeseries of macroeconomic statistics of the Russian Federation from [sophist.hse.ru](http://sophist.hse.ru/hse/nindex.shtml). The data is provided by HSE (Higher School of Economics), which is a leading national research university with expertise in STEM, socio-economic and humanitarian areas, as well as creative industries.

## Installation

```bash
pip3 install sophisthse
```

## Usage

### Get available tables

```python
from sophisthse import sophisthse

sp = sophisthse()
tables = sp.list_tables()
print(tables.head())
```

```
                 date            name
0 2020-05-27 15:46:00  AGR_M_I - Copy
1 2024-08-08 09:10:00         AGR_M_I
2 2024-08-08 09:10:00         AGR_Q_I
3 2024-02-11 19:10:00      AGR_Y_DIRI
4 2024-07-26 20:04:00          APCI3N
```

### Get specific table

```python
sp = sophisthse(to_timestamp=True, verbose=False)
df = sp.get_table("AGR_M_I")
print(df.tail())
```

```
                               HHI_M_DIRI  HHI_M_DIRI_SA    HHI_M
T                                                                
2018-09-30 23:59:59.999999999       184.1          187.5  31698.0
2018-10-31 23:59:59.999999999       190.9          187.9  32962.0
2018-11-30 23:59:59.999999999       183.3          188.6  32282.0
2018-12-31 23:59:59.999999999       279.1          189.6  47673.0
2019-01-31 23:59:59.999999999       139.6          190.7  24496.0
```
