import api from "./axios";

const getStoredDocuments = () => {
  const data = localStorage.getItem("mediflow_documents");
  if (!data) return [];
  try {
    return JSON.parse(data);
  } catch (e) {
    return [];
  }
};

const saveStoredDocuments = (docs) => {
  localStorage.setItem("mediflow_documents", JSON.stringify(docs));
};

export const auditApi = {
  // GET /api/auditoria
  obtenerAuditorias: async () => {
    try {
      const response = await api.get("/auditoria");
      return response.data;
    } catch (error) {
      console.warn("Backend real no disponible. Obteniendo lista de auditorías desde mock.", error);
      const docs = getStoredDocuments();
      return docs.filter(
        d => d.estado === "AUDITORIA" || d.decision_enrutamiento?.requiere_auditoria || d.clasificacion?.score_confianza < 0.60
      );
    }
  },

  // GET /api/auditoria/{id}
  obtenerAuditoriaPorId: async (id) => {
    try {
      const response = await api.get(`/auditoria/${id}`);
      return response.data;
    } catch (error) {
      console.warn(`Backend real no disponible. Obteniendo auditoría ${id} desde mock.`, error);
      const docs = getStoredDocuments();
      const doc = docs.find(d => d.documento_id === id);
      if (!doc) {
        throw new Error(`Documento de auditoría ${id} no encontrado.`);
      }
      return doc;
    }
  },

  // PUT /api/auditoria/{id}/aprobar
  aprobarAuditoria: async (id) => {
    try {
      const response = await api.put(`/auditoria/${id}/aprobar`);
      return response.data;
    } catch (error) {
      console.warn(`Backend real no disponible. Aprobando auditoría ${id} en mock.`, error);
      const docs = getStoredDocuments();
      const index = docs.findIndex(d => d.documento_id === id);
      if (index !== -1) {
        docs[index].estado = "PROCESADO";
        docs[index].decision_enrutamiento.requiere_auditoria = false;
        docs[index].decision_enrutamiento.motivo_auditoria = "Aprobado por auditoría humana";
        saveStoredDocuments(docs);
        return docs[index];
      }
      throw new Error("Documento no encontrado");
    }
  },

  // PUT /api/auditoria/{id}/rechazar
  rechazarAuditoria: async (id, motivo = "Rechazado en revisión humana") => {
    try {
      const response = await api.put(`/auditoria/${id}/rechazar`, { motivo });
      return response.data;
    } catch (error) {
      console.warn(`Backend real no disponible. Rechazando auditoría ${id} en mock.`, error);
      const docs = getStoredDocuments();
      const index = docs.findIndex(d => d.documento_id === id);
      if (index !== -1) {
        docs[index].estado = "RECHAZADO";
        docs[index].decision_enrutamiento.requiere_auditoria = false;
        docs[index].decision_enrutamiento.motivo_auditoria = motivo;
        saveStoredDocuments(docs);
        return docs[index];
      }
      throw new Error("Documento no encontrado");
    }
  },

  // PUT /api/auditoria/{id}
  corregirAuditoria: async (id, datosCorregidos) => {
    try {
      const response = await api.put(`/auditoria/${id}`, datosCorregidos);
      return response.data;
    } catch (error) {
      console.warn(`Backend real no disponible. Corrigiendo auditoría ${id} en mock.`, error);
      const docs = getStoredDocuments();
      const index = docs.findIndex(d => d.documento_id === id);
      if (index !== -1) {
        // Merge corrected data into document
        if (datosCorregidos.paciente) {
          docs[index].datos_extraidos.paciente = {
            ...docs[index].datos_extraidos.paciente,
            ...datosCorregidos.paciente
          };
        }
        if (datosCorregidos.medico) {
          docs[index].datos_extraidos.medico = {
            ...docs[index].datos_extraidos.medico,
            ...datosCorregidos.medico
          };
        }
        if (datosCorregidos.diagnostico) {
          docs[index].datos_extraidos.diagnostico = datosCorregidos.diagnostico;
        }
        if (datosCorregidos.cie10) {
          docs[index].datos_extraidos.cie10 = datosCorregidos.cie10;
        }
        if (datosCorregidos.tipo_documento) {
          docs[index].clasificacion.tipo_documento = datosCorregidos.tipo_documento;
        }
        if (datosCorregidos.prioridad) {
          docs[index].clasificacion.prioridad = datosCorregidos.prioridad;
        }
        if (datosCorregidos.destino) {
          docs[index].decision_enrutamiento.destino = datosCorregidos.destino;
        }

        docs[index].estado = "PROCESADO";
        docs[index].decision_enrutamiento.requiere_auditoria = false;
        saveStoredDocuments(docs);
        return docs[index];
      }
      throw new Error("Documento no encontrado");
    }
  }
};
