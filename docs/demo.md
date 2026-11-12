# Demo con datos sintéticos (T165)

Contribución de Nicolás (backend/motor/IA). El guion final de la demo lo
coordina Alfredo; este documento cubre la preparación y reproducción de los
datos.

## Reglas

- **Solo datos sintéticos.** Clientes `Cliente Sintético NN`, correos
  `@example.test` y códigos `OPD-####`. Los cuatro registros reales no se
  migran en el MVP (`H-05`, `S-11`).
- **Nada de Datastore.** Los scripts generan JSON; la escritura real la hace
  la infraestructura cuando exista el emulador (T034).
- **Reproducible.** La misma semilla produce el mismo contenido.

## 1. Semilla amplia (1.000 registros)

```powershell
python scripts/seed_synthetic.py --cantidad 1000 --salida datos_sinteticos.json
```

Esperado:

```
Semilla de 1000 registros y ~1.700 perfiles -> datos_sinteticos.json
```

Incluye 12 sectores, 30 % multiperfil, 20 % con probabilidad intermedia,
10 % de continuidad y contratos, ajustes y vigencias sintéticas.

## 2. Fixture de cuatro registros (AC-14)

```powershell
python scripts/seed_synthetic.py --fixture four-records --salida fixture.json
```

Esperado:

```
Fixture de 4 registros (4 inconsistencias esperadas) -> fixture.json
```

Cada fila provoca una inconsistencia que el cargador **reporta sin corregir**:

| Fila | Código | Caso |
|---|---|---|
| 1 | `REGISTRO_CERRADO_CON_HC` | Registro cerrado por pérdida con HC activo |
| 2 | `PROBABILIDAD_FUERA_CATALOGO` | Probabilidad 3.333 bp fuera del catálogo |
| 3 | `FECHA_FUTURA` | `fecha_ingreso` posterior al período cargado |
| 4 | `ESTADO_TIPO_INCOHERENTE` | `ADJUDICADA` en una Oportunidad |

## 3. Carga en código

El caso de uso es `CargarEstructura` (`application/use_cases/carga.py`):

```python
from proyecta.application.use_cases.carga import CargarEstructura
from proyecta.seed.fixtures import cargar_fixture

fixture = cargar_fixture()
resultado = CargarEstructura(almacen).ejecutar(
    fixture.datos, periodo=fixture.periodo
)

resultado.creados          # 4
resultado.horas_mensuales  # 180
[f.codigo for f in resultado.inconsistencias]
```

La segunda ejecución devuelve `creados == 0` y `actualizados == 4`: la carga es
idempotente por `codigo`.

## 4. Guion sugerido para la pantalla

1. Mostrar la semilla de 1.000 registros y el dashboard con la serie de 12 meses.
2. Abrir el detalle de un registro: componentes, P, C, días activos y bolsa
   (MAB vs. Backlog).
3. Ejecutar el fixture de cuatro registros y mostrar el reporte de
   inconsistencias por fila.
4. Repetir la carga y mostrar que no se duplica nada.
5. Cerrar con la simulación aislada (US10), etiquetada como `simulado`.

## 5. Verificación

```powershell
python -m pytest tests/integration/test_seed.py -q
```

Cubre AC-14, idempotencia, ausencia de datos reales y recálculo a 180 h.
