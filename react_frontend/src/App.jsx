import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';

function App() {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1); // Page 1: Table, Page 2: Charts

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/data')
      .then(res => setData(res.data))
      .catch(err => console.error("API Error:", err));
  }, []);

  // 🔍 UNIVERSAL SEARCH: Searches column names and values
  const filteredData = data.filter(item => {
    const search = searchTerm.toLowerCase();
    return Object.values(item).some(val => String(val).toLowerCase().includes(search));
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div style={{ width: '100vw', minHeight: '100vh', backgroundColor: '#0f172a', color: '#fff', fontFamily: 'sans-serif' }}>
      
      {/* HEADER & SEARCH ENGINE */}
      <div style={{ padding: '40px', textAlign: 'center', background: 'linear-gradient(to right, #1e293b, #0f172a)' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '20px' }}>🚀 Nifty 50 Discovery Engine</h1>
        <input 
          type="text" 
          placeholder="Search column names (Open, High, Low) or values..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={searchStyle}
        />
        <div style={{ marginTop: '20px' }}>
          <button onClick={() => setPage(1)} style={page === 1 ? activeBtn : navBtn}>1. Data Table</button>
          <button onClick={() => setPage(2)} style={page === 2 ? activeBtn : navBtn}>2. Visual Analytics</button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {page === 1 ? (
          /* PAGE 1: CSV TABLE VIEW */
          <motion.div key="p1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ padding: '40px' }}>
            <div style={tableContainer}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#1e293b', textAlign: 'left' }}>
                    <th style={tdStyle}>Timestamp</th><th style={tdStyle}>Date</th>
                    <th style={tdStyle}>Open</th><th style={tdStyle}>High</th>
                    <th style={tdStyle}>Low</th><th style={tdStyle}>Close</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.slice(0, 50).map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #334155' }}>
                      <td style={tdStyle}>{row.timestamp}</td><td style={tdStyle}>{row.dt}</td>
                      <td style={tdStyle}>{row.open}</td><td style={tdStyle}>{row.high}</td>
                      <td style={tdStyle}>{row.low}</td><td style={tdStyle}>{row.close}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        ) : (
          /* PAGE 2: INTERACTIVE CHARTS & ANIMATIONS */
          <motion.div key="p2" initial={{ x: 100, opacity: 0 }} animate={{ x: 0, opacity: 1 }} style={{ padding: '40px' }}>
            <div style={chartGrid}>
              
              {/* LINE CHART */}
              <div style={chartCard}><h3>Line: Price Trend</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={filteredData.slice(0, 20)}><XAxis dataKey="timestamp" stroke="#94a3b8"/><YAxis stroke="#94a3b8"/><Tooltip/><Line type="monotone" dataKey="close" stroke="#38bdf8" strokeWidth={3} dot={{ r: 6 }}/></LineChart>
                </ResponsiveContainer>
              </div>

              {/* BAR CHART */}
              <div style={chartCard}><h3>Bar: Market Volatility</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={filteredData.slice(0, 10)}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="timestamp" stroke="#94a3b8"/><YAxis stroke="#94a3b8"/><Tooltip/><Bar dataKey="high" fill="#4ade80" /><Bar dataKey="low" fill="#f87171" /></BarChart>
                </ResponsiveContainer>
              </div>

              {/* PIE CHART */}
              <div style={chartCard}><h3>Pie: Price Concentration</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart><Pie data={filteredData.slice(0, 5)} dataKey="close" nameKey="timestamp" cx="50%" cy="50%" outerRadius={80}>{filteredData.map((e, i) => <Cell key={i} fill={COLORS[i % 4]} />)}</Pie><Tooltip/></PieChart>
                </ResponsiveContainer>
              </div>

              {/* SCATTER PLOT */}
              <div style={chartCard}><h3>Live Scatter: Open vs Close</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <ScatterChart><XAxis dataKey="open" name="Open" stroke="#94a3b8"/><YAxis dataKey="close" name="Close" stroke="#94a3b8"/><Tooltip cursor={{ strokeDasharray: '3 3' }} /><Scatter name="Nifty" data={filteredData.slice(0, 50)} fill="#fbbf24" /></ScatterChart>
                </ResponsiveContainer>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// STYLES
const searchStyle = { width: '60%', padding: '15px', borderRadius: '30px', border: 'none', outline: 'none', fontSize: '1.1rem', backgroundColor: '#1e293b', color: '#fff', boxShadow: '0 0 20px rgba(56, 189, 248, 0.2)' };
const navBtn = { padding: '10px 20px', margin: '0 10px', borderRadius: '5px', border: '1px solid #38bdf8', background: 'transparent', color: '#38bdf8', cursor: 'pointer' };
const activeBtn = { ...navBtn, background: '#38bdf8', color: '#0f172a' };
const tableContainer = { backgroundColor: '#1e293b', borderRadius: '15px', padding: '20px', overflowX: 'auto' };
const tdStyle = { padding: '15px', borderBottom: '1px solid #334155' };
const chartGrid = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' };
const chartCard = { backgroundColor: '#1e293b', padding: '20px', borderRadius: '15px', boxShadow: '0 10px 15px rgba(0,0,0,0.3)' };

export default App;