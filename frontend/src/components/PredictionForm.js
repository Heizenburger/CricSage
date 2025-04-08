import React, { useState } from 'react';
import axios from 'axios';

const teamAbbreviations = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "Punjab Kings": "PBKS",
    "Sunrisers Hyderabad": "SRH"
};

const PredictionForm = () => {
    const [teams] = useState([
      'Mumbai Indians', 'Chennai Super Kings', 
      'Royal Challengers Bangalore', 'Kolkata Knight Riders',
      'Rajasthan Royals', 'Delhi Capitals', 'Gujarat Titans', 'Lucknow Super Giants', 'Punjab Kings', 'Sunrisers Hyderabad'
    ]);
    
    const [venues] = useState([
        'MA Chidambaram Stadium, Chennai',
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur, Chandigarh',
        'Eden Gardens, Kolkata',
        'Sawai Mansingh Stadium, Jaipur',
        'Narendra Modi Stadium, Ahmedabad',
        'M.Chinnaswamy Stadium, Bengaluru',
        'Rajiv Gandhi International Stadium, Hyderabad',
        'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam',
        'Wankhede Stadium, Mumbai',
        'Arun Jaitley Stadium, Delhi',
        'Himachal Pradesh Cricket Association Stadium, Dharamsala',
        'Barsapara Cricket Stadium, Guwahati',
        'Punjab Cricket Association IS Bindra Stadium, Mohali',
        'Brabourne Stadium, Mumbai',
        'Dr DY Patil Sports Academy, Mumbai',
        'Maharashtra Cricket Association Stadium, Pune'
    ]);

    const [selectedTeam1, setSelectedTeam1] = useState('');
    const [selectedTeam2, setSelectedTeam2] = useState('');
    const [selectedVenue, setSelectedVenue] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Update handlePredict to fetch player predictions
const handlePredict = async () => {
    try {
      setIsLoading(true);
      const team1Abbr = teamAbbreviations[selectedTeam1];
      const team2Abbr = teamAbbreviations[selectedTeam2];
  
      // Get both predictions in parallel
      const [matchResponse, playersResponse] = await Promise.all([
        axios.post('http://localhost:5000/api/predict', {
          team1: team1Abbr,
          team2: team2Abbr,
          venue: selectedVenue
        }),
        axios.post('http://localhost:5000/api/predict_players', {
          team1: team1Abbr,
          team2: team2Abbr,
          venue: selectedVenue
        })
      ]);
  
      // Merge responses
      setPrediction({
        ...matchResponse.data,
        keyPlayers: playersResponse.data.key_players
      });
  
    } catch (err) {
      console.error('Prediction Error:', err);
      setError(err.response?.data?.error || err.message);
    } finally {
      setIsLoading(false);
    }
  };

    const renderProbabilityBar = (team, probability) => (
        <div className="team-prob">
            <span>{team}: </span>
            <strong>{probability}</strong>
        </div>
    );

    const renderKeyPlayers = () => {
        if (!prediction?.keyPlayers) return null;

        return (
            <div className="key-players">
                <h4>Key Players to Watch:</h4>
                <div className="players-grid">
                    {Object.entries(prediction.keyPlayers).map(([player, prob]) => (
                        <div key={player} className="player-card">
                            <h5>{player}</h5>
                            <div className="performance-meter">
                                <div className="meter-bar" style={{ width: prob }}>
                                    {prob}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="prediction-container">
            <h2>IPL Match Predictor</h2>
            
            <div className="selection-panel">
                <select 
                    value={selectedTeam1}
                    onChange={(e) => setSelectedTeam1(e.target.value)}
                    disabled={isLoading}
                >
                    <option value="">Select Team 1</option>
                    {teams.map(team => (
                        <option key={team} value={team}>{team}</option>
                    ))}
                </select>

                <select 
                    value={selectedTeam2}
                    onChange={(e) => setSelectedTeam2(e.target.value)}
                    disabled={isLoading}
                >
                    <option value="">Select Team 2</option>
                    {teams.map(team => (
                        <option key={team} value={team}>{team}</option>
                    ))}
                </select>

                <select 
                    value={selectedVenue}
                    onChange={(e) => setSelectedVenue(e.target.value)}
                    disabled={isLoading}
                >
                    <option value="">Select Venue</option>
                    {venues.map(venue => (
                        <option key={venue} value={venue}>{venue}</option>
                    ))}
                </select>

                <button 
                    onClick={handlePredict}
                    disabled={!selectedTeam1 || !selectedTeam2 || !selectedVenue || isLoading}
                >
                    {isLoading ? 'Predicting...' : 'Predict'}
                </button>
            </div>

            {error && (
                <div className="error-message">
                    <h3>Error:</h3>
                    <p>{error.includes('{') ? JSON.parse(error).error : error}</p>
                </div>
            )}

            {prediction && (
                <div className="prediction-result">
                    <h3>{prediction.team1} vs {prediction.team2}</h3>
                    <p className="venue">Venue: {selectedVenue}</p>
                    
                    <div className="win-probability">
                        <h4>Win Probability:</h4>
                        <div className="probability-bars">
                            {renderProbabilityBar(prediction.team1, prediction.winProbability[prediction.team1])}
                            {renderProbabilityBar(prediction.team2, prediction.winProbability[prediction.team2])}
                        </div>
                    </div>

                    <div className="score-prediction">
                        <h4>Predicted Score Range:</h4>
                        <p>{prediction.predictedScore}</p>
                    </div>

                    {renderKeyPlayers()}
                </div>
            )}
        </div>
    );
};

export default PredictionForm;