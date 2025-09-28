// frontend/src/App.js
import React from "react";
import ChatUI from "./components/ChatUI";   // ✅ default import

function App(){
  return (
    <div style={{padding:20, fontFamily:'Segoe UI, sans-serif'}}>
      <h1 style={{textAlign:'center'}}>AI Data Agent</h1>
      <ChatUI />
    </div>
  );
}

export default App;
