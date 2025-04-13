import { createContext, useContext, useState } from "react";

export const ConvertToSheetContext = createContext();

export const ConvertToSheetProvider = ({ children }) => {
    const [convertToSheet, setConvertToSheet] = useState(null);

    return (
        <ConvertToSheetContext.Provider value={{ convertToSheet, setConvertToSheet }}>
            {children}
        </ConvertToSheetContext.Provider>
    );
};

export const useConvertToSheet = () => {
    const context = useContext(ConvertToSheetContext);
    if (!context) {
        throw new Error("useConvertToSheet must be used within a ConvertToSheetProvider");
    }
    return context;
};