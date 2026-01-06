import { useState } from 'react';
import axios from 'axios';
import './App.css'; 

function App() {
  const [url, setUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!url) {
      setError("Please enter a valid URL first!");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // استدعاء الباكيند للفحص
      const response = await axios.get(`http://127.0.0.1:8000/analyze?url=${url}`);
      setData(response.data);
    } catch (err) {
      setError("Unable to reach the backend. Make sure it's running on port 8000!");
    }
    setLoading(false);
  };

  const downloadPDF = () => {
    if (!data) return;
    // تحويل المصفوفة إلى نص مفصل بـ | ليفهمه الباكيند
    const recs = data.recommendations ? data.recommendations.join('|') : "No specific recommendations.";
    const reportUrl = `http://127.0.0.1:8000/download-pdf?url=${url}&title=${encodeURIComponent(data.title)}&score=${data.score}&recommendations=${encodeURIComponent(recs)}`;
    window.open(reportUrl);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#020617] font-sans">
      {/* خلفية النجوم المتحركة */}
      <div className="stars"></div>
      <div className="twinkling"></div>

      <div className="relative z-10 w-full max-w-2xl px-4 py-8 mx-auto text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 animate-pulse">
          SEO Checker Pro
        </h1>
        <p className="text-gray-400 mb-8 text-sm md:text-lg tracking-wide">Instant Professional Website Audit</p>
        
        {/* صندوق البحث */}
        <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
          <input 
            type="text" 
            placeholder="https://example.com" 
            className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button 
            onClick={handleAnalyze}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50 shadow-lg shadow-blue-500/20"
          >
            {loading ? 'Scanning...' : 'Analyze'}
          </button>
        </div>

        {/* عرض الخطأ إن وجد */}
        {error && (
          <div className="animate-bounce mb-6 p-3 bg-red-500/20 border border-red-500/50 text-red-400 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* عرض النتائج */}
        {data && (
          <div className="animate-fadeIn bg-white/10 backdrop-blur-xl p-6 rounded-3xl border border-white/20 text-left shadow-2xl relative overflow-hidden">
            <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
              <h2 className="text-2xl font-bold text-white">Analysis Results</h2>
              <div className="text-right">
                <span className="text-xs text-gray-400 block uppercase">SEO Score</span>
                <span className={`text-2xl font-mono font-bold ${data.score > 70 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {data.score}/100
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="space-y-1">
                <span className="text-blue-400 text-xs uppercase tracking-wider font-bold">Page Title</span>
                <p className="text-gray-200 text-base italic">"{data.title}"</p>
              </div>
              <div className="space-y-1">
                <span className="text-purple-400 text-xs uppercase tracking-wider font-bold">Content Status</span>
                <p className="text-gray-200 text-base flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span> Active Page
                </p>
              </div>
              <div className="md:col-span-2 space-y-1">
                <span className="text-green-400 text-xs uppercase tracking-wider font-bold">Meta Description</span>
                <p className="text-gray-300 text-sm leading-relaxed bg-black/20 p-3 rounded-lg border border-white/5">
                  {data.description}
                </p>
              </div>
            </div>

            {/* قسم التوصيات */}
            {data.recommendations && data.recommendations.length > 0 && (
              <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                <h3 className="text-blue-400 font-bold text-sm mb-2">💡 Recommendations:</h3>
                <ul className="text-xs text-gray-300 space-y-1 list-disc ml-4">
                  {data.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
                </ul>
              </div>
            )}

            {/* زر PDF الصغير */}
            <div className="flex justify-end pt-4 border-t border-white/10">
              <button 
                onClick={downloadPDF}
                className="flex items-center gap-2 bg-red-500/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-500/40 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-300 group"
              >
                <span>Download Report</span>
                <span className="group-hover:scale-125 transition-transform">📄</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;