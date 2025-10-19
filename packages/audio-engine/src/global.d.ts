// Extend the Window interface to include webkitAudioContext
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }

  // Extend HTMLAudioElement to include the missing properties
  interface HTMLAudioElement {
    volume: number;
    muted: boolean;
    currentTime: number;
    duration: number;
    play(): Promise<void>;
    pause(): void;
    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
  }

  // Add type for React event handlers
  interface HTMLInputEvent extends Event {
    target: HTMLInputElement & EventTarget;
  }
}

export {}; // This file needs to be a module
