"""Casos de uso de registros, perfiles, estados, bitácora y parámetros (US1, US2, US8, RF-51).

Cada cambio se valida antes de tocar datos, se audita campo por campo con valor anterior,
valor nuevo, usuario, motivo, fecha efectiva e impacto en MAB y Forecast (FR-027, US8 esc. 1),
e incrementa la versión del registro (bloqueo optimista, FR-003).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from proyecta.application.ports import CambioAuditado
from proyecta.application.services.audit import ServicioAuditoria
from proyecta.application.use_cases.calculo import CalcularProyeccion
from proyecta.domain import states
from proyecta.domain.engine.service import ImpactoCalculo, ResultadoRegistro
from proyecta.domain.entities import (
    Bitacora,
    Contrato,
    EventoAuditoria,
    Parametro,
    Perfil,
    Registro,
    TarifaPerfil,
    Usuario,
    VigenciaEstadoCalculo,
    utcnow,
)
from proyecta.domain.enums import (
    BP_TOTAL,
    CONFIABILIDAD_INICIAL_BP,
    FLUJOS_POR_TIPO,
    PROBABILIDADES_VALIDAS_BP,
    CampoVigencia,
    EntidadAuditoria,
    Estado,
    Flujo,
    MotivoCierre,
    Rol,
    Tipo,
    TipoEventoBitacora,
    TipoParametro,
)
from proyecta.domain.errors import (
    ErrorConflicto,
    ErrorNoEncontrado,
    ErrorRango,
    ErrorValidacion,
    PermisoDenegado,
)
from proyecta.domain.value_objects import Period
from proyecta.infrastructure.memoria import Almacen

CAMPOS_EDITABLES = ("servicio_proyecto", "cliente_id", "sector_id", "manager_id", "modalidad", "studio",
                    "cuenta", "id_externo", "observaciones", "fecha_ingreso", "fecha_fin_vigencia",
                    "en_staffing", "en_invoicing")


def _a_texto(valor: Any) -> Any:
    """Valor serializable para la auditoría."""
    if valor is None or isinstance(valor, (int, str, bool)):
        return valor
    return getattr(valor, "value", None) or str(valor)


def _motivo(motivo: str | None) -> str:
    motivo = (motivo or "").strip()
    if not motivo:
        raise ErrorValidacion("MOTIVO_OBLIGATORIO", "Este cambio exige un motivo escrito.")
    if len(motivo) > 500:
        raise ErrorValidacion("VALIDACION", "El motivo admite hasta 500 caracteres.")
    return motivo


@dataclass
class ServicioRegistros:
    almacen: Almacen
    calculo: CalcularProyeccion
    auditoria: ServicioAuditoria

    # -- Apoyo -------------------------------------------------------------
    def obtener(self, registro_id: UUID) -> Registro:
        registro = self.almacen.registros.obtener(registro_id)
        if registro is None:
            raise ErrorNoEncontrado("NO_ENCONTRADO", "El registro no existe.")
        return registro

    def _editable(self, usuario: Usuario, registro: Registro, version: int | None) -> None:
        if not states.puede_editar(usuario.rol, usuario.id, registro):
            raise PermisoDenegado(message="Tu rol no permite modificar este registro.", accion="editar")
        if version is not None and version != registro.version:
            raise ErrorConflicto(
                "CONFLICTO_VERSION",
                "Otra persona guardó este registro mientras lo editabas. Revisa la versión vigente y vuelve a aplicar tu cambio.",
                detalle={"version_vigente": registro.version, "version_enviada": version},
            )

    def _resultado(self, registro_id: UUID) -> ResultadoRegistro:
        return self.calculo.calcular_registro(registro_id)

    def _auditar(self, usuario: Usuario, registro: Registro, cambios, antes: ResultadoRegistro, *,
                 motivo: str | None = None, fecha_efectiva: date | None = None,
                 entidad: EntidadAuditoria = EntidadAuditoria.REGISTRO, entidad_id: UUID | None = None,
                 prefijo: str = "") -> list[EventoAuditoria]:
        """Un evento por campo, todos con el impacto del cambio completo en MAB y Forecast."""
        if not cambios:
            return []
        registro.version += 1
        registro.actualizado_por = usuario.id
        registro.actualizado_en = utcnow()
        despues = self._resultado(registro.id)
        return [
            self.auditoria.registrar_cambio_de_calculo(
                entidad=entidad.value, entidad_id=entidad_id or registro.id, registro_id=registro.id,
                campo=prefijo + campo, valor_anterior=_a_texto(a), valor_nuevo=_a_texto(n),
                usuario_id=usuario.id, antes=antes, despues=despues, motivo=motivo, fecha_efectiva=fecha_efectiva,
            )
            for campo, a, n in cambios
        ]

    def _vigencia(self, usuario: Usuario, registro: Registro, campo: CampoVigencia, anterior: int,
                  nuevo: int, desde: date, motivo: str) -> None:
        """Historial mensual de P o C: el cambio rige desde su mes y no reescribe los anteriores (H-04)."""
        vigencias = self.almacen.vigencias
        inicio = Period.desde_fecha(registro.fecha_creacion).inicio
        if not any(v.vigente_desde <= inicio for v in vigencias.listar(registro.id, campo)):
            vigencias.guardar(VigenciaEstadoCalculo(registro_id=registro.id, campo=campo, valor_bp=anterior,
                                                    vigente_desde=inicio, motivo="Valor inicial", usuario_id=usuario.id))
        vigencias.guardar(VigenciaEstadoCalculo(registro_id=registro.id, campo=campo, valor_bp=nuevo,
                                                vigente_desde=Period.desde_fecha(desde).inicio, motivo=motivo,
                                                usuario_id=usuario.id))

    def perfiles_con_ingreso(self, registro_id: UUID) -> int:
        return sum(1 for p in self.almacen.perfiles.listar_por_registro(registro_id) if p.hc >= 1 and p.fecha_ingreso)

    # -- US1: crear y editar ----------------------------------------------
    def crear(self, usuario: Usuario, datos: dict[str, Any], perfiles: list[dict[str, Any]],
              contrato: dict[str, Any] | None = None) -> Registro:
        if usuario.rol is Rol.EJECUTIVO:
            raise PermisoDenegado(message="El rol Ejecutivo solo consulta.", accion="crear")
        tipo = Tipo(datos.get("tipo") or Tipo.OPORTUNIDAD)
        hoy = date.today()
        servicio = (datos.get("servicio_proyecto") or "").strip()
        errores = []
        if not servicio or len(servicio) > 200:
            errores.append("El servicio o proyecto es obligatorio (hasta 200 caracteres).")
        for campo, nombre in (("cliente_id", "cliente"), ("sector_id", "sector"), ("manager_id", "manager")):
            if not datos.get(campo):
                errores.append(f"El {nombre} es obligatorio.")
        perfiles_ok = [p for p in perfiles if p]
        if tipo is Tipo.DEMANDA and not perfiles_ok:
            errores.append("Una demanda directa requiere al menos un perfil (FR-007).")
        if tipo is Tipo.DEMANDA and not (datos.get("motivo") or "").strip():
            errores.append("Una demanda directa requiere el motivo de demanda directa (FR-007).")
        if tipo is Tipo.CONTINUIDAD and usuario.rol is not Rol.OPERACIONES:
            errores.append("Solo Operaciones registra continuidades (F3).")
        if tipo is Tipo.CONTINUIDAD and not (contrato and contrato.get("codigo_contrato")):
            errores.append("Una continuidad requiere la ficha de contrato (FR-008).")
        if errores:
            raise ErrorValidacion("VALIDACION", " ".join(errores), detalle={"errores": errores})

        owner = datos.get("owner_id") if usuario.rol is Rol.OPERACIONES and datos.get("owner_id") else usuario.id
        registro = Registro(
            codigo=self.almacen.registros.siguiente_codigo(), tipo=tipo,
            manager_id=datos["manager_id"], owner_id=owner, sector_id=datos["sector_id"],
            cliente_id=datos["cliente_id"], servicio_proyecto=servicio,
            observaciones=(datos.get("observaciones") or "").strip() or None,
            fecha_creacion=hoy, fecha_ingreso=datos.get("fecha_ingreso"),
            fecha_fin_vigencia=datos.get("fecha_fin_vigencia"), creado_por=usuario.id, actualizado_por=usuario.id,
        )
        if tipo is Tipo.DEMANDA:  # F2: nace adjudicada, flujo 3 a 5, P 100 %
            flujo = Flujo(datos.get("flujo") or Flujo.PROPUESTA_ENTREGADA)
            if not 3 <= flujo.orden <= 5:
                raise ErrorValidacion("VALIDACION", "Una demanda directa nace en el flujo 3, 4 o 5.")
            registro.estado, registro.flujo, registro.probabilidad_bp = Estado.ADJUDICADA, flujo, BP_TOTAL
            registro.fecha_adjudicacion = datos.get("fecha_adjudicacion") or hoy
        elif tipo is Tipo.CONTINUIDAD:  # F3: en curso, flujo 6, P y C 100 %
            registro.estado, registro.flujo = Estado.EN_CURSO, Flujo.PERFILES_SELECCIONADOS
            registro.probabilidad_bp = registro.confiabilidad_bp = BP_TOTAL
        else:  # F1: Pendiente, flujo 1, P 10 %, C 90 %
            registro.confiabilidad_bp = CONFIABILIDAD_INICIAL_BP

        nuevos = [self._perfil(registro, p, orden) for orden, p in enumerate(perfiles_ok, 1)]
        ficha = None
        if tipo is Tipo.CONTINUIDAD:
            ficha = Contrato(registro_id=registro.id, codigo_contrato=contrato["codigo_contrato"].strip(),
                             fecha_inicio=contrato.get("fecha_inicio") or hoy, fecha_fin=contrato.get("fecha_fin"),
                             es_indefinido=contrato.get("fecha_fin") is None,
                             monto_mensual_clp=contrato.get("monto_mensual_clp"),
                             hc_comprometido=contrato.get("hc_comprometido") or 0)
        # Todo validado: recién ahora se guarda (FR-004, sin guardado parcial).
        self.almacen.registros.guardar(registro)
        for perfil, tarifa in nuevos:
            self.almacen.perfiles.guardar(perfil)
            self.almacen.perfiles.guardar_tarifa(tarifa)
        if ficha:
            self.almacen.contratos.guardar(ficha)
        despues = self._resultado(registro.id)
        self.auditoria.registrar(
            _creacion(registro, usuario, len(nuevos), datos.get("motivo")),
            impacto=ImpactoCalculo(0, despues.total_mab(), 0, despues.total_forecast()),
        )
        return registro

    def _perfil(self, registro: Registro, datos: dict[str, Any], orden: int) -> tuple[Perfil, TarifaPerfil]:
        tarifa = datos.get("tarifa_hora_centavos") or 0
        if tarifa <= 0:
            raise ErrorRango("RANGO_INVALIDO", f"Perfil {orden}: la tarifa debe ser mayor que cero (RI-04).")
        ingreso = datos["fecha_ingreso"]
        if ingreso < registro.fecha_creacion and registro.tipo is not Tipo.CONTINUIDAD:
            raise ErrorRango("RANGO_INVALIDO",
                             f"Perfil {orden}: el ingreso no puede ser anterior a la creación del registro (RN-52).")
        try:
            perfil = Perfil(registro_id=registro.id, nombre_perfil_id=datos.get("nombre_perfil_id"),
                            hc=datos["hc"], dedicacion_pct=datos.get("dedicacion_pct") or 100,
                            fecha_ingreso=ingreso, fecha_fin=datos.get("fecha_fin"), orden=orden)
        except ErrorRango as error:
            raise ErrorRango("RANGO_INVALIDO", f"Perfil {orden}: {error.message} (RI-03).") from error
        return perfil, TarifaPerfil(perfil_id=perfil.id, tarifa_hora_centavos=tarifa, vigente_desde=ingreso)

    def editar(self, usuario: Usuario, registro_id: UUID, version: int, campos: dict[str, Any]) -> Registro:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        if registro.es_terminal:
            raise ErrorValidacion("VALIDACION", "Un registro cerrado o cancelado no se edita; Operaciones puede reabrirlo.")
        servicio = campos.get("servicio_proyecto")
        if servicio is not None and not (0 < len(servicio.strip()) <= 200):
            raise ErrorValidacion("VALIDACION", "El servicio o proyecto es obligatorio (hasta 200 caracteres).")
        ingreso = campos.get("fecha_ingreso", registro.fecha_ingreso)
        fin = campos.get("fecha_fin_vigencia", registro.fecha_fin_vigencia)
        if ingreso and fin and fin < ingreso:
            raise ErrorRango("RANGO_INVALIDO", "La fecha de fin no puede ser anterior a la de ingreso.")
        antes = self._resultado(registro.id)
        cambios = []
        for campo in CAMPOS_EDITABLES:
            if campo in campos:
                valor = campos[campo].strip() if isinstance(campos[campo], str) else campos[campo]
                if campo in ("observaciones", "id_externo") and valor == "":
                    valor = None
                if getattr(registro, campo) != valor:
                    cambios.append((campo, getattr(registro, campo), valor))
                    setattr(registro, campo, valor)
        self._auditar(usuario, registro, cambios, antes)
        return registro

    # -- Perfiles y tarifas (FR-011 a FR-013) ------------------------------
    def agregar_perfil(self, usuario: Usuario, registro_id: UUID, version: int, datos: dict[str, Any]) -> Perfil:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        if registro.es_terminal:
            raise ErrorValidacion("VALIDACION", "No se agregan perfiles a un registro cerrado (FR-011).")
        orden = len(self.almacen.perfiles.listar_por_registro(registro.id)) + 1
        perfil, tarifa = self._perfil(registro, datos, orden)
        antes = self._resultado(registro.id)
        self.almacen.perfiles.guardar(perfil)
        self.almacen.perfiles.guardar_tarifa(tarifa)
        self._auditar(usuario, registro, [("perfil", None, f"{perfil.hc} HC desde {perfil.fecha_ingreso:%d-%m-%Y}"),
                                          ("tarifa", None, tarifa.tarifa_hora_centavos)],
                      antes, entidad=EntidadAuditoria.PERFIL, entidad_id=perfil.id,
                      fecha_efectiva=perfil.fecha_ingreso, motivo=datos.get("motivo"))
        return perfil

    def editar_perfil(self, usuario: Usuario, registro_id: UUID, version: int, perfil_id: UUID,
                      datos: dict[str, Any], motivo: str | None) -> Perfil:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        perfil = self.almacen.perfiles.obtener(perfil_id)
        if perfil is None or perfil.registro_id != registro.id:
            raise ErrorNoEncontrado("NO_ENCONTRADO", "El perfil no existe en este registro.")
        nuevo = {k: datos.get(k, getattr(perfil, k)) for k in ("hc", "dedicacion_pct", "fecha_ingreso", "fecha_fin")}
        Perfil(**nuevo)  # valida rangos sin tocar el original
        if nuevo["hc"] != perfil.hc:
            motivo = _motivo(motivo)  # cambio de HC exige motivo (clarificación 2026-10-27)
        antes = self._resultado(registro.id)
        cambios = []
        for campo, valor in nuevo.items():
            if getattr(perfil, campo) != valor:
                cambios.append((campo, getattr(perfil, campo), valor))
                setattr(perfil, campo, valor)
        self._auditar(usuario, registro, cambios, antes, entidad=EntidadAuditoria.PERFIL, entidad_id=perfil.id,
                      motivo=motivo, prefijo=f"perfil {perfil.orden} · ")
        return perfil

    def quitar_perfil(self, usuario: Usuario, registro_id: UUID, version: int, perfil_id: UUID, motivo: str) -> None:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        motivo = _motivo(motivo)
        perfil = self.almacen.perfiles.obtener(perfil_id)
        if perfil is None or perfil.registro_id != registro.id:
            raise ErrorNoEncontrado("NO_ENCONTRADO", "El perfil no existe en este registro.")
        if registro.estado in (Estado.ADJUDICADA, Estado.EN_CURSO) and self.perfiles_con_ingreso(registro.id) <= 1:
            raise ErrorValidacion("VALIDACION", "Un registro adjudicado o en curso debe conservar al menos un perfil.")
        antes = self._resultado(registro.id)
        self.almacen.perfiles.quitar(perfil_id)
        self._auditar(usuario, registro, [(f"perfil {perfil.orden}", f"{perfil.hc} HC", None)], antes,
                      entidad=EntidadAuditoria.PERFIL, entidad_id=perfil.id, motivo=motivo)

    def nueva_tarifa(self, usuario: Usuario, registro_id: UUID, version: int, perfil_id: UUID,
                     centavos: int, desde: date, motivo: str) -> TarifaPerfil:
        """La nueva tarifa rige desde su mes; las anteriores no se reescriben (RI-06, RN-44)."""
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        motivo = _motivo(motivo)
        if centavos <= 0:
            raise ErrorRango("RANGO_INVALIDO", "La tarifa debe ser mayor que cero (RI-04).")
        perfil = self.almacen.perfiles.obtener(perfil_id)
        if perfil is None or perfil.registro_id != registro.id:
            raise ErrorNoEncontrado("NO_ENCONTRADO", "El perfil no existe en este registro.")
        historia = list(self.almacen.perfiles.tarifas_de(perfil.id))
        desde = Period.desde_fecha(desde).inicio
        if historia and desde <= historia[-1].vigente_desde:
            raise ErrorRango("RANGO_INVALIDO", "La nueva tarifa debe regir después de la última vigente (sin superposición).")
        antes = self._resultado(registro.id)
        if historia:
            historia[-1].vigente_hasta = desde
        tarifa = self.almacen.perfiles.guardar_tarifa(
            TarifaPerfil(perfil_id=perfil.id, tarifa_hora_centavos=centavos, vigente_desde=desde, motivo_cambio=motivo))
        anterior = historia[-1].tarifa_hora_centavos if historia else None
        self._auditar(usuario, registro, [(f"tarifa perfil {perfil.orden}", anterior, centavos)], antes,
                      entidad=EntidadAuditoria.TARIFA, entidad_id=tarifa.id, motivo=motivo, fecha_efectiva=desde)
        return tarifa

    # -- US2: estados, flujo, P y C ---------------------------------------
    def transicionar(self, usuario: Usuario, registro_id: UUID, version: int, destino: Estado, motivo: str,
                     fecha: date, motivo_cierre: MotivoCierre | None = None) -> Registro:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        antes = self._resultado(registro.id)
        probabilidad_antes = registro.probabilidad_bp
        cambios = states.transicionar(registro, destino, rol=usuario.rol, motivo=motivo, fecha=fecha,
                                      perfiles_con_ingreso=self.perfiles_con_ingreso(registro.id),
                                      motivo_cierre=motivo_cierre)
        if registro.probabilidad_bp != probabilidad_antes:
            self._vigencia(usuario, registro, CampoVigencia.PROBABILIDAD, probabilidad_antes,
                           registro.probabilidad_bp, fecha, motivo)
        self._registrar_bitacora(registro, usuario, TipoEventoBitacora.ESTADO,
                                 f"Cambio de estado a {destino.value.replace('_', ' ').capitalize()}: {motivo.strip()}")
        self._auditar(usuario, registro, cambios, antes, motivo=motivo.strip(), fecha_efectiva=fecha)
        return registro

    def cambiar_flujo(self, usuario: Usuario, registro_id: UUID, version: int, flujo: Flujo, motivo: str,
                      fecha: date) -> Registro:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        motivo = _motivo(motivo)
        if flujo not in FLUJOS_POR_TIPO[registro.tipo]:
            raise ErrorValidacion("VALIDACION", "Ese flujo no corresponde al tipo del registro.")
        antes = self._resultado(registro.id)
        probabilidad_antes = registro.probabilidad_bp
        cambios = states.cambiar_flujo(registro, flujo, perfiles_con_ingreso=self.perfiles_con_ingreso(registro.id))
        if registro.probabilidad_bp != probabilidad_antes:
            self._vigencia(usuario, registro, CampoVigencia.PROBABILIDAD, probabilidad_antes,
                           registro.probabilidad_bp, fecha, motivo)
        self._registrar_bitacora(registro, usuario, TipoEventoBitacora.ESTADO, f"Cambio de flujo: {motivo}")
        self._auditar(usuario, registro, cambios, antes, motivo=motivo, fecha_efectiva=fecha)
        return registro

    def cambiar_probabilidad(self, usuario: Usuario, registro_id: UUID, version: int, valor_bp: int,
                             desde: date, motivo: str) -> Registro:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, version)
        motivo = _motivo(motivo)
        if states.probabilidad_fija(registro):
            raise ErrorValidacion("VALIDACION", "La probabilidad está fija en 100 % en este estado (FR-020).")
        if registro.estado is not Estado.PENDIENTE:
            raise ErrorValidacion("VALIDACION", "Solo se ajusta la probabilidad de un registro Pendiente.")
        if valor_bp not in PROBABILIDADES_VALIDAS_BP or valor_bp == BP_TOTAL:
            raise ErrorRango("RANGO_INVALIDO", "La probabilidad debe ser un valor del catálogo (FR-028).")
        return self._cambiar_vigencia(usuario, registro, CampoVigencia.PROBABILIDAD, "probabilidad_bp",
                                      valor_bp, desde, motivo)

    def cambiar_confiabilidad(self, usuario: Usuario, registro_id: UUID, version: int, valor_bp: int,
                              desde: date, motivo: str) -> Registro:
        registro = self.obtener(registro_id)
        if usuario.rol is not Rol.OPERACIONES:
            raise PermisoDenegado(message="Solo Operaciones ajusta la confiabilidad (FR-026).", accion="confiabilidad")
        self._editable(usuario, registro, version)
        motivo = _motivo(motivo)
        if not 0 <= valor_bp <= BP_TOTAL:
            raise ErrorRango("RANGO_INVALIDO", "La confiabilidad va de 0 % a 100 %.")
        registro.motivo_confiabilidad = motivo
        return self._cambiar_vigencia(usuario, registro, CampoVigencia.CONFIABILIDAD, "confiabilidad_bp",
                                      valor_bp, desde, motivo)

    def _cambiar_vigencia(self, usuario, registro, campo_vigencia, atributo, valor_bp, desde, motivo):
        anterior = getattr(registro, atributo)
        antes = self._resultado(registro.id)
        self._vigencia(usuario, registro, campo_vigencia, anterior, valor_bp, desde, motivo)
        setattr(registro, atributo, valor_bp)
        self._auditar(usuario, registro, [(atributo, anterior, valor_bp)], antes, motivo=motivo,
                      fecha_efectiva=Period.desde_fecha(desde).inicio)
        return registro

    # -- Bitácora (US1 esc. 5) ---------------------------------------------
    def _registrar_bitacora(self, registro, usuario, tipo, contenido, proxima=None, compromiso=None):
        return self.almacen.bitacora.registrar(Bitacora(registro_id=registro.id, tipo_evento=tipo,
                                                        contenido=contenido, proxima_accion=proxima,
                                                        fecha_compromiso=compromiso, autor_id=usuario.id))

    def agregar_bitacora(self, usuario: Usuario, registro_id: UUID, tipo: TipoEventoBitacora, contenido: str,
                         proxima_accion: str | None, fecha_compromiso: date | None,
                         referencia_id: UUID | None = None) -> Bitacora:
        registro = self.obtener(registro_id)
        self._editable(usuario, registro, None)
        contenido = (contenido or "").strip()
        if not contenido or len(contenido) > 2000:
            raise ErrorValidacion("VALIDACION", "La entrada de bitácora es obligatoria (hasta 2.000 caracteres).")
        entrada = self._registrar_bitacora(registro, usuario, tipo, contenido,
                                           (proxima_accion or "").strip() or None, fecha_compromiso)
        entrada.referencia_id = referencia_id  # una corrección referencia la entrada anterior (F6)
        return entrada

    # -- Mantenedor de la MAB (RF-51): horas mensuales con vigencia --------
    def cambiar_horas(self, usuario: Usuario, horas: int, desde: date, motivo: str) -> Parametro:
        if usuario.rol is not Rol.OPERACIONES:
            raise PermisoDenegado(message="Solo Operaciones cambia los parámetros (FR-037).", accion="parametros")
        motivo = _motivo(motivo)
        if not 1 <= horas <= 744:
            raise ErrorRango("RANGO_INVALIDO", "Las horas mensuales deben estar entre 1 y 744.")
        desde = Period.desde_fecha(desde).inicio
        vigente = self.almacen.parametros.vigente("horas_mensuales", desde)
        antes = self.calculo.ejecutar()
        parametro = self.almacen.parametros.guardar(Parametro(clave="horas_mensuales", valor=horas,
                                                              tipo=TipoParametro.ENTERO, vigente_desde=desde,
                                                              usuario_id=usuario.id))
        despues = self.calculo.ejecutar()
        self.auditoria.registrar(
            _cambio_parametro(parametro, usuario, vigente.valor if vigente else None, motivo),
            impacto=ImpactoCalculo(antes.totales.mab_clp, despues.totales.mab_clp,
                                   antes.totales.forecast_clp, despues.totales.forecast_clp),
        )
        return parametro


def _creacion(registro: Registro, usuario: Usuario, perfiles: int, motivo: str | None):
    return CambioAuditado(
        entidad=EntidadAuditoria.REGISTRO.value, entidad_id=registro.id, registro_id=registro.id,
        campo="creacion", valor_anterior=None,
        valor_nuevo={"codigo": registro.codigo, "tipo": registro.tipo.value, "estado": registro.estado.value,
                     "flujo": registro.flujo.value, "probabilidad_bp": registro.probabilidad_bp,
                     "confiabilidad_bp": registro.confiabilidad_bp, "perfiles": perfiles},
        usuario_id=usuario.id, motivo=(motivo or "").strip() or None, fecha_efectiva=registro.fecha_creacion,
    )


def _cambio_parametro(parametro: Parametro, usuario: Usuario, anterior, motivo: str):
    return CambioAuditado(
        entidad=EntidadAuditoria.PARAMETRO.value, entidad_id=parametro.id, registro_id=parametro.id,
        campo="horas_mensuales", valor_anterior=anterior, valor_nuevo=parametro.valor,
        usuario_id=usuario.id, motivo=motivo, fecha_efectiva=parametro.vigente_desde,
    )
