import React, { useRef, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom';
import { CLASS_NAMES, CLASS_COLORS } from '../../config/constants';

const EditLayout = () => {
    const canvasRef = useRef(null);
	const location = useLocation();
	const page = location.state?.page;
	const zone = location.state?.zone;

	const [image, setImage] = useState(new Image());
	const [boxes, setBoxes] = useState([]);
	const [scale, setScale] = useState(0.5);
	const [startPos, setStartPos] = useState({x: 0, y: 0});
	const [anchor, setAnchor] = useState({x: 0, y: 0});
	const draggingRef = useRef(false);

	const drawImage = () => {
		const canvas = canvasRef.current;
		const ctx = canvas.getContext('2d');

		const startX = startPos.x;
		const startY = startPos.y;

		console.log("startX", startX, "startY", startY)

		ctx.clearRect(0, 0, canvas.width, canvas.height);

		// Adjust the starting position
		ctx.translate(startX, startY);

		// Draw the image
		ctx.drawImage(image, 0, 0, image.width * scale, image.height * scale);

		// Draw the boxes
		boxes.forEach((symbol, index) => {
			if (symbol.length > 0) {
				symbol.forEach((box, _) => {
					ctx.beginPath();
					ctx.strokeStyle = CLASS_COLORS[index];
					ctx.lineWidth = 2;
					const b_width = box[2] - box[0];
					const b_height = box[3] - box[1];
					const b_x = box[0];
					const b_y = box[1];
					ctx.rect(b_x * scale, b_y * scale, b_width * scale, b_height * scale);
					ctx.stroke();
					ctx.closePath();
				})
			}
		})

		// Reset the starting position
		ctx.translate(-startX, -startY);
	}

	// Retrieve data from session storage
    useEffect(() => {
		const retrievedData = JSON.parse(window.sessionStorage.getItem('images'));
		const canvasData = retrievedData.find((image) => image.page === page && image.zone === zone);

		const canvas = canvasRef.current;
		const parent = canvas.parentElement;

		canvas.width = parent.getBoundingClientRect().width;
		canvas.height = parent.getBoundingClientRect().height;

        image.src = `data:image/png;base64,${canvasData.image}`;
        image.alt = `Page ${canvasData.page}`;

		setStartPos((startPos) => ({
			x: canvas.width / 2 - image.width * scale/2,
			y: canvas.height / 2 - image.height * scale/2,
		}));

		setBoxes((boxes) => canvasData.boxes);

        image.onload = () => {
			drawImage();
        };

    }, []);

	// Zoom in
	const handleZoomIn = () => {
		const offsetFactorX = Math.abs(startPos.x) * 0.025;
		const offsetFactorY = Math.abs(startPos.y) * 0.025;
		setScale((scale) => Math.min(scale + 0.05, 2));

		// Adjust the starting position to zoom in on the center of the image
		setStartPos((startPos) => ({
			x: startPos.x - offsetFactorX,
			y: startPos.y - offsetFactorY,
		}));
	}

	// Zoom out
	const handleZoomOut = () => {
		const offsetFactorX = Math.abs(startPos.x) * 0.025;
		const offsetFactorY = Math.abs(startPos.y) * 0.025;
		setScale((scale) => Math.max(scale - 0.05, 0.1));

		// Adjust the starting position to zoom out from the center of the image
		setStartPos((startPos) => ({
			x: startPos.x + offsetFactorX,
			y: startPos.y + offsetFactorY,
		}));
	}

	// Redraw image on scale and drag changes
	useEffect(() => {
		if (!image.src) return;
		drawImage();
	}, [scale, startPos]);

	const getRelativeCoords = (e) => {
		const canvas = canvasRef.current;
		const rect = canvas.getBoundingClientRect();
		const x = e.clientX - rect.left;
		const y = e.clientY - rect.top;

		return {x, y};
	}

	const handleWheel = (e) => {
		if (e.deltaY < 0) {
			handleZoomIn();
		} else {
			handleZoomOut();
		}
	}

	const handleMouseDown = (e) => {
		// console.log("mouse down")
		draggingRef.current = true;
		const coords = getRelativeCoords(e);

		// Set the anchor point to the current mouse position
		setAnchor({
			x: coords.x,
			y: coords.y,
		})
	}

	const handleMouseMove = (e) => {
		if (!draggingRef.current) return;
		const canvasRect = canvasRef.current.getBoundingClientRect();
		const coords = getRelativeCoords(e);
		console.log(coords.x, coords.y, anchor.x, anchor.y)

		// If the mouse moves outside the canvas, stop dragging
		if (e.clientX < canvasRect.left || e.clientX > canvasRect.right || e.clientY < canvasRef.current.getBoundingClientRect().top || e.clientY > canvasRef.current.getBoundingClientRect().bottom) {
			draggingRef.current = false;
			return;
		}

		// Calculate the new start position based on the difference between the current mouse position and the anchor point
		setStartPos((prevStartPos) => ({
			x: prevStartPos.x + (coords.x - anchor.x),
			y: prevStartPos.y + (coords.y - anchor.y),
		  }));

		// Update the anchor point
		setAnchor({ x: coords.x, y: coords.y })
	}

	const handleMouseUp = (e) => {
		draggingRef.current = false;
	}

	return (
  		<div className='flex h-[100vh]'>
			<div className='w-[15%] border '></div>
			<div className='w-[85%]'>
				<canvas ref={canvasRef} className='w-full h-full' onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}>

				</canvas>
			</div>

		</div>
  	)
}

export default EditLayout