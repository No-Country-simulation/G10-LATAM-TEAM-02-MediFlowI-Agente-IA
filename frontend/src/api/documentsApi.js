import api from "./axios";

const getBearerHeaders = () => {
  const rawSession = localStorage.getItem("mediflow_auth_session");
  const token = rawSession ? JSON.parse(rawSession).access_token : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Initial mock database stored in localStorage for offline/development testing
const INITIAL_DOCUMENTS = [
  {
    documento_id: "DOC-001",
    nombre_archivo: "receta001.pdf",
    canal_origen: "Consulta Externa",
    fecha_creacion: "2026-09-20T10:30:00Z",
    estado: "PROCESADO",
    clasificacion: {
      tipo_documento: "Receta Médica",
      especialidad: "Medicina General",
      prioridad: "NORMAL",
      score_confianza: 0.94
    },
    datos_extraidos: {
      paciente: {
        nombre: "Juan Pérez",
        dni: "45879632",
        edad: 45
      },
      medico: {
        nombre: "Carlos Ramos",
        cmp: "45872"
      },
      diagnostico: "Hipertensión arterial",
      cie10: "I10",
      medicamentos: [
        {
          nombre: "Losartán",
          dosis: "50 mg",
          frecuencia: "Cada 24 horas"
        }
      ],
      estudio_solicitado: null
    },
    texto_ocr: `HOSPITAL CLINICO CENTRAL\nFecha: 20/09/2026\n\nPaciente: Juan Pérez\nDNI: 45879632\nEdad: 45 años\n\nMédico Tratante: Dr. Carlos Ramos\nCMP: 45872\n\nDiagnóstico Presuntivo:\nHipertensión arterial (CIE-10: I10)\n\nRP/\n1. Losartán 50 mg - Tomar 1 tableta cada 24 horas por 30 días.\n\nFirma y Sello del Médico`,
    decision_enrutamiento: {
      destino: "FARMACIA",
      requiere_auditoria: false,
      motivo_auditoria: null
    }
  },
  {
    documento_id: "DOC-002",
    nombre_archivo: "informe_urgente.pdf",
    canal_origen: "Emergencia",
    fecha_creacion: "2026-09-20T11:15:00Z",
    estado: "PROCESADO",
    clasificacion: {
      tipo_documento: "Informe Médico",
      especialidad: "Cardiología",
      prioridad: "URGENTE",
      score_confianza: 0.98
    },
    datos_extraidos: {
      paciente: {
        nombre: "Ana Pérez",
        dni: "71234567",
        edad: 62
      },
      medico: {
        nombre: "Dra. Sofía Mendoza",
        cmp: "51204"
      },
      diagnostico: "Síndrome Coronario Agudo",
      cie10: "I24.9",
      medicamentos: [
        {
          nombre: "Aspirina",
          dosis: "100 mg",
          frecuencia: "Inmediata"
        },
        {
          nombre: "Clopidogrel",
          dosis: "75 mg",
          frecuencia: "Cada 24 horas"
        }
      ],
      estudio_solicitado: "Electrocardiograma urgente & Enzimas cardíacas"
    },
    texto_ocr: `SERVICIO DE EMERGENCIA CARDIOVASCULAR\nFecha: 20/09/2026\n\nPaciente: Ana Pérez\nDNI: 71234567\nEdad: 62 años\n\nMédico: Dra. Sofía Mendoza CMP: 51204\n\nCuadro Clínico:\nDolor torácico opresivo de 2 horas de evolución.\nDiagnóstico: Síndrome Coronario Agudo (I24.9)\nPrioridad: URGENTE\n\nRP/ Aspirina 100 mg STAT, Clopidogrel 75mg q24h.\nEstudio: ECG urgente y enzimas cardíacas.`,
    decision_enrutamiento: {
      destino: "EMERGENCIA / CARDIOLOGÍA",
      requiere_auditoria: false,
      motivo_auditoria: null
    }
  },
  {
    documento_id: "DOC-003",
    nombre_archivo: "orden_ambigua.jpg",
    canal_origen: "Hospitalización",
    fecha_creacion: "2026-09-20T09:45:00Z",
    estado: "AUDITORIA",
    clasificacion: {
      tipo_documento: "Orden Médica",
      especialidad: "Medicina General",
      prioridad: "PRIORITARIO",
      score_confianza: 0.52
    },
    datos_extraidos: {
      paciente: {
        nombre: "Juan Perez",
        dni: "4587?932",
        edad: null
      },
      medico: {
        nombre: "Dr. Desconocido",
        cmp: null
      },
      diagnostico: "HTA",
      cie10: null,
      medicamentos: [],
      estudio_solicitado: "Ecografía abdominal"
    },
    texto_ocr: `ORDEN MEDICA\nFecha: 20/09/2026\n\nPaciente: Juan Perez\nDNI: 4587?932 (ilegible)\nDx: HTA\n\nSolicito: Ecografía abdominal\n\nFirma ilegible`,
    decision_enrutamiento: {
      destino: "AUDITORÍA HUMANA",
      requiere_auditoria: true,
      motivo_auditoria: "Datos ilegibles en DNI y firma médica no identificada"
    }
  }
];

const getStoredDocuments = () => {
  const data = localStorage.getItem("mediflow_documents");
  if (!data) {
    localStorage.setItem("mediflow_documents", JSON.stringify(INITIAL_DOCUMENTS));
    return INITIAL_DOCUMENTS;
  }
  try {
    return JSON.parse(data);
  } catch (e) {
    return INITIAL_DOCUMENTS;
  }
};

const saveStoredDocuments = (docs) => {
  localStorage.setItem("mediflow_documents", JSON.stringify(docs));
};

const normalizeBackendDocument = (item) => {
  const clasif = item.clasificacion || {}
  const datos = item.datos_extraidos || {}
  const decision = item.decision_enrutamiento || {}

  const scoreConf =
    clasif.score_confianza_clasificacion !== undefined
      ? clasif.score_confianza_clasificacion
      : clasif.score_confianza !== undefined
      ? clasif.score_confianza
      : 0.9

  const rawPrio = (clasif.nivel_prioridad || clasif.prioridad || "RUTINA").toUpperCase()
  const prio = rawPrio === "RUTINA" ? "NORMAL" : rawPrio === "URGENTE" ? "URGENTE" : rawPrio === "AMBIGUO" ? "PRIORITARIO" : rawPrio

  const rawStatus = (item.status || item.estado || "PROCESADO").toUpperCase()
  const estadoNorm = rawStatus === "PENDIENTE_AUDITORIA" ? "AUDITORIA" : rawStatus

  const destinoNorm = (decision.destino_principal || decision.destino || "Cola_Rutina")
    .replace(/_/g, " ")
    .replace("Cola ", "")

  return {
    documento_id: item.documento_id,
    nombre_archivo: item.nombre_archivo || `${item.documento_id}.pdf`,
    canal_origen: item.canal_origen || "Sistema",
    fecha_creacion: item.created_at || item.fecha_creacion || new Date().toISOString(),
    estado: estadoNorm,
    clasificacion: {
      tipo_documento: clasif.tipo_documento || "Informe Clínico",
      especialidad: clasif.especialidad || "Medicina General",
      prioridad: prio,
      score_confianza: scoreConf,
    },
    datos_extraidos: {
      paciente: {
        nombre: datos.paciente?.nombre || "Paciente Clínico",
        dni: datos.paciente?.dni || "-",
        edad: datos.paciente?.edad || null,
      },
      medico: {
        nombre: datos.medico_solicitante?.nombre || datos.medico?.nombre || "-",
        cmp: datos.medico_solicitante?.matricula || datos.medico?.cmp || "-",
      },
      diagnostico: datos.diagnostico_principal || datos.diagnostico || "-",
      cie10: datos.cie10_sugerido || datos.cie10 || "-",
      medicamentos: datos.medicamentos || [],
      estudio_solicitado: datos.hallazgos_clave ? datos.hallazgos_clave.join(", ") : null,
    },
    texto_ocr: item.texto_ocr || "Documento procesado por Agente IA MediFlow",
    decision_enrutamiento: {
      destino: destinoNorm,
      requiere_auditoria: decision.requiere_auditoria_humana || decision.requiere_auditoria || false,
      motivo_auditoria: decision.justificacion_enrutamiento || decision.motivo_auditoria || null,
    },
  }
}

export const documentsApi = {
  // POST /api/documentos/procesar
  procesarDocumento: async (file, canalOrigen) => {
    const formData = new FormData();
    formData.append("archivo", file);
    formData.append("canalOrigen", canalOrigen || "Otro");

    try {
      const response = await api.post("/documentos/procesar", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return response.data;
    } catch (error) {
      console.warn("Backend real no disponible. Simulando respuesta de procesamiento.", error);
      
      const docs = getStoredDocuments();
      const newIdNumber = docs.length + 1;
      const docId = `DOC-${String(newIdNumber).padStart(3, "0")}`;
      
      const fileNameLower = file.name.toLowerCase();
      const isUrgent = fileNameLower.includes("urgente") || canalOrigen === "Emergencia";
      const isAmbiguous = fileNameLower.includes("borroso") || fileNameLower.includes("ambiguo") || file.name.endsWith(".png");

      let confidence = isAmbiguous ? 0.55 : isUrgent ? 0.96 : 0.92;
      let priority = isUrgent ? "URGENTE" : "NORMAL";
      let requiereAuditoria = confidence < 0.60;
      let estado = requiereAuditoria ? "AUDITORIA" : "PROCESADO";
      let destino = requiereAuditoria ? "AUDITORÍA HUMANA" : isUrgent ? "EMERGENCIA" : "CONSULTA EXTERNA";

      const newDoc = {
        documento_id: docId,
        nombre_archivo: file.name,
        canal_origen: canalOrigen || "Consulta Externa",
        fecha_creacion: new Date().toISOString(),
        estado: estado,
        clasificacion: {
          tipo_documento: file.name.endsWith(".pdf") ? "Informe Clínico" : "Receta Médica",
          especialidad: isUrgent ? "Emergenciología" : "Medicina General",
          prioridad: priority,
          score_confianza: confidence
        },
        datos_extraidos: {
          paciente: {
            nombre: "Carlos Gómez",
            dni: "44556677",
            edad: 38
          },
          medico: {
            nombre: "Dr. Mario Fuentes",
            cmp: "38921"
          },
          diagnostico: isUrgent ? "Insuficiencia Respiratoria Aguda" : "Bronquitis Aguda",
          cie10: isUrgent ? "J96.0" : "J20.9",
          medicamentos: [
            {
              nombre: isUrgent ? "Salbutamol Inhalador" : "Amoxicilina",
              dosis: isUrgent ? "100 mcg" : "500 mg",
              frecuencia: isUrgent ? "Cada 4 horas" : "Cada 8 horas"
            }
          ],
          estudio_solicitado: isUrgent ? "Radiografía de Tórax AP" : null
        },
        texto_ocr: `MEDIFLOW CLINIC\nDocumento: ${file.name}\nCanal: ${canalOrigen}\n\nPaciente: Carlos Gómez (DNI: 44556677, Edad: 38)\nMédico: Dr. Mario Fuentes (CMP: 38921)\n\nDx: ${isUrgent ? "Insuficiencia Respiratoria Aguda" : "Bronquitis Aguda"}\nIndicaciones y tratamiento prescrito.`,
        decision_enrutamiento: {
          destino: destino,
          requiere_auditoria: requiereAuditoria,
          motivo_auditoria: requiereAuditoria ? "Score de confianza inferior al umbral mínimo (60%)" : null
        }
      };

      docs.unshift(newDoc);
      saveStoredDocuments(docs);

      return newDoc;
    }
  },

  // GET /api/v1/documents
  obtenerDocumentos: async (filtros = {}) => {
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const res = await fetch(`${API_BASE}/documents`, {
        headers: {
          'Content-Type': 'application/json',
          ...getBearerHeaders(),
        },
      });

      if (res.ok) {
        const data = await res.json();
        const rawItems = data.items || (Array.isArray(data) ? data : []);
        if (rawItems.length > 0) {
          let docs = rawItems.map(normalizeBackendDocument);

          if (filtros.estado) {
            docs = docs.filter(d => d.estado.toUpperCase() === filtros.estado.toUpperCase());
          }
          if (filtros.tipo) {
            docs = docs.filter(d => d.clasificacion.tipo_documento.toLowerCase().includes(filtros.tipo.toLowerCase()));
          }
          if (filtros.prioridad) {
            docs = docs.filter(d => d.clasificacion.prioridad.toUpperCase() === filtros.prioridad.toUpperCase());
          }
          if (filtros.paciente) {
            const p = filtros.paciente.toLowerCase();
            docs = docs.filter(d => (d.datos_extraidos?.paciente?.nombre || "").toLowerCase().includes(p) || (d.datos_extraidos?.paciente?.dni || "").includes(p));
          }
          return docs;
        }
      }
    } catch (error) {
      console.warn("Backend real no disponible o error al consultar /api/v1/documents:", error);
    }

    let docs = getStoredDocuments();
    if (filtros.estado) {
      docs = docs.filter(d => d.estado.toUpperCase() === filtros.estado.toUpperCase());
    }
    if (filtros.tipo) {
      docs = docs.filter(d => d.clasificacion.tipo_documento.toLowerCase().includes(filtros.tipo.toLowerCase()));
    }
    if (filtros.prioridad) {
      docs = docs.filter(d => d.clasificacion.prioridad.toUpperCase() === filtros.prioridad.toUpperCase());
    }
    if (filtros.paciente) {
      const p = filtros.paciente.toLowerCase();
      docs = docs.filter(d => (d.datos_extraidos?.paciente?.nombre || "").toLowerCase().includes(p) || (d.datos_extraidos?.paciente?.dni || "").includes(p));
    }
    return docs;
  },

  // GET /api/v1/documents/{id}
  obtenerDocumentoPorId: async (id) => {
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const res = await fetch(`${API_BASE}/documents/${id}`, {
        headers: {
          'Content-Type': 'application/json',
          ...getBearerHeaders(),
        },
      });

      if (res.ok) {
        const item = await res.json();
        return normalizeBackendDocument(item);
      }
    } catch (error) {
      console.warn(`Error al consultar documento ${id} desde backend real:`, error);
    }

    const docs = getStoredDocuments();
    const doc = docs.find(d => d.documento_id === id);
    if (!doc) {
      throw new Error(`Documento con ID ${id} no encontrado.`);
    }
    return doc;
  },

  // GET /api/v1/dashboard/resumen
  obtenerResumenDashboard: async () => {
    try {
      const docs = await documentsApi.obtenerDocumentos();
      const procesados = docs.filter(d => d.estado === "PROCESADO").length;
      const urgentes = docs.filter(d => d.clasificacion?.prioridad === "URGENTE").length;
      const auditoria = docs.filter(d => d.estado === "AUDITORIA" || d.decision_enrutamiento?.requiere_auditoria).length;
      const errores = docs.filter(d => d.estado === "ERROR" || d.estado === "RECHAZADO").length;

      return {
        procesados: procesados || docs.length,
        urgentes: urgentes,
        auditoria: auditoria,
        errores: errores,
        recientes: docs.slice(0, 5)
      };
    } catch (error) {
      console.warn("Error al calcular resumen de dashboard:", error);
      const docs = getStoredDocuments();
      return {
        procesados: docs.filter(d => d.estado === "PROCESADO").length,
        urgentes: docs.filter(d => d.clasificacion?.prioridad === "URGENTE").length,
        auditoria: docs.filter(d => d.estado === "AUDITORIA").length,
        errores: docs.filter(d => d.estado === "ERROR").length,
        recientes: docs.slice(0, 5)
      };
    }
  }
};
