import { create } from 'zustand';

export interface UserProfile {
  name: string;
  profession: string;
  summary: string;
}

interface SettingsState {
  userProfile: UserProfile | null;
  setUserProfile: (profile: UserProfile) => void;
  clearUserProfile: () => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  userProfile: null,
  setUserProfile: (profile) => set({ userProfile: profile }),
  clearUserProfile: () => set({ userProfile: null }),
}));
