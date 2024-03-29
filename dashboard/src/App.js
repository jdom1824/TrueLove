import React, { useState, useEffect } from 'react';
import './App.css';
import { database } from './firebase-config';
import { ref, onValue } from "firebase/database"; // Importar ref y onValue

function App() {
  const [usersData, setUsersData] = useState([]);

  useEffect(() => {
    const usersRef = ref(database, 'users'); // Actualiza esta línea
    // console.log(usersRef)

    // Escucha por los datos una sola vez
    onValue(usersRef, (snapshot) => { // Cambia usersRef.once a onValue
      const usersSnapshot = snapshot.val();
      console.log(usersSnapshot)
      const usersList = Object.keys(usersSnapshot).map((key) => {
        const userData = usersSnapshot[key];
        const iterations = userData.iterations || {};
        const iterationKeys = Object.keys(iterations);
        const lastIterationKey = iterationKeys[iterationKeys.length - 1];
        const lastIteration = iterations[lastIterationKey] || {};

        return {
          username: userData.username,
          lastIterationNumber: lastIteration.iteration_number || 'N/A',
          walletsPerSecond: lastIteration.wallets_per_second || 'N/A'
        };
      });
      setUsersData(usersList);
    }, {
      onlyOnce: true // Agrega esta opción para escuchar una sola vez
    });
  }, []);

  return (
    <div className="App">
    <header className="App-header">
      <span>DASHBOARD</span><span style={{ color: '#FF1493' }}> TRUELOVE:</span>
      {usersData.map((user, index) => (
      <div key={index} style={{ marginBottom: '15px' }}>
      <span style={{ fontSize: '14px'}} >Username:</span><span style={{ color: '#FF1493', fontSize: '14px' }}> {user.username} </span>
      <span style={{ fontSize: '14px'}} >Iteration Number:</span><span style={{ color: '#FF1493', fontSize: '14px' }}> {user.lastIterationNumber} </span>
      <span style={{ fontSize: '14px'}} >Wallets per Second:</span><span style={{ color: '#FF1493', fontSize: '14px' }}> {user.walletsPerSecond}</span>
      </div>
      ))}
      </header>
    </div>
  );
}

export default App;

