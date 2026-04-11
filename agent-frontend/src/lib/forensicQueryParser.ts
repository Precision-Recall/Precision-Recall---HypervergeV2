/**
 * Parse natural language queries into forensic engine parameters
 */

import { ForensicMode, ForensicParams } from './forensicApi';

interface ParsedForensicQuery {
  mode: ForensicMode;
  params: ForensicParams;
}

export function parseForensicQuery(query: string): ParsedForensicQuery {
  const lowerQuery = query.toLowerCase();
  
  // Extract company ticker
  const companyMatch = query.match(/\b([A-Z]{1,5})\b/);
  const company = companyMatch ? companyMatch[1] : 'TSLA';
  
  // Extract years
  const yearMatches = query.match(/\b(20\d{2})\b/g);
  const years = yearMatches ? yearMatches.map(y => parseInt(y)) : [];
  
  // Detect mode based on keywords
  if (lowerQuery.includes('promise') || lowerQuery.includes('deliver') || lowerQuery.includes('target')) {
    // Promise vs. Reality mode
    const promise_year = years[0] || 2018;
    const verification_year = years[1] || 2023;
    
    return {
      mode: 'promise_vs_reality',
      params: {
        company,
        promise_year,
        verification_year,
        promise_query: query,
        lens: detectLens(query)
      }
    };
  } 
  else if (lowerQuery.includes('anomaly') || lowerQuery.includes('change') || lowerQuery.includes('risk factor')) {
    // Anomaly Detection mode
    const start_year = years[0] || 2022;
    const end_year = years[1] || 2023;
    
    return {
      mode: 'anomaly_detection',
      params: {
        company,
        start_year,
        end_year,
        lens: detectLens(query)
      }
    };
  } 
  else if (lowerQuery.includes('sentiment') || lowerQuery.includes('optimistic') || lowerQuery.includes('divergence')) {
    // Sentiment Divergence mode
    const year = years[0] || 2023;
    
    return {
      mode: 'sentiment_divergence',
      params: {
        company,
        year,
        lens: detectLens(query)
      }
    };
  }
  
  // Default to anomaly detection
  return {
    mode: 'anomaly_detection',
    params: {
      company,
      start_year: years[0] || 2022,
      end_year: years[1] || 2023,
      lens: 'governance'
    }
  };
}

function detectLens(query: string): 'finance' | 'environment' | 'strategy' | 'governance' {
  const lowerQuery = query.toLowerCase();
  
  if (lowerQuery.includes('environment') || lowerQuery.includes('renewable') || lowerQuery.includes('esg') || lowerQuery.includes('climate')) {
    return 'environment';
  }
  if (lowerQuery.includes('strategy') || lowerQuery.includes('business') || lowerQuery.includes('market')) {
    return 'strategy';
  }
  if (lowerQuery.includes('governance') || lowerQuery.includes('compliance') || lowerQuery.includes('control')) {
    return 'governance';
  }
  // Default to finance
  return 'finance';
}
