import { useState, useEffect, useCallback } from "react";
import { documentsApi } from "../api/documentsApi";

export const useDocuments = (initialFilters = {}) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  const fetchDocuments = useCallback(async (currentFilters = filters) => {
    setLoading(true);
    setError(null);
    try {
      const data = await documentsApi.obtenerDocumentos(currentFilters);
      setDocuments(data);
    } catch (err) {
      setError(err.message || "Error al cargar la lista de documentos");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const updateFilters = (newFilters) => {
    const updated = { ...filters, ...newFilters };
    setFilters(updated);
    fetchDocuments(updated);
  };

  return {
    documents,
    loading,
    error,
    filters,
    updateFilters,
    refetch: fetchDocuments
  };
};
