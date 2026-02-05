import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import './Requests.css'

const Requests = () => {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [selectedDonation, setSelectedDonation] = useState(null)
  const [pickupTime, setPickupTime] = useState('')

  const { data: requests, isLoading: requestsLoading } = useQuery({
    queryKey: ['requests', user?.role],
    queryFn: async () => {
      const response = await api.get('/api/requests/')
      return response.data
    },
    enabled: !!user,
  })

  const { data: availableDonations } = useQuery({
    queryKey: ['donations', 'available'],
    queryFn: async () => {
      const response = await api.get('/api/donations/')
      return response.data.filter((d) => d.status === 'AVAILABLE')
    },
    enabled: !!user && user?.role === 'NGO',
  })

  const createMutation = useMutation({
    mutationFn: async (data) => {
      // Convert datetime-local to ISO format
      const pickupTimeISO = new Date(data.pickup_time).toISOString()
      const response = await api.post('/api/requests/', {
        donation: data.donation,
        pickup_time: pickupTimeISO,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['requests'])
      queryClient.invalidateQueries(['donations'])
      setShowForm(false)
      setSelectedDonation(null)
      setPickupTime('')
    },
    onError: (error) => {
      console.error('Error creating request:', error)
      alert(error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || 'Failed to create request')
    },
  })

  const approveMutation = useMutation({
    mutationFn: async (requestId) => {
      const response = await api.post(`/api/requests/${requestId}/approve/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['requests'])
    },
  })

  const completeMutation = useMutation({
    mutationFn: async (requestId) => {
      const response = await api.post(`/api/requests/${requestId}/complete_pickup/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['requests'])
      queryClient.invalidateQueries(['donations'])
      queryClient.invalidateQueries(['impact-stats'])
    },
  })

  const handleRequestSubmit = (e) => {
    e.preventDefault()
    if (!selectedDonation || !pickupTime) return

    createMutation.mutate({
      donation: selectedDonation.id,
      pickup_time: pickupTime,
    })
  }

  if (requestsLoading) return <div>Loading...</div>

  return (
    <div className="requests">
      <div className="page-header">
        <h1>Food Requests</h1>
        {user?.role === 'NGO' && (
          <button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Request'}
          </button>
        )}
      </div>

      {showForm && user?.role === 'NGO' && (
        <form onSubmit={handleRequestSubmit} className="request-form">
          <div className="form-group">
            <label>Select Donation</label>
            <select
              value={selectedDonation?.id || ''}
              onChange={(e) => {
                const donation = availableDonations?.find(
                  (d) => d.id === parseInt(e.target.value)
                )
                setSelectedDonation(donation)
              }}
              required
            >
              <option value="">-- Select a donation --</option>
              {availableDonations?.map((donation) => (
                <option key={donation.id} value={donation.id}>
                  {donation.food_type} - {donation.quantity_kg}kg -{' '}
                  {donation.distance_km && `${donation.distance_km}km away`}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Pickup Time</label>
            <input
              type="datetime-local"
              value={pickupTime}
              onChange={(e) => setPickupTime(e.target.value)}
              required
            />
          </div>
          {createMutation.isError && (
            <div className="error-message">
              {createMutation.error?.response?.data?.detail || 
               createMutation.error?.response?.data?.non_field_errors?.[0] || 
               'Failed to create request'}
            </div>
          )}
          <button type="submit" disabled={createMutation.isLoading}>
            {createMutation.isLoading ? 'Creating...' : 'Create Request'}
          </button>
        </form>
      )}

      <div className="requests-list">
        {requests && requests.length > 0 ? (
          requests.map((request) => (
            <div key={request.id} className="request-card">
              <div className="request-header">
                <h3>Request #{request.id}</h3>
                <span className={`status-badge status-${request.status.toLowerCase()}`}>
                  {request.status}
                </span>
              </div>
              {request.donation && (
                <div className="request-donation">
                  <p>
                    <strong>Food Type:</strong> {request.donation.food_type}
                  </p>
                  <p>
                    <strong>Quantity:</strong> {request.donation.quantity_kg} kg
                  </p>
                  <p>
                    <strong>Description:</strong> {request.donation.description}
                  </p>
                </div>
              )}
              {request.ngo && (
                <p>
                  <strong>NGO:</strong> {request.ngo.username}
                </p>
              )}
              <p>
                <strong>Pickup Time:</strong>{' '}
                {new Date(request.pickup_time).toLocaleString()}
              </p>
              <div className="request-actions">
                {user?.role === 'DONOR' &&
                  request.status === 'PENDING' && (
                    <button
                      onClick={() => approveMutation.mutate(request.id)}
                      disabled={approveMutation.isLoading}
                    >
                      {approveMutation.isLoading ? 'Approving...' : 'Approve'}
                    </button>
                  )}
                {user?.role === 'NGO' &&
                  request.status === 'APPROVED' && (
                    <button
                      onClick={() => completeMutation.mutate(request.id)}
                      disabled={completeMutation.isLoading}
                    >
                      {completeMutation.isLoading
                        ? 'Completing...'
                        : 'Mark as Completed'}
                    </button>
                  )}
              </div>
            </div>
          ))
        ) : (
          <p>No requests yet</p>
        )}
      </div>
    </div>
  )
}

export default Requests

