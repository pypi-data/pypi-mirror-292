# pysophisthse
SophistHSE library ported to Python

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
                              AGR_M_DIRI AGR_M_DIRI_SA
T                                                     
2024-02-29 23:59:59.999999999       1100          3533
2024-03-31 23:59:59.999999999       1696          3557
2024-04-30 23:59:59.999999999       1903          3572
2024-05-31 23:59:59.999999999       2084          3580
2024-06-30 23:59:59.999999999       2132          3585
```
