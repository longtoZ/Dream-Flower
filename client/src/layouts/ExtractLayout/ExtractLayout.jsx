import React, { useEffect, useState, useRef, useContext } from 'react'
import { useNavigate } from 'react-router-dom';
import { ConvertToSheetContext } from '../../context/ConvertToSheet';

import NavBar from '../../components/NavBar';
import Footer from '../../components/Footer';
import ImageCard from './components/ImageCard';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ImageSearchIcon from '@mui/icons-material/ImageSearch';

import { toast, ToastContainer } from 'react-toastify';

const ExtractLayout = () => {
	const [file, setFile] = useState(null);
	const fileInputRef = useRef(null);
	const [images, setImages] = useState([]);
	const [isDragging, setIsDragging] = useState(false);
	const eventSource = useRef(null);

	// ConvertToSheet context
	const { setConvertToSheet } = useContext(ConvertToSheetContext);
	const Navigate = useNavigate();

	const [loading, setLoading] = useState(false);
	const [toastId, setToastId] = useState(null);

	useEffect(() => {
		console.log("Images: ", images);
	}, [images]);

	// Load stored images from session storage on component mount
	useEffect(() => {
		const storedImages = localStorage.getItem("images");

		if (storedImages) {
			setImages(JSON.parse(storedImages));
			console.log("Stored images loaded from session storage");
		}

	}, []);

	useEffect(() => {
		if (loading) {
			const id = toast.loading("Extracting images...");
			console.log("Toast ID: ", id);
			setToastId(id);
		} else {
			if (toastId) {
				toast.update(toastId, {
					render: "All images extracted successfully",
					type: "success",
					isLoading: false,
					autoClose: 2000,
				});
				setToastId(null);
			}
		}
	}, [loading]);

	const handleDrop = (e) => {
		e.preventDefault();
		e.stopPropagation();
		const droppedFile = e.dataTransfer.files[0]; // Always one file

		if (droppedFile.type !== "application/pdf") {
			alert("Please upload a PDF file");
			return;
		}

		if (droppedFile) setFile(droppedFile);
		setIsDragging(false);
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
		setIsDragging(true);
	}

	const handleDragLeave = (e) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragging(false);
	}

	const handleUpload = async () => {
		const formData = new FormData();
		formData.append("file", file);

		// Reset images
		setImages([]);
		setLoading(true);

		try {
			// Upload PDF file to server
			const response = await fetch("http://127.0.0.1:5000/api/upload", {
				method: "POST",
				body: formData,
				headers: {
					"Accept": "text/event-stream",
				}
			});

			if (!response.ok) throw new Error("Failed to upload file");

			const data = await response.json();
			const sessionId = data["session_id"];

			// Start listening for server-sent events
			eventSource.current = new EventSource(`http://127.0.0.1:5000/api/stream/${sessionId}`);

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
		<>
			<ToastContainer
				position='bottom-right'
				autoClose={2000}
				hideProgressBar={false}
				closeOnClick={true}
				pauseOnHover={false}
				toastStyle={{ backgroundColor: "#30323b", color: "white" }}
			/>
			<NavBar/>
			<div className="w-full px-[10%] py-10">
				{/* File Drop/Select Area */}
				<div
					onDrop={handleDrop}
					onDragOver={handleDragOver}
					onDragLeave={handleDragLeave} // Add drag leave handler
					onClick={() => fileInputRef.current && fileInputRef.current.click()}
					className={`border mt-[150px] h-72 p-6 rounded-md flex items-center justify-center flex-col cursor-pointer bg-secondary border-dashed border-tertiary border-2 transition-all duration-300 ${
						isDragging
						? "shadow-[0_0_15px_5px_rgba(255,255,255,0.5)]"
						: "border-tertiary"
					}`} // Dynamic glow based on drag state
					style={{ position: "relative" }}
					>
					{file ? (
						<>
						<h3 className="text-gray-200 mb-2">{file.name}</h3>
						<p className="text-gray-400 opacity-50 text-sm">Click to change file</p>
						<PictureAsPdfIcon
							className="text-white opacity-30 mt-4"
							style={{ fontSize: "4rem" }}
						/>
						</>
					) : (
						<>
						<h3 className="text-gray-200 mb-2">Drag or drop your file here to upload</h3>
						<p className="text-gray-400 opacity-50 text-sm">Only support .pdf format</p>
						<CloudUploadIcon
							className="text-white opacity-30 mt-4"
							style={{ fontSize: "4rem" }}
						/>
						</>
					)}
					<input
						type="file"
						accept="application/pdf"
						className="hidden"
						onChange={handleSelect}
						ref={fileInputRef}
					/>
					</div>

				<div className='flex gap-2 mt-4'>
					<button className='bg-transparent text-gray-300 border border-2 border-primary rounded-md py-2 px-3 hover:bg-primary transition duration-100 cursor-pointer' onClick={() => setFile(null)} disabled={!file}>
						Delete File
					</button>
					<button onClick={handleUpload} className="float-button">
						Upload File
					</button>
				</div>
				
				{/* Extracted Images Section */}
				<div className='mt-40 mb-6'>
					<h1 className='text-2xl font-bold text-white mb-2'>Extracted Images</h1>
					<p className='text-sm text-gray-400'>
						Here are the images extracted from the PDF file. You can click on each image to view it in full size. You can also edit the boxes inside the image by clicking on them. 
						Once you are done, click on the "Save" button to save the changes.
					</p>
				</div>

				{/* Images Grid */}
				{images.length === 0 ? (
					<div className='flex flex-col justify-center items-center mt-10'>
						<ImageSearchIcon className="text-gray-400 opacity-30 mb-8 mt-20" style={{fontSize: "5rem"}}/>
						<p className='text-gray-400'>No images extracted yet. Please upload a PDF file.</p>
					</div>
				) : (
					<>
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
					</>
				)}
			</div>
			<Footer/>
		</>
	)
}

export default ExtractLayout