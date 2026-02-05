import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import './Heatmap.css'

const Heatmap = () => {
  const { data: heatmapData, isLoading } = useQuery({
    queryKey: ['heatmap-data'],
    queryFn: async () => {
      const response = await api.get('/api/stats/heatmap/')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="heatmap">
      <h1>Food Waste Heatmap</h1>
      <p className="heatmap-description">
        Visual representation of food donation locations and quantities
      </p>
      <div className="heatmap-container">
        {heatmapData && heatmapData.length > 0 ? (
          <div className="heatmap-list">
            {heatmapData.map((point, index) => (
              <div key={index} className="heatmap-point">
                <div className="heatmap-location">
                  <strong>Location {index + 1}</strong>
                </div>
                <div className="heatmap-details">
                  <span>
                    📍 Lat: {point.latitude}, Lng: {point.longitude}
                  </span>
                  <span>📦 {point.count} donations</span>
                  <span>⚖️ {point.total_quantity_kg} kg total</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data">
            <p>No donation data available for heatmap</p>
            <p className="hint">
              💡 Donations with location data will appear here
            </p>
          </div>
        )}
      </div>
      <div className="heatmap-note">
        <p>
          💡 For a visual map, integrate with Google Maps API or Leaflet to
          display these coordinates on an interactive map
        </p>
      </div>
    </div>
  )
}

export default Heatmap

