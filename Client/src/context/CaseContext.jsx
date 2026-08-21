import React, { createContext, useContext, useState, useEffect } from 'react';
import { caseService } from '../services/case';
import { useAuth } from './AuthContext';

const CaseContext = createContext(null);

export const CaseProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(() => {
    const saved = localStorage.getItem('tracelens_active_case');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  const fetchCases = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const data = await caseService.getCases();
      setCases(data);
      if (data.length > 0) {
        // If active case is set, refresh it from new list or select first
        setActiveCase((prev) => {
          if (prev) {
            const found = data.find((c) => c.id === prev.id);
            if (found) {
              localStorage.setItem('tracelens_active_case', JSON.stringify(found));
              return found;
            }
          }
          localStorage.setItem('tracelens_active_case', JSON.stringify(data[0]));
          return data[0];
        });
      }
    } catch (err) {
      console.error('Failed to load cases', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [isAuthenticated]);

  const selectCase = (caseObj) => {
    setActiveCase(caseObj);
    localStorage.setItem('tracelens_active_case', JSON.stringify(caseObj));
  };

  const createNewCase = async (caseData) => {
    const newCase = await caseService.createCase(caseData);
    setCases((prev) => [newCase, ...prev]);
    selectCase(newCase);
    return newCase;
  };

  return (
    <CaseContext.Provider
      value={{
        cases,
        activeCase,
        loading,
        selectCase,
        refreshCases: fetchCases,
        createNewCase,
      }}
    >
      {children}
    </CaseContext.Provider>
  );
};

export const useCase = () => {
  const context = useContext(CaseContext);
  if (!context) {
    throw new Error('useCase must be used within a CaseProvider');
  }
  return context;
};
