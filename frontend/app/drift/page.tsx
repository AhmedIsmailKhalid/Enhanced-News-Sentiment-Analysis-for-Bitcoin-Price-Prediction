'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import DriftStatusCard from '@/components/drift/DriftStatusCard';

interface DriftSummary {
  feature_set: string;
  model_type: string;
  overall_severity: string;
  feature_drift: {
    status: string;
    drift_severity?: string;
    message?: string;
    significant_drift_count?: number;
    features_tested?: number;
    drift_results?: Array<{
      feature: string;
      psi: number;
      ks_pvalue: number;
      drift_detected: boolean;
      reference_mean?: number;
      current_mean?: number;
    }>;
  };
  model_drift: {
    status: string;
    drift_severity?: string;
    message?: string;
    accuracy?: {
      reference: number;
      current: number;
      drop: number;
      drift_detected: boolean;
    };
  };
  recommendations: string[];
}

export default function DriftPage() {
  const [vaderDrift, setVaderDrift] = useState<DriftSummary | null>(null);
  const [finbertDrift, setFinbertDrift] = useState<DriftSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'vader' | 'finbert'>('vader');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDriftData();

    // Refresh every 60 seconds
    const interval = setInterval(loadDriftData, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadDriftData = async () => {
    try {
      const [vaderResp, finbertResp] = await Promise.all([
        apiClient.getDriftSummary('vader', 'random_forest'),
        apiClient.getDriftSummary('finbert', 'random_forest'),
      ]);

      setVaderDrift(vaderResp.summary);
      setFinbertDrift(finbertResp.summary);
    } catch (error) {
      console.error('Failed to load drift data:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentDrift = activeTab === 'vader' ? vaderDrift : finbertDrift;

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Model Selector Tabs */}
      <div className="bg-white rounded-lg shadow p-2 inline-flex space-x-2">
        <button
          onClick={() => setActiveTab('vader')}
          className={`px-6 py-2 rounded-md font-medium transition-colors ${
            activeTab === 'vader'
              ? 'bg-cyan-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-100'
          }`}
        >
          VADER
        </button>
        <button
          onClick={() => setActiveTab('finbert')}
          className={`px-6 py-2 rounded-md font-medium transition-colors ${
            activeTab === 'finbert'
              ? 'bg-rose-600 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-100'
          }`}
        >
          FinBERT
        </button>
      </div>

      {/* Drift Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DriftStatusCard
          title="Overall Drift Severity"
          severity={currentDrift?.overall_severity || 'Unknown'}
          message={
            currentDrift?.overall_severity === 'unknown'
              ? 'Insufficient data for analysis'
              : 'System drift assessment'
          }
        />

        <DriftStatusCard
          title="Feature Drift"
          severity={currentDrift?.feature_drift?.drift_severity || currentDrift?.feature_drift?.status || 'Unknown'}
          message={currentDrift?.feature_drift?.message || 'Data distribution monitoring'}
        />

        <DriftStatusCard
          title="Model Drift"
          severity={currentDrift?.model_drift?.drift_severity || currentDrift?.model_drift?.status || 'Unknown'}
          message={currentDrift?.model_drift?.message || 'Performance monitoring'}
        />
      </div>

      {/* Feature Drift Details */}
      {currentDrift?.feature_drift?.drift_results && currentDrift.feature_drift.drift_results.length > 0 ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Top Drifted Features</h3>
            <p className="text-sm text-gray-500 mt-1">
              {currentDrift.feature_drift.significant_drift_count || 0} of{' '}
              {currentDrift.feature_drift.features_tested || 0} features showing significant drift
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Feature</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">PSI</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">KS p-value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ref Mean</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Mean</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Drift</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentDrift.feature_drift.drift_results.slice(0, 10).map((feature, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{feature.feature}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{feature.psi.toFixed(3)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{feature.ks_pvalue.toFixed(3)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {feature.reference_mean?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {feature.current_mean?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {feature.drift_detected ? (
                        <span className="text-red-600 font-medium">Yes</span>
                      ) : (
                        <span className="text-green-600 font-medium">No</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Drift Details</h3>
          <p className="text-gray-500 text-center py-8">
            {currentDrift?.feature_drift?.message || 'No drift data available - insufficient current data for comparison'}
          </p>
        </div>
      )}

      {/* Model Drift Details */}
      {currentDrift?.model_drift?.accuracy ? (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Performance Drift</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-cyan-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Reference Accuracy</p>
              <p className="text-2xl font-bold text-blue-600">
                {(currentDrift.model_drift.accuracy.reference * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Historical performance</p>
            </div>
            <div className="p-4 bg-rose-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Current Accuracy</p>
              <p className="text-2xl font-bold text-rose-600">
                {(currentDrift.model_drift.accuracy.current * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Recent performance</p>
            </div>
            <div className={`p-4 rounded-lg ${
              currentDrift.model_drift.accuracy.drift_detected ? 'bg-red-50' : 'bg-green-50'
            }`}>
              <p className="text-sm text-gray-600 mb-1">Accuracy Drop</p>
              <p className={`text-2xl font-bold ${
                currentDrift.model_drift.accuracy.drift_detected ? 'text-red-600' : 'text-green-600'
              }`}>
                {(currentDrift.model_drift.accuracy.drop * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {currentDrift.model_drift.accuracy.drift_detected ? 'Drift detected' : 'Within threshold'}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Performance Drift</h3>
          <p className="text-gray-500 text-center py-8">
            {currentDrift?.model_drift?.message || 'No model drift data available'}
          </p>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
        {currentDrift?.recommendations && currentDrift.recommendations.length > 0 ? (
          <ul className="space-y-2">
            {currentDrift.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start">
                <span className={`mr-2 ${
                  rec.includes('HIGH') ? 'text-red-600' :
                  rec.includes('MEDIUM') ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {rec.includes('HIGH') ? '⚠' : rec.includes('MEDIUM') ? '⚡' : '✓'}
                </span>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No specific recommendations - system stable</p>
        )}
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadDriftData}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Drift Analysis
        </button>
      </div>
    </div>
  );
}