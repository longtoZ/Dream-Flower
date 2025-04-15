import React, { useEffect, useState, useRef, useContext } from 'react'
import { useNavigate } from 'react-router-dom';
import { ConvertToSheetContext } from '../../context/ConvertToSheet';

import SheetNavigator from './components/SheetNavigator';

const ConvertToSheetLayout = () => {
    const rawData = useContext(ConvertToSheetContext).convertToSheet;

    const [musicSheetData, setMusicSheetData] = useState([]);

    useEffect(() => {
        async function fetchMusicSheetData() {
            try {
                const response = await fetch("http://localhost:5000/api/convert-to-sheet", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: rawData,
                });
    
                if (!response.ok) {
                    throw new Error("Network response was not ok " + response.statusText);
                }
    
                const data = await response.json();
                setMusicSheetData(data);
    
            } catch (error) {
                console.error("Error uploading file:", error);
            }
        }
        fetchMusicSheetData();

    }, [rawData]);

    return (
        <div className="p-4 bg-gray-100 h-screen overflow-auto">
            <div className="grid grid-cols-1 gap-4 mb-4">
                <SheetNavigator musicSheetData={musicSheetData} />
            </div>
        </div>
    )
}

export default ConvertToSheetLayout