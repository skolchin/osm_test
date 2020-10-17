import React, { useEffect } from 'react';

import Home from './Home';
import './App.css';

import { AppContext, AppReducer } from './app_context';

function App() {
  const [state, dispatch] = AppReducer();

  useEffect(() => {
    fetch('roads.json')
    .then(res => {
      if (res.ok)
        return res.json();
      throw res;
    })
    .then(resJson => {
      dispatch({type: 'LOAD_ROADS', payload: resJson})
    })
    .catch(error => {
      console.log(`Error loading roads list, falling back to default: ${error}`)
    })
}, [dispatch]);

  
  return (
    <div className="App">
      <AppContext.Provider value={[state, dispatch]}>
        <Home />
      </AppContext.Provider>
    </div>
  );
}

export default App;
