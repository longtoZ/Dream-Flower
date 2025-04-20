import { createContext, useContext, useState } from "react";

export const ConvertToSheetContext = createContext();

export const ConvertToSheetProvider = ({children}) => {
    const [convertToSheet, setConvertToSheet] = useState(null);

    return (
        <ConvertToSheetContext.Provider value={{ convertToSheet, setConvertToSheet }}>
            {children}
        </ConvertToSheetContext.Provider>
    );
};