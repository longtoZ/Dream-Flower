import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ExtractLayout from './layouts/ExtractLayout/ExtractLayout'
import EditLayout from './layouts/EditLayout/EditLayout';

function App() {
    return (
    	<Router>
			<Routes>
				<Route path="/extract" element={<ExtractLayout />} />
				<Route path="/edit/:id" element={<EditLayout />} />
			</Routes>
		</Router>
    )
}

export default App
