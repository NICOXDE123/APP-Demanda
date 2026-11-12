"""Dobles de prueba en memoria para los casos de uso (sin Datastore).

Viven en ``tests/integration`` para que las pruebas de Nicolás no dependan del
``conftest.py`` de la fundación (T009).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Sequence
from uuid import UUID

from proyecta.domain.entities import (
    AjusteHC,
    Bitacora,
    Contrato,
    EventoAuditoria,
    MetaComercial,
    Parametro,
    Perfil,
    Registro,
    SugerenciaIA,
    TarifaPerfil,
    VigenciaEstadoCalculo,
)


def _coincide(valor: Any, filtros: Sequence[Any] | None) -> bool:
    if not filtros:
        return True
    codigos = {getattr(filtro, "value", filtro) for filtro in filtros}
    return getattr(valor, "value", valor) in codigos


class RelojFijo:
    def __init__(self, momento: datetime | None = None) -> None:
        self.momento = momento or datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

    def ahora(self) -> datetime:
        return self.momento

    def hoy(self) -> date:
        return self.momento.date()


class FakeRepositorioRegistros:
    def __init__(self, registros: Sequence[Registro] = ()) -> None:
        self._datos = {registro.id: registro for registro in registros}
        self.guardados: list[Registro] = []

    def obtener(self, registro_id: UUID) -> Registro | None:
        return self._datos.get(registro_id)

    def listar(
        self,
        *,
        owner_id: UUID | None = None,
        sector_id: UUID | None = None,
        tipos: Sequence[Any] | None = None,
        estados: Sequence[Any] | None = None,
        codigos: Sequence[str] | None = None,
        limite: int | None = None,
    ) -> Sequence[Registro]:
        resultado = [
            registro
            for registro in self._datos.values()
            if (owner_id is None or registro.owner_id == owner_id)
            and (sector_id is None or registro.sector_id == sector_id)
            and _coincide(registro.tipo, tipos)
            and _coincide(registro.estado, estados)
            and (not codigos or registro.codigo in codigos)
        ]
        resultado.sort(key=lambda registro: registro.codigo)
        return resultado[:limite] if limite else resultado

    def guardar(self, registro: Registro) -> Registro:
        self.guardados.append(registro)
        self._datos[registro.id] = registro
        return registro


class FakeRepositorioPerfiles:
    def __init__(
        self,
        perfiles: Sequence[Perfil] = (),
        tarifas: Sequence[TarifaPerfil] = (),
        ajustes: Sequence[AjusteHC] = (),
    ) -> None:
        self.perfiles = list(perfiles)
        self._tarifas: dict[UUID, list[TarifaPerfil]] = {}
        for tarifa in tarifas:
            if tarifa.perfil_id is not None:
                self._tarifas.setdefault(tarifa.perfil_id, []).append(tarifa)
        self._ajustes = list(ajustes)
        self.guardados: list[Perfil] = []

    def listar_por_registro(self, registro_id: UUID) -> Sequence[Perfil]:
        return [perfil for perfil in self.perfiles if perfil.registro_id == registro_id]

    def tarifas_de(self, perfil_id: UUID) -> Sequence[TarifaPerfil]:
        return self._tarifas.get(perfil_id, [])

    def ajustes_de(self, registro_id: UUID) -> Sequence[AjusteHC]:
        return [ajuste for ajuste in self._ajustes if ajuste.registro_id == registro_id]

    def guardar(self, perfil: Perfil) -> Perfil:
        self.guardados.append(perfil)
        self.perfiles.append(perfil)
        return perfil

    def guardar_tarifa(self, tarifa: TarifaPerfil) -> TarifaPerfil:
        self._tarifas.setdefault(tarifa.perfil_id, []).append(tarifa)
        return tarifa

    def guardar_ajuste(self, ajuste: AjusteHC) -> AjusteHC:
        self._ajustes.append(ajuste)
        return ajuste


class FakeRepositorioContratos:
    def __init__(self, contratos: Sequence[Contrato] = ()) -> None:
        self._datos = {contrato.registro_id: contrato for contrato in contratos}

    def obtener_por_registro(self, registro_id: UUID) -> Contrato | None:
        return self._datos.get(registro_id)

    def listar(self) -> Sequence[Contrato]:
        return list(self._datos.values())

    def guardar(self, contrato: Contrato) -> Contrato:
        self._datos[contrato.registro_id] = contrato
        return contrato


class FakeRepositorioParametros:
    def __init__(self, parametros: Sequence[Parametro] = ()) -> None:
        self._datos = list(parametros)

    def listar(self, clave: str | None = None) -> Sequence[Parametro]:
        return [p for p in self._datos if clave is None or p.clave == clave]

    def vigente(self, clave: str, mes: date) -> Parametro | None:
        candidatos = [
            p
            for p in self._datos
            if p.clave == clave
            and p.vigente_desde <= mes
            and (p.vigente_hasta is None or p.vigente_hasta >= mes)
        ]
        return max(candidatos, key=lambda p: p.vigente_desde) if candidatos else None


class FakeRepositorioVigencias:
    def __init__(self, vigencias: Sequence[VigenciaEstadoCalculo] = ()) -> None:
        self._datos = list(vigencias)

    def listar(self, registro_id: UUID, campo=None) -> Sequence[VigenciaEstadoCalculo]:
        return [
            vigencia
            for vigencia in self._datos
            if vigencia.registro_id == registro_id and (campo is None or vigencia.campo is campo)
        ]

    def listar_todas(self) -> Sequence[VigenciaEstadoCalculo]:
        return list(self._datos)

    def guardar(self, vigencia: VigenciaEstadoCalculo) -> VigenciaEstadoCalculo:
        self._datos.append(vigencia)
        return vigencia


class FakeRepositorioMetas:
    def __init__(self, metas: Sequence[MetaComercial] = ()) -> None:
        self._datos = list(metas)

    def obtener(self, sector_id: UUID, mes: date) -> MetaComercial | None:
        for meta in self._datos:
            if meta.sector_id == sector_id and meta.mes == mes:
                return meta
        return None

    def listar(self, *, sector_id: UUID | None = None) -> Sequence[MetaComercial]:
        return [meta for meta in self._datos if sector_id is None or meta.sector_id == sector_id]


class FakeRepositorioBitacora:
    def __init__(self, entradas: Sequence[Bitacora] = ()) -> None:
        self._datos = list(entradas)
        self.registradas: list[Bitacora] = []

    def listar_por_registro(self, registro_id: UUID) -> Sequence[Bitacora]:
        return [entrada for entrada in self._datos if entrada.registro_id == registro_id]

    def registrar(self, entrada: Bitacora) -> Bitacora:
        self._datos.append(entrada)
        self.registradas.append(entrada)
        return entrada


class FakeRepositorioAuditoria:
    def __init__(self) -> None:
        self.eventos: list[EventoAuditoria] = []

    def listar_por_registro(self, registro_id: UUID) -> Sequence[EventoAuditoria]:
        return [evento for evento in self.eventos if evento.registro_id == registro_id]

    def registrar(self, evento: EventoAuditoria) -> EventoAuditoria:
        self.eventos.append(evento)
        return evento


class FakeRepositorioSugerencias:
    def __init__(self, sugerencias: Sequence[SugerenciaIA] = ()) -> None:
        self._datos = {sugerencia.id: sugerencia for sugerencia in sugerencias}
        self.guardadas: list[SugerenciaIA] = []

    def listar_pendientes(self) -> Sequence[SugerenciaIA]:
        return [s for s in self._datos.values() if s.estado.value == "PENDIENTE"]

    def obtener(self, sugerencia_id: UUID) -> SugerenciaIA | None:
        return self._datos.get(sugerencia_id)

    def guardar(self, sugerencia: SugerenciaIA) -> SugerenciaIA:
        self._datos[sugerencia.id] = sugerencia
        self.guardadas.append(sugerencia)
        return sugerencia
