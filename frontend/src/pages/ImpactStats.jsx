import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './ImpactStats.css'

const ImpactStats = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['impact-stats'],
    queryFn: async () => {
      const response = await api.get('/api/stats/impact/')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="impact-stats">
      <h1>Impact Statistics</h1>
      <div className="stats-grid">
        <div className="stat-card large">
          <div className="stat-icon">🍽️</div>
          <h2>{stats?.total_meals_saved || 0}</h2>
          <p>Meals Saved</p>
        </div>
        <div className="stat-card large">
          <div className="stat-icon">📦</div>
          <h2>{stats?.total_food_saved_kg || 0} kg</h2>
          <p>Food Saved</p>
        </div>
        <div className="stat-card large">
          <div className="stat-icon">🌱</div>
          <h2>{stats?.total_co2_saved_kg || 0} kg</h2>
          <p>CO₂ Saved</p>
        </div>
        <div className="stat-card large">
          <div className="stat-icon">📊</div>
          <h2>{stats?.total_donations || 0}</h2>
          <p>Total Donations</p>
        </div>
      </div>
      <div className="impact-message">
        <p>
          🌍 Together, we're making a difference! Every donation helps reduce
          food waste and feed those in need.
        </p>
      </div>
    </div>
  )
}

export default ImpactStats

