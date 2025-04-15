import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ExtractLayout from './layouts/ExtractLayout/ExtractLayout'
import EditLayout from './layouts/EditLayout/EditLayout';
import ConvertToSheetLayout from './layouts/ConvertToSheetLayout/ConvertToSheetLayout';
import { ConvertToSheetProvider } from './context/ConvertToSheet';

function App() {
    return (
		<ConvertToSheetProvider>
			<Router>
				<Routes>
					<Route path="/extract" element={<ExtractLayout />} />
					<Route path="/edit/:id" element={<EditLayout />} />
					<Route path="/convert-to-sheet/:id" element={<ConvertToSheetLayout />} />
				</Routes>
			</Router>
		</ConvertToSheetProvider>
    )
}

export default App
