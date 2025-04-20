import { createContext, useContext, useState } from "react";

export const AudioContext = createContext();

export const AudioProvider = ({ children }) => {
    const [audioUrl, setAudioUrl] = useState(null);
    const [jsonData, setJsonData] = useState(null);

    return (
        <AudioContext.Provider value={{ audioUrl, setAudioUrl, jsonData, setJsonData }}>
            {children}
        </AudioContext.Provider>
    );
}