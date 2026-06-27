import { useState } from 'react';
import axios from 'axios';
import { Routes, Route, Link } from 'react-router-dom';
import CategoryCard from './CategoryCard';
import PrivacyPolicy from './PrivacyPolicy';
import About from './About';
import Contact from './Contact';
import './App.css';

const AdBanner = () => (
    <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-2280336108138157"
        data-ad-slot="8237171876"
        data-ad-format="auto"
        data-full-width-responsive="true"
        ref={(el) => {
            if (el) {
                try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) {}
            }
        }}
    />
);

const scoreRing = (score) => {
    if (score >= 70) return 'border-green-500 text-green-500';
    if (score >= 50) return 'border-yellow-500 text-yellow-500';
    return 'border-red-500 text-red-500';
};

const miniScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
};

const Home = () => {
    const [url, setUrl] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!url.trim()) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const response = await axios.get(`/api/analyze?url=${encodeURIComponent(url.trim())}`);
            setData(response.data);
        } catch (err) {
            setError('Unable to analyze the URL. Make sure it is publicly accessible and starts with https://');
        }
        setLoading(false);
    };

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617]">
            <div className="stars"></div>
            <div className="twinkling"></div>

            {/* Hero / Tool */}
            <div className="relative z-10 w-full max-w-3xl px-4 mx-auto text-center pt-20 pb-10">
                <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    BoostSEO
                </h1>
                <p className="text-gray-400 mb-2 text-sm md:text-lg">Free Technical SEO Audit — 21 Checks</p>
                <p className="text-gray-500 mb-8 text-xs md:text-sm max-w-xl mx-auto">
                    Enter any public URL to get an instant SEO health score, grouped check results, and a downloadable PDF report.
                </p>

                {/* Input */}
                <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
                    <input
                        type="text"
                        placeholder="https://example.com"
                        className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                    >
                        {loading ? 'Analyzing…' : 'Start Audit'}
                    </button>
                </div>

                {error && (
                    <p className="text-red-400 mb-6 bg-red-400/10 p-3 rounded-lg border border-red-400/20">{error}</p>
                )}

                {/* Results */}
                {data && (
                    <div className="space-y-6 text-left">
                        {/* Overall score card */}
                        <div className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 shadow-2xl">
                            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                                <div>
                                    <h2 className="text-3xl font-bold text-white">Overall SEO Score</h2>
                                    <p className="text-gray-400 text-sm mt-1">Based on {data.meta.checks_total} checks</p>
                                    {data.summary && <p className="text-gray-300 text-sm mt-2">{data.summary}</p>}
                                    <div className="flex gap-5 mt-3 text-sm">
                                        <span className="text-green-400 font-medium">{data.meta.checks_passed} Passed</span>
                                        <span className="text-yellow-400 font-medium">{data.meta.checks_warned} Warnings</span>
                                        <span className="text-red-400 font-medium">{data.meta.checks_failed} Failed</span>
                                    </div>
                                </div>
                                <div className={`text-5xl font-black p-6 rounded-full border-4 flex-shrink-0 ${scoreRing(data.score)}`}>
                                    {data.score}
                                </div>
                            </div>

                            {/* Category mini-scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 border-t border-white/10 mt-6 pt-5">
                                {data.categories.map((cat) => (
                                    <div key={cat.name} className="text-center">
                                        <div className={`text-xl font-bold ${miniScoreColor(cat.score)}`}>{cat.score}%</div>
                                        <div className="text-gray-500 text-xs mt-1 leading-tight">{cat.name}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Category cards */}
                        {data.categories.map((cat) => (
                            <CategoryCard key={cat.name} category={cat} />
                        ))}

                        {/* Ad banner */}
                        <div className="rounded-2xl overflow-hidden">
                            <AdBanner />
                        </div>

                        {/* PDF download */}
                        <div className="flex justify-center pb-4">
                            <a
                                href={`/api/download-pdf?url=${encodeURIComponent(url)}`}
                                target="_blank"
                                rel="noreferrer"
                                className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl border border-white/20 transition-all flex items-center gap-2"
                            >
                                📥 Download PDF Report
                            </a>
                        </div>
                    </div>
                )}

                {/* Feature grid — shown before first audit */}
                {!data && (
                    <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                        {[
                            { icon: '🏷️', label: 'Meta & Social', desc: 'Title, description, canonical, Open Graph, Twitter Card' },
                            { icon: '📝', label: 'Content', desc: 'H1/H2/H3 structure, word count, image alt text' },
                            { icon: '⚙️', label: 'Technical', desc: 'HTTPS, viewport, favicon, language, structured data' },
                            { icon: '⚡', label: 'Performance', desc: 'Page load speed vs 2-second benchmark' },
                            { icon: '🔍', label: 'Crawlability', desc: 'robots.txt, sitemap.xml, broken links' },
                            { icon: '📄', label: 'PDF Report', desc: 'Download a full audit report for any URL' },
                        ].map((item) => (
                            <div key={item.label} className="bg-white/5 backdrop-blur-md p-4 rounded-xl border border-white/10">
                                <div className="text-2xl mb-2">{item.icon}</div>
                                <p className="text-white font-semibold text-sm mb-1">{item.label}</p>
                                <p className="text-gray-400 text-xs">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className="relative z-10 w-full py-6 text-center border-t border-white/5 bg-[#020617]/50 backdrop-blur-sm mt-auto">
                <div className="flex justify-center flex-wrap gap-6 text-sm">
                    <Link to="/" className="text-gray-500 hover:text-blue-400 transition-colors">Home</Link>
                    <Link to="/about" className="text-gray-500 hover:text-blue-400 transition-colors">About</Link>
                    <Link to="/contact" className="text-gray-500 hover:text-blue-400 transition-colors">Contact</Link>
                    <Link to="/privacy-policy" className="text-gray-500 hover:text-blue-400 transition-colors">Privacy Policy</Link>
                </div>
                <p className="mt-2 text-gray-600 text-xs">© 2026 BoostSEO. All rights reserved.</p>
            </footer>
        </div>
    );
};

function App() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        </Routes>
    );
}

export default App;
