import React, { useEffect, useState, useRef, useContext } from 'react'
import { useNavigate } from 'react-router-dom';
import { ConvertToSheetContext } from '../../context/ConvertToSheet';

import ImageCard from './components/ImageCard';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ExtractLayout = () => {
	const [file, setFile] = useState(null);
	const [loading, setLoading] = useState(false);
	const [images, setImages] = useState([]);
	const eventSource = useRef(null);

	// ConvertToSheet context
	const { setConvertToSheet } = useContext(ConvertToSheetContext);
	const Navigate = useNavigate();

	useEffect(() => {
		console.log(images);
	}, [images]);

	// Load stored images from session storage on component mount
	useEffect(() => {
		const storedImages = localStorage.getItem("images");

		if (storedImages) {
			setImages(JSON.parse(storedImages));
			console.log("Stored images loaded from session storage");
		}

	}, []);

	const handleDrop = (e) => {
		e.preventDefault();
		e.stopPropagation();
		const droppedFile = e.dataTransfer.files[0]; // Always one file

		if (droppedFile.type !== "application/pdf") {
			alert("Please upload a PDF file");
			return;
		}

		if (droppedFile) setFile(droppedFile);
		console.log(droppedFile);
	}

	const handleSelect = (e) => {
		const selectedFile = e.target.files[0]; // Always one file

		if (selectedFile.type !== "application/pdf") {
			alert("Please upload a PDF file");
			return;
		}

		if (selectedFile) setFile(selectedFile);
	}

	const handleDragOver = (e) => {
		e.preventDefault();
		e.stopPropagation();
	}

	const handleUpload = async () => {
		const formData = new FormData();
		formData.append("file", file);

		// Reset images
		setImages([]);
		setLoading(true);

		try {
			// Upload PDF file to server
			const response = await fetch("http://127.0.0.1:5000/extract", {
				method: "POST",
				body: formData,
				headers: {
					"Accept": "text/event-stream",
				}
			});

			if (!response.ok) throw new Error("Failed to upload file");

			// Start listening for server-sent events
			eventSource.current = new EventSource("http://127.0.0.1:5000/stream");

			eventSource.current.onmessage = (e) => {

				if (e.data === "done") {
					eventSource.current.close();
					setLoading(false);
				} else {
					setImages((prevImages) => {
						const updatedImages = [...prevImages, JSON.parse(e.data)];
						
						// Store images in session storage
						localStorage.setItem("images", JSON.stringify(updatedImages));
						console.log("Images stored in session storage");

						return updatedImages;
					});
				}
			}

			eventSource.current.onerror = (e) => {
				console.error(e);
				eventSource.current.close();
				setLoading(false);
			}
		} catch (error) {
			console.error(error);
		}

		setLoading(false);

	}

	const handleConvert = () => {
		// Get the boxes data from session storage
		const storedImages = localStorage.getItem("images");

		// Store the data in the ConvertToSheet context
		setConvertToSheet(storedImages);

		// Get the filename from the file object
		const filename = images[0].filename;

		// Navigate to the ConvertToSheet page with the filename as a parameter
		Navigate(`/convert-to-sheet/${filename}`, {state: {filename}});
	}

	return (
		<div className="w-full px-[10%] py-10">
			<div onDrop={handleDrop} onDragOver={handleDragOver} className="border mt-[100px] h-60 p-6 rounded-md flex items-center justify-center flex-col cursor-pointer bg-secondary border-dashed border-tertiary border-2">
				<h3 className="opacity-30">
					Drag and drop your file here to upload
				</h3>
				<CloudUploadIcon className="text-white opacity-30 mt-4" style={{fontSize: "3.5rem"}}/>

				<input type="file" accept="application/pdf" className="hidden" onChange={handleSelect}/>
			</div>

			<button onClick={handleUpload} className="mt-4 float-button">
				Upload File
			</button>

			<div className='mt-20'></div>
			<div className='grid grid-cols-4 gap-4'>
				{images.map((imageData, index) => (
					<ImageCard key={index} filename={imageData.filename} page={imageData.page} zone={imageData.zone} data={imageData.image} boxes={imageData.boxes}/>
				))}
			</div>
			
			<div className='mt-20 w-full flex justify-center items-center'>
				<button onClick={handleConvert} className="float-button">
					Convert to Sheet
				</button>
			</div>

		</div>
  	)
}

export default ExtractLayout