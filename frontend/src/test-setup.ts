import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Mock de Fullscreen API para entorno de pruebas JSDOM
if (typeof HTMLElement !== 'undefined' && !HTMLElement.prototype.requestFullscreen) {
  HTMLElement.prototype.requestFullscreen = vi.fn().mockImplementation(function (this: HTMLElement) {
    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      value: this,
    });
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  });
}

if (typeof document !== 'undefined' && !document.exitFullscreen) {
  document.exitFullscreen = vi.fn().mockImplementation(() => {
    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      value: null,
    });
    document.dispatchEvent(new Event('fullscreenchange'));
    return Promise.resolve();
  });
}
