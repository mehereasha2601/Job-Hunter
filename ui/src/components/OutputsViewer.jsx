import { useState, useEffect } from 'react';
import { api } from '../api';

export default function OutputsViewer() {
  const [outputs, setOutputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadOutputs();
  }, []);

  const loadOutputs = async () => {
    try {
      setLoading(true);
      const data = await api.getOutputs();
      setOutputs(data.outputs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading outputs...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button onClick={loadOutputs} className="mt-2 text-sm text-red-600 underline">
          Retry
        </button>
      </div>
    );
  }

  if (outputs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <p className="text-gray-500">No tailored outputs yet.</p>
        <p className="text-sm text-gray-400 mt-2">
          Select jobs from the Jobs tab and click "Tailor Selected" to generate outputs.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Tailored Outputs ({outputs.length})
          </h2>
        </div>

        <div className="divide-y divide-gray-200">
          {outputs.map((output) => (
            <div key={output.id} className="px-6 py-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">
                    {output.title} at {output.company}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Tailored: {new Date(output.tailored_at).toLocaleDateString()} at{' '}
                    {new Date(output.tailored_at).toLocaleTimeString()}
                  </p>

                  <div className="flex items-center gap-4 mt-4">
                    {output.doc_url && (
                      <a
                        href={output.doc_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        📄 Resume Doc →
                      </a>
                    )}
                    {output.email_doc_url && (
                      <a
                        href={output.email_doc_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        ✉️ Email Doc →
                      </a>
                    )}
                    {output.resume_pdf_url && (
                      <a
                        href={output.resume_pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        📥 PDF →
                      </a>
                    )}
                    {output.md_path && (
                      <span className="text-sm text-gray-500">
                        📝 {output.md_path}
                      </span>
                    )}
                  </div>

                  <div className="mt-2">
                    <span className={`status-badge status-${output.status}`}>
                      {output.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
