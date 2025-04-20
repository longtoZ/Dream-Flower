import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ExtractLayout from './layouts/ExtractLayout/ExtractLayout'
import EditLayout from './layouts/EditLayout/EditLayout';
import ConvertToSheetLayout from './layouts/ConvertToSheetLayout/ConvertToSheetLayout';
import { ConvertToSheetProvider } from './context/ConvertToSheet';
import { AudioProvider } from './context/Audio';

import './style.css'

function App() {
    return (
		<ConvertToSheetProvider>
			<AudioProvider>
				<Router>
					<Routes>
						<Route path="/extract" element={<ExtractLayout />} />
						<Route path="/edit/:id" element={<EditLayout />} />
						<Route path="/convert-to-sheet/:id" element={<ConvertToSheetLayout />} />
					</Routes>
				</Router>
			</AudioProvider>
		</ConvertToSheetProvider>
    )
}

export default App
