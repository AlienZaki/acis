/**
 * Glasses store — tracks Bluetooth A2DP connection state.
 *
 * In Phase 1 this is updated by the native AudioSessionManager module when
 * the A2DP route changes.  For now it defaults to false and can be toggled.
 */

import { create } from "zustand";

interface GlassesState {
  connected: boolean;
  setConnected: (v: boolean) => void;
}

export const useGlassesStore = create<GlassesState>((set) => ({
  connected: false,
  setConnected: (v) => set({ connected: v }),
}));
