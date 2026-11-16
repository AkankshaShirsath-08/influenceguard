import { useState } from 'react';
import axios from 'axios';
import { ShieldCheck, CloudUpload } from 'lucide-react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

function App() {
  const [files, setFiles] = useState({ accounts: null, comments: null, growth: null });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFiles({ ...files, [e.target.name]: e.target.files[0] });
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!files.accounts || !files.comments || !files.growth) {
      setError("Please select all three CSV files.");
      return;
    }

    const formData = new FormData();
    formData.append("accounts", files.accounts);
    formData.append("comments", files.comments);
    formData.append("growth", files.growth);
    formData.append("influencer_name", "demo_user");

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post("http://localhost:8000/api/analyze", formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Check backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', fontFamily: 'sans-serif' }}>
      
      {/* NAVBAR */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 40px', backgroundColor: '#1e293b', borderBottom: '1px solid #334155' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '18px', fontWeight: 'bold', color: '#f8fafc' }}>
          <ShieldCheck size={24} color="#38bdf8" /> InfluenceGuard AI
        </div>
        <div style={{ display: 'flex', gap: '25px', color: '#94a3b8', fontSize: '14px' }}>
          <span style={{ cursor: 'pointer', color: '#f8fafc' }}>Upload</span>
          <span style={{ cursor: 'pointer' }}>Report</span>
          <span style={{ cursor: 'pointer' }}>Metrics</span>
        </div>
      </nav>

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '60px 20px' }}>
        
        {/* UPLOAD PAGE */}
        {!result && (
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '10px', color: '#f8fafc' }}>
              How real is this influencer's audience?
            </h1>
            <p style={{ color: '#94a3b8', marginBottom: '40px', fontSize: '15px' }}>
              Upload the data and get an authenticity score, fake follower share, spam comments and bot networks in seconds.
            </p>
            
            <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              
              <div style={{ width: '100%', maxWidth: '600px', border: '2px dashed #475569', borderRadius: '12px', padding: '40px', backgroundColor: '#1e293b', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' }}>
                <CloudUpload size={48} color="#38bdf8" />
                <div style={{ marginBottom: '10px' }}>
                  <h3 style={{ margin: '0 0 5px 0', fontSize: '16px', color: '#f8fafc' }}>Upload your CSV files here</h3>
                  <p style={{ color: '#64748b', margin: 0, fontSize: '13px' }}>accounts.csv, comments.csv, growth.csv</p>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%', maxWidth: '400px' }}>
                  <input type="file" id="accounts" name="accounts" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
                  <label htmlFor="accounts" style={{ display: 'block', padding: '12px', backgroundColor: '#0f172a', border: '1px dashed #475569', borderRadius: '8px', cursor: 'pointer', textAlign: 'center', color: files.accounts ? '#38bdf8' : '#94a3b8', fontSize: '14px' }}>
                    {files.accounts ? `✅ ${files.accounts.name}` : '📄 Select accounts.csv'}
                  </label>

                  <input type="file" id="comments" name="comments" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
                  <label htmlFor="comments" style={{ display: 'block', padding: '12px', backgroundColor: '#0f172a', border: '1px dashed #475569', borderRadius: '8px', cursor: 'pointer', textAlign: 'center', color: files.comments ? '#38bdf8' : '#94a3b8', fontSize: '14px' }}>
                    {files.comments ? `✅ ${files.comments.name}` : '💬 Select comments.csv'}
                  </label>

                  <input type="file" id="growth" name="growth" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
                  <label htmlFor="growth" style={{ display: 'block', padding: '12px', backgroundColor: '#0f172a', border: '1px dashed #475569', borderRadius: '8px', cursor: 'pointer', textAlign: 'center', color: files.growth ? '#38bdf8' : '#94a3b8', fontSize: '14px' }}>
                    {files.growth ? `✅ ${files.growth.name}` : '📈 Select growth.csv'}
                  </label>
                </div>

                <button type="submit" disabled={loading} style={{ marginTop: '15px', padding: '12px 30px', backgroundColor: '#20c997', color: '#0f172a', border: 'none', borderRadius: '6px', fontSize: '15px', cursor: 'pointer', fontWeight: 'bold' }}>
                  {loading ? "Analyzing..." : "Analyze influencer"}
                </button>
              </div>

            </form>
            {error && <p style={{ color: '#ef4444', marginTop: '20px' }}>{error}</p>}
          </div>
        )}

        {/* DASHBOARD */}
        {result && (
          <div style={{ backgroundColor: '#1e293b', padding: '30px', borderRadius: '12px', border: '1px solid #334155' }}>
            
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '20px', marginBottom: '20px' }}>
              <div>
                <h2 style={{ fontSize: '24px', color: '#38bdf8', margin: '0 0 5px 0' }}>Analysis Report</h2>
                <p style={{ color: '#94a3b8', margin: 0 }}>Profile: demo_user</p>
              </div>
              <div style={{ backgroundColor: result.risk_level === 'High' ? '#ef4444' : '#10b981', color: 'white', padding: '8px 16px', borderRadius: '20px', fontWeight: 'bold' }}>
                {result.risk_level} Risk
              </div>
            </div>

            {/* Top Row: Gauge & Stats */}
            <div style={{ display: 'flex', gap: '20px' }}>
              <div style={{ flex: 1, backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', textAlign: 'center', border: '1px solid #334155' }}>
                <h3 style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '20px' }}>AUTHENTICITY SCORE</h3>
                <div style={{ width: '120px', height: '120px', borderRadius: '50%', margin: '0 auto', background: `conic-gradient(${result.authenticity_score > 60 ? '#10b981' : '#ef4444'} ${result.authenticity_score}%, #334155 0)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ width: '100px', height: '100px', borderRadius: '50%', backgroundColor: '#0f172a', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                    <span style={{ fontSize: '32px', fontWeight: 'bold' }}>{result.authenticity_score}</span>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>out of 100</span>
                  </div>
                </div>
              </div>

              <div style={{ flex: 2, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                  <h4 style={{ color: '#94a3b8', margin: '0 0 10px 0', fontSize: '14px' }}>Fake Followers</h4>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#ef4444', margin: 0 }}>{result.fake_follower_pct}%</p>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                  <h4 style={{ color: '#94a3b8', margin: '0 0 10px 0', fontSize: '14px' }}>Spam Comments</h4>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#f59e0b', margin: 0 }}>{result.spam_comment_pct}%</p>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                  <h4 style={{ color: '#94a3b8', margin: '0 0 10px 0', fontSize: '14px' }}>Growth Spikes</h4>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#38bdf8', margin: 0 }}>{result.growth.length}</p>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                  <h4 style={{ color: '#94a3b8', margin: '0 0 10px 0', fontSize: '14px' }}>Bot Pods</h4>
                  <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#c084fc', margin: 0 }}>
                    {result.reasons.some(r => r.feature.includes("Bot pod")) ? "Yes" : "No"}
                  </p>
                </div>
              </div>
            </div>

            {/* Middle Row: Charts */}
            <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
              
              {/* Donut Chart */}
              <div style={{ flex: 1, backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                <h3 style={{ margin: '0 0 15px 0', fontSize: '16px' }}>Fake vs Real Followers</h3>
                <div style={{ width: '100%', height: '180px', display: 'flex', alignItems: 'center' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Fake', value: result.fake_follower_pct },
                          { name: 'Real', value: 100 - result.fake_follower_pct }
                        ]}
                        cx="50%" cy="50%" innerRadius={55} outerRadius={75} paddingAngle={5} dataKey="value"
                      >
                        <Cell fill="#ef4444" />
                        <Cell fill="#10b981" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                {/* DYNAMIC NUMBERS UPDATED HERE */}
                <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '10px', fontSize: '14px' }}>
                  <span style={{ color: '#ef4444' }}>
                    ■ Fake: {result.fake_follower_count}
                  </span>
                  <span style={{ color: '#10b981' }}>
                    ■ Real: {result.total_followers - result.fake_follower_count}
                  </span>
                </div>
              </div>

              {/* Growth Line Chart */}
              <div style={{ flex: 2, backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                <h3 style={{ margin: '0 0 15px 0', fontSize: '16px' }}>Follower Growth</h3>
                <div style={{ width: '100%', height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.growth}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                      <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                      <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                      <Line type="monotone" dataKey="followers" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

            </div>

            {/* Reasons Section */}
            <div style={{ marginTop: '20px', backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
              <h3 style={{ margin: '0 0 15px 0', fontSize: '18px' }}>Top Reasons for this Score</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {result.reasons.map((reason, idx) => (
                  <div key={idx}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                      <span style={{ color: '#e2e8f0', fontSize: '14px' }}>{reason.feature}</span>
                      <span style={{ color: '#94a3b8', fontSize: '12px' }}>{Math.round(reason.impact * 100)}%</span>
                    </div>
                    {/* Pink Progress Bar */}
                    <div style={{ width: '100%', height: '8px', backgroundColor: '#334155', borderRadius: '4px' }}>
                      <div style={{ width: `${reason.impact * 100}%`, height: '100%', backgroundColor: '#f43f5e', borderRadius: '4px' }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button onClick={() => setResult(null)} style={{ marginTop: '20px', padding: '12px 24px', backgroundColor: '#334155', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              Analyze Another Profile
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;