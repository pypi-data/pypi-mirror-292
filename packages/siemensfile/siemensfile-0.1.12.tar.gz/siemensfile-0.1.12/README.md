## Uso

Aquí un ejemplo básico de cómo usar SIEMENSFile:

```python
from siemensfile import process_siemens_file

# Procesar un archivo con reconstrucción Cartesiana
metadata, rawdata = process_siemens_file('ruta/a/tu/archivo.dat', reconstruction="Cartesiana")

# Procesar un archivo sin reconstrucción
metadata, rawdata = process_siemens_file('ruta/a/tu/archivo.dat')

# Trabajar con los resultados
print(metadata)
print(rawdata.shape)