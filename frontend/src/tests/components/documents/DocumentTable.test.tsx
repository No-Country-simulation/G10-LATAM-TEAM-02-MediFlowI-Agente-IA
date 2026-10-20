import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryRouter } from "react-router-dom";
import DocumentTable from "../../../components/documents/DocumentTable";
import type { ClinicalDocument } from "../../../types/documents";

const mockDocs: ClinicalDocument[] = Array.from({ length: 15 }, (_, i) => ({
  documento_id: `DOC-2026-00${i + 1}`,
  nombre_archivo: `epicrisis_${i + 1}.pdf`,
  estado: i === 0 ? "AUDITORIA" : "PROCESADO",
  fecha_creacion: "2026-10-20T10:00:00Z",
  clasificacion: {
    tipo_documento: "EPICRISIS",
    prioridad: i === 0 ? "ALTA" : "MEDIA",
    score_confianza: 0.88,
  },
  datos_extraidos: {
    paciente: {
      nombre: `Paciente ${i + 1}`,
    },
  },
  decision_enrutamiento: {
    destino: "Cardiología",
    requiere_auditoria: i === 0,
  },
}));

describe("DocumentTable Component", () => {
  it("renders empty state when no documents are provided", () => {
    render(<DocumentTable documents={[]} />);
    expect(screen.getByText(/No se encontraron documentos en esta vista/i)).toBeInTheDocument();
  });

  it("renders table with documents and pagination controls", () => {
    render(
      <MemoryRouter>
        <DocumentTable documents={mockDocs} pageSize={5} />
      </MemoryRouter>
    );

    expect(screen.getByText("DOC-2026-001")).toBeInTheDocument();
    expect(screen.getByText("epicrisis_1.pdf")).toBeInTheDocument();
    expect(screen.getByText("Paciente 1")).toBeInTheDocument();

    // Check pagination summary
    expect(screen.getByTestId("pagination-info")).toHaveTextContent("Mostrando 1 a 5 de 15 documentos");

    // Revisar button should be visible for doc 0
    expect(screen.getByText("Revisar")).toBeInTheDocument();
  });

  it("navigates between pages using Siguiente and Anterior buttons", () => {
    render(
      <MemoryRouter>
        <DocumentTable documents={mockDocs} pageSize={5} />
      </MemoryRouter>
    );

    const prevBtn = screen.getByTestId("pagination-prev");
    const nextBtn = screen.getByTestId("pagination-next");

    expect(prevBtn).toBeDisabled();
    expect(nextBtn).toBeEnabled();

    // Go to next page
    fireEvent.click(nextBtn);
    expect(screen.getByTestId("pagination-info")).toHaveTextContent("Mostrando 6 a 10 de 15 documentos");
    expect(screen.getByText("DOC-2026-006")).toBeInTheDocument();
    expect(prevBtn).toBeEnabled();

    // Go back to first page
    fireEvent.click(prevBtn);
    expect(screen.getByTestId("pagination-info")).toHaveTextContent("Mostrando 1 a 5 de 15 documentos");
    expect(screen.getByText("DOC-2026-001")).toBeInTheDocument();
  });

  it("changes page size when select option is changed", () => {
    render(
      <MemoryRouter>
        <DocumentTable documents={mockDocs} pageSize={5} />
      </MemoryRouter>
    );

    const pageSizeSelect = screen.getByTestId("page-size-select");
    fireEvent.change(pageSizeSelect, { target: { value: "20" } });

    expect(screen.getByTestId("pagination-info")).toHaveTextContent("Mostrando 1 a 15 de 15 documentos");
  });
});
