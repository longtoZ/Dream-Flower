import React, { useEffect, useState, useRef } from 'react'

const ExtractLayout = () => {
	const [file, setFile] = useState(null);
	const [loading, setLoading] = useState(false);
	const [images, setImages] = useState([]);
	const eventSource = useRef(null);

	useEffect(() => {
		console.log(images);
	}, [images]);

	const handleDrop = (e) => {
		e.preventDefault();
		e.stopPropagation();
		const droppedFile = e.dataTransfer.files[0]; // Always one file

		if (droppedFile.type !== "application/pdf") {
			alert("Please upload a PDF file");
			return;
		}

		if (droppedFile) setFile(droppedFile);
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
				} else {
					setImages((prevImages) => [...prevImages, e.data]);
				}
			}

			eventSource.current.onerror = (e) => {
				console.error(e);
				eventSource.current.close();
			}
		} catch (error) {
			console.error(error);
		}

	}

	return (
		<div className="w-full px-[10%]">
			<div  onDrop={handleDrop} onDragOver={handleDragOver} className="border border-zinc-800 mt-[100px] p-6 rounded-md flex items-center justify-center flex-col cursor-pointer">
				<h3>Drag and drop your file here to upload</h3>

				<input type="file" accept="application/pdf" className="hidden" onChange={handleSelect}/>
			</div>

			<button onClick={handleUpload} className="mt-4 bg-zinc-500 text-white px-4 py-2 rounded-md">
				Upload File
			</button>

			{images.map((imageData, index) => (
				<img key={index} src={`data:image/png;base64,${imageData}`} alt={`Image ${index + 1}`} />
			))}
		</div>
  	)
}

export default ExtractLayout