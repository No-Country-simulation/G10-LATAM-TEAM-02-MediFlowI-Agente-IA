export type ViewerLoadingState = 'idle' | 'loading' | 'ready' | 'error';

export interface DocumentViewerProps {
  /** Nombre del archivo o identificador clínico para títulos y metadatos */
  fileName?: string;
  /** URL accesible o data URL del documento o imagen */
  fileUrl?: string;
  /** Altura mínima predeterminada del visor (por defecto: '480px') */
  minHeight?: string;
  /** Callback opcional notificador de cambios en pantalla completa */
  onFullScreenChange?: (isFullScreen: boolean) => void;
  /** Callback opcional notificador de fallos de carga */
  onError?: (error: Error) => void;
}

export interface DocumentViewerState {
  loadingState: ViewerLoadingState;
  zoomLevel: number;
  isFullscreen: boolean;
  errorMessage: string | null;
  lastLoadedUrl?: string;
}

