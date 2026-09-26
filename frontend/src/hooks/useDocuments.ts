import { useCallback, useEffect, useState } from 'react'
import { documentsApi, type DocumentFilters } from '../api/documentsApi'
import type { ClinicalDocument } from '../types/documents'

export function useDocuments(initialFilters: DocumentFilters = {}) {
  const [documents, setDocuments] = useState<ClinicalDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<DocumentFilters>(initialFilters)
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    let active = true
    documentsApi.obtenerDocumentos(filters)
      .then((items) => { if (active) setDocuments(items) })
      .catch((caughtError: unknown) => {
        if (active) setError(caughtError instanceof Error ? caughtError.message : 'Error al cargar la lista de documentos')
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [filters, revision])

  const refetch = useCallback(() => {
    setLoading(true)
    setError(null)
    setRevision((value) => value + 1)
  }, [])

  const updateFilters = (newFilters: Partial<DocumentFilters>) => {
    const updated = { ...filters, ...newFilters }
    setFilters(updated)
  }

  return { documents, loading, error, filters, updateFilters, refetch }
}
