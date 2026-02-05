import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const { user } = useAuth()

  const { data: stats } = useQuery({
    queryKey: ['impact-stats'],
    queryFn: async () => {
      const response = await api.get('/api/stats/impact/')
      return response.data
    },
  })

  const { data: donations } = useQuery({
    queryKey: ['donations', user?.role],
    queryFn: async () => {
      const response = await api.get('/api/donations/')
      return response.data
    },
    enabled: !!user,
  })

  const { data: requests } = useQuery({
    queryKey: ['requests', user?.role],
    queryFn: async () => {
      const response = await api.get('/api/requests/')
      return response.data
    },
    enabled: !!user,
  })

  return (
    <div className="dashboard">
      <h1>Welcome, {user?.username}!</h1>
      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Meals Saved</h3>
          <p className="stat-value">{stats?.total_meals_saved || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Food Saved (kg)</h3>
          <p className="stat-value">{stats?.total_food_saved_kg || 0}</p>
        </div>
        <div className="stat-card">
          <h3>CO₂ Saved (kg)</h3>
          <p className="stat-value">{stats?.total_co2_saved_kg || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Total Donations</h3>
          <p className="stat-value">{stats?.total_donations || 0}</p>
        </div>
      </div>

      <div className="dashboard-sections">
        <div className="section-card">
          <h2>Recent Donations</h2>
          {donations && donations.length > 0 ? (
            <ul>
              {donations.slice(0, 5).map((donation) => (
                <li key={donation.id}>
                  {donation.food_type} - {donation.quantity_kg}kg -{' '}
                  {donation.status}
                </li>
              ))}
            </ul>
          ) : (
            <p>No donations yet</p>
          )}
        </div>

        <div className="section-card">
          <h2>Recent Requests</h2>
          {requests && requests.length > 0 ? (
            <ul>
              {requests.slice(0, 5).map((request) => (
                <li key={request.id}>
                  Request #{request.id} - {request.status}
                </li>
              ))}
            </ul>
          ) : (
            <p>No requests yet</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

