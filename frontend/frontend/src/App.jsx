import { useState } from 'react'
import axios from 'axios'

function App() {
  const [url, setUrl] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      // هنا نقوم بمناداة الباكيند الذي برمجناه (تأكدي أن سيرفر البايثون يعمل)
      const response = await axios.get(`http://127.0.0.1:8000/analyze?url=${url}`)
      setData(response.data)
    } catch (error) {
      alert("Error connecting to backend!")
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-100 p-10 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8 text-blue-600">SEO Checker 🚀</h1>
      
      <div className="flex gap-2 mb-10 w-full max-w-md">
        <input 
          type="text" 
          placeholder="Enter website URL (https://...)" 
          className="flex-1 p-2 border rounded"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button 
          onClick={handleAnalyze}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Checking...' : 'Analyze'}
        </button>
      </div>

      {data && (
        <div className="bg-white p-6 rounded shadow-lg w-full max-w-2xl">
          <h2 className="text-xl font-bold border-b pb-2 mb-4">Analysis Report</h2>
          <div className="space-y-4">
            <p><strong>Title:</strong> {data.title}</p>
            <p><strong>Description:</strong> {data.description}</p>
            <div className="p-3 bg-green-50 text-green-700 rounded">
              Status: {data.status}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App