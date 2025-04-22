import React, { useEffect, useState, useRef, useContext } from 'react'
import { ConvertToSheetContext } from '../../context/ConvertToSheet';
import { AudioContext } from '../../context/Audio';

import SheetNavigator from './components/SheetNavigator';
import AudioPlayer from './components/AudioPlayer';
import NotFound from '../../components/NotFound'

const ConvertToSheetLayout = () => {
    const rawData = useContext(ConvertToSheetContext).convertToSheet;
    const audioUrl = useContext(AudioContext).audioUrl;
    const jsonData = useContext(AudioContext).jsonData;

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

    useEffect(() => {
        console.log("JSON Data:", jsonData);
    }, [jsonData]);

    return (
        <div className="p-4 h-screen overflow-auto">
            {rawData ? (
                <div className="grid grid-cols-1 gap-4 mb-4">
                    <SheetNavigator receivedData={musicSheetData} />
                    {audioUrl && <AudioPlayer audioUrl={audioUrl} jsonData={jsonData} />}
                </div>
            ) : (
                <NotFound />
            )
            }

        </div>
    )
}

export default ConvertToSheetLayout