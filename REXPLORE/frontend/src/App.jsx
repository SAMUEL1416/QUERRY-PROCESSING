import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import LibraryPage from './pages/LibraryPage'
import UploadPage from './pages/UploadPage'
import PaperPage from './pages/PaperPage'
import ComparisonPage from './pages/ComparisonPage'
import AnalyticsPage from './pages/AnalyticsPage'
import { useAuth } from './context/AuthContext'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [theme, setTheme] = useState(() => localStorage.getItem('rexplore-theme') || 'light')
  const { isAuthenticated, loading } = useAuth()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('rexplore-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  if (loading) {
    return (
      <div className="auth-boot-loader">
        <Loader2 size={28} className="spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<Navigate to="/" replace />} />
          <Route path="/register" element={<Navigate to="/" replace />} />
          <Route path="/" element={<Dashboard onOpenSidebar={() => setSidebarOpen(true)} />} />
          <Route path="/library" element={<LibraryPage onOpenSidebar={() => setSidebarOpen(true)} />} />
          <Route path="/upload" element={<UploadPage onOpenSidebar={() => setSidebarOpen(true)} />} />
          <Route path="/papers/:id" element={<PaperPage onOpenSidebar={() => setSidebarOpen(true)} />} />
          <Route path="/comparison" element={<ComparisonPage onOpenSidebar={() => setSidebarOpen(true)} />} />
          <Route path="/analytics" element={<AnalyticsPage onOpenSidebar={() => setSidebarOpen(true)} />} />
        </Routes>
      </main>
    </div>
  )
}
