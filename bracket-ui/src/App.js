import React, { useState } from "react";
import axios from "axios";

export default function BracketApp() {
  const [bracket, setBracket] = useState(null);

  const generateBracket = async () => {
    try {
      const response = await axios.get("https://bracket-simulator.onrender.com");
      setBracket(response.data);
    } catch (error) {
      console.error("Error fetching bracket:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">🏀 Bracket Simulator 🏀</h1>
      
      <button 
        className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600"
        onClick={generateBracket}
      >
        Generate Bracket
      </button>

      {bracket && (
        <div className="mt-6 w-full max-w-3xl bg-white shadow-lg rounded-lg p-6">
          {["top_left", "bottom_left", "top_right", "bottom_right"].map(region => (
            <div key={region} className="mb-6">
              <h2 className="text-xl font-semibold text-gray-800 border-b pb-2">{bracket[region].region} Region</h2>
              <table className="w-full border-collapse mt-2">
                <tbody>
                  <tr><td className="p-2 font-bold">Round of 32:</td><td>{bracket[region].round_of_32.join(", ")}</td></tr>
                  <tr><td className="p-2 font-bold">Sweet 16:</td><td>{bracket[region].sweet_16.join(", ")}</td></tr>
                  <tr><td className="p-2 font-bold">Elite 8:</td><td>{bracket[region].elite_8.join(", ")}</td></tr>
                  <tr className="bg-blue-100"><td className="p-2 font-bold">Regional Champ:</td><td>{bracket[region].regional_champ}</td></tr>
                </tbody>
              </table>
            </div>
          ))}

          <div className="mt-4 border-t pt-4">
            <h2 className="text-xl font-bold text-gray-900">🏆 Final Four 🏆</h2>
            <p className="text-lg mt-2">Left: <span className="font-semibold">{bracket.final_four.left.region} ({bracket.final_four.left.seed})</span></p>
            <p className="text-lg">Right: <span className="font-semibold">{bracket.final_four.right.region} ({bracket.final_four.right.seed})</span></p>
          </div>

          <div className="mt-4 bg-yellow-100 p-4 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-yellow-700">🏅 National Champion 🏅</h2>
            <p className="text-xl mt-2 font-semibold">{bracket.national_champion.region} ({bracket.national_champion.seed})</p>
          </div>
        </div>
      )}
    </div>
  );
}
