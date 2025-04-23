import React, { useEffect, useState, useRef, useContext } from 'react'
import { ConvertToSheetContext } from '../../context/ConvertToSheet';
import { AudioContext } from '../../context/Audio';
import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';

import SheetNavigator from './components/SheetNavigator';
import AudioPlayer from './components/AudioPlayer';
import NotFound from '../../components/NotFound'

const ConvertToSheetLayout = () => {
    const rawData = useContext(ConvertToSheetContext).convertToSheet;
    const audioUrl = useContext(AudioContext).audioUrl;
    const jsonData = useContext(AudioContext).jsonData;

    const [musicSheetData, setMusicSheetData] = useState([]);

    useEffect(() => {
        document.documentElement.scrollTop = 0;
    }, []);

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

    return rawData ? (
        <>
            <NavBar />
            <div className="p-4 mt-20">
                <div className="grid grid-cols-1 gap-4 mb-4">
                    <SheetNavigator receivedData={musicSheetData} />
                    {audioUrl && <AudioPlayer audioUrl={audioUrl} jsonData={jsonData}/>}
                </div>
            </div>
            <Footer />
        </>
        ) : (
            <NotFound />
        )
}

export default ConvertToSheetLayout