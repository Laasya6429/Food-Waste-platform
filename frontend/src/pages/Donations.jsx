import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import './Donations.css'

const Donations = () => {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    food_type: 'COOKED',
    description: '',
    quantity_kg: '',
    cooked_time: '',
    expiry_time: '',
  })

  const { data: donations, isLoading } = useQuery({
    queryKey: ['donations', user?.role],
    queryFn: async () => {
      const response = await api.get('/api/donations/')
      return response.data
    },
    enabled: !!user,
  })

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/donations/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['donations'])
      setShowForm(false)
      setFormData({
        food_type: 'COOKED',
        description: '',
        quantity_kg: '',
        cooked_time: '',
        expiry_time: '',
      })
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="donations">
      <div className="page-header">
        <h1>Donations</h1>
        {user?.role === 'DONOR' && (
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Donation'}
          </button>
        )}
      </div>

      {showForm && user?.role === 'DONOR' && (
        <form onSubmit={handleSubmit} className="donation-form">
          <div className="form-group">
            <label>Food Type</label>
            <select
              name="food_type"
              value={formData.food_type}
              onChange={handleChange}
              required
            >
              <option value="COOKED">Cooked Food</option>
              <option value="PACKAGED">Packaged Food</option>
              <option value="RAW">Raw Ingredients</option>
            </select>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Quantity (kg)</label>
            <input
              type="number"
              step="0.1"
              name="quantity_kg"
              value={formData.quantity_kg}
              onChange={handleChange}
              required
            />
          </div>
          {formData.food_type === 'COOKED' && (
            <div className="form-group">
              <label>Cooked Time</label>
              <input
                type="datetime-local"
                name="cooked_time"
                value={formData.cooked_time}
                onChange={handleChange}
              />
            </div>
          )}
          <div className="form-group">
            <label>Expiry Time</label>
            <input
              type="datetime-local"
              name="expiry_time"
              value={formData.expiry_time}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" disabled={createMutation.isLoading}>
            {createMutation.isLoading ? 'Creating...' : 'Create Donation'}
          </button>
        </form>
      )}

      <div className="donations-list">
        {donations && donations.length > 0 ? (
          donations.map((donation) => (
            <div key={donation.id} className="donation-card">
              <div className="donation-header">
                <h3>{donation.food_type}</h3>
                <span className={`status-badge status-${donation.status.toLowerCase()}`}>
                  {donation.status}
                </span>
              </div>
              <p className="donation-description">{donation.description}</p>
              <div className="donation-details">
                <span>Quantity: {donation.quantity_kg} kg</span>
                {donation.donor && (
                  <span>Donor: {donation.donor.username}</span>
                )}
                {donation.distance_km && (
                  <span>Distance: {donation.distance_km} km</span>
                )}
                {donation.risk_assessment && (
                  <span className={`risk-${donation.risk_assessment.risk_level.toLowerCase()}`}>
                    Risk: {donation.risk_assessment.risk_level}
                  </span>
                )}
              </div>
              <p className="donation-expiry">
                Expires: {new Date(donation.expiry_time).toLocaleString()}
              </p>
            </div>
          ))
        ) : (
          <p>No donations available</p>
        )}
      </div>
    </div>
  )
}

export default Donations

