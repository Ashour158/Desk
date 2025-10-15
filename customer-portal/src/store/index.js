/**
 * Redux Store Configuration
 * Centralized state management with Redux Toolkit
 */

import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from '@reduxjs/toolkit';

// Import slice reducers
import authSlice from './slices/authSlice';
import ticketsSlice from './slices/ticketsSlice';
import dashboardSlice from './slices/dashboardSlice';
import knowledgeSlice from './slices/knowledgeSlice';
import communicationSlice from './slices/communicationSlice';
import userSlice from './slices/userSlice';
import performanceSlice from './slices/performanceSlice';
import uiSlice from './slices/uiSlice';

/**
 * Root reducer
 */
const rootReducer = combineReducers({
  auth: authSlice,
  tickets: ticketsSlice,
  dashboard: dashboardSlice,
  knowledge: knowledgeSlice,
  communication: communicationSlice,
  user: userSlice,
  performance: performanceSlice,
  ui: uiSlice
});

/**
 * Persist configuration
 */
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth', 'user', 'ui'], // Only persist these slices
  blacklist: ['performance', 'communication'] // Don't persist these slices
};

/**
 * Persisted reducer
 */
const persistedReducer = persistReducer(persistConfig, rootReducer);

/**
 * Store configuration
 */
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        ignoredPaths: ['_persist']
      },
      immutableCheck: {
        ignoredPaths: ['_persist']
      }
    }),
  devTools: process.env.NODE_ENV !== 'production'
});

/**
 * Persistor
 */
export const persistor = persistStore(store);

/**
 * Store types
 */
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

/**
 * Typed hooks
 */
export { useAppDispatch, useAppSelector } from './hooks';

export default store;
