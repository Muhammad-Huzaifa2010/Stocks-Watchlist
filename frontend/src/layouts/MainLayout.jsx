import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'

function MainLayout() {
  return (
    <div className="layout">
      <Navbar />
      <main className="layout-content">
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout
