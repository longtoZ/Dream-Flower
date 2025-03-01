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
		const canvas = canvasRef.current;
        const oldScale = scale;
        const newScale = Math.min(scale + 0.05, 2);
        setScale(newScale);

        // Calculate the center of the canvas
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        // Calculate the change in scale
        const scaleChange = newScale - oldScale;

        // Adjust the starting position to zoom in on the center
		// new_start_pos = old_start_pos - (center_pos - old_start_pos) * scale_change / new_scale
        setStartPos((prevStartPos) => ({
            x: prevStartPos.x - (centerX - prevStartPos.x) * scaleChange / newScale,
            y: prevStartPos.y - (centerY - prevStartPos.y) * scaleChange / newScale,
        }));
	}

	// Zoom out
	const handleZoomOut = () => {
		const canvas = canvasRef.current;
		const oldScale = scale;
		const newScale = Math.max(scale - 0.05, 0.1); // Prevent going below a minimum scale (e.g., 0.1)
		setScale(newScale);
	  
		const centerX = canvas.width / 2;
		const centerY = canvas.height / 2;
	  
		const scaleChange = newScale - oldScale;
	  
		setStartPos((prevStartPos) => ({
			x: prevStartPos.x - (centerX - prevStartPos.x) * scaleChange / newScale,
			y: prevStartPos.y - (centerY - prevStartPos.y) * scaleChange / newScale,
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
		});
	}

	const handleMouseMove = (e) => {
		if (!draggingRef.current) return;
		const canvasRect = canvasRef.current.getBoundingClientRect();
		const coords = getRelativeCoords(e);
		// console.log(coords.x, coords.y, anchor.x, anchor.y)

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

	const drawImageWithFocus = (index, b_x, b_y) => {
		const canvas = canvasRef.current;
		const ctx = canvas.getContext('2d');

		ctx.clearRect(0, 0, canvas.width, canvas.height);

		// Adjust the starting position
		ctx.translate(startPos.x, startPos.y);

		// Set global alpha for dimmed image
		ctx.globalAlpha = 0.5;

		// Draw the image
		ctx.drawImage(image, 0, 0, image.width * scale, image.height * scale);

		// Reset global alpha
		ctx.globalAlpha = 1;

		// Set the color of the box's border
		ctx.strokeStyle = CLASS_COLORS[index];
		ctx.lineWidth = 2;

		boxes[index].forEach((box, _) => {
			const b_width = box[2] - box[0];
			const b_height = box[3] - box[1];
			const b_x = box[0];
			const b_y = box[1];

			// Get the selected zones of the original image but draw with the modified scale
			ctx.drawImage(image, b_x, b_y, b_width, b_height, b_x * scale, b_y * scale, b_width * scale, b_height * scale);
			
			// Draw the box
			ctx.beginPath();
			ctx.strokeRect(b_x * scale, b_y * scale, b_width * scale, b_height * scale);
			ctx.closePath();
		});

		// Add class name of the selected boxes
		ctx.font = `${scale * 20}px Arial`;
		ctx.strokeStyle = CLASS_COLORS[index];
		ctx.lineWidth = 2;
		ctx.strokeText(CLASS_NAMES[index], b_x, b_y);
		ctx.fillStyle = "white";
		ctx.fillText(CLASS_NAMES[index], b_x, b_y);

		// Reset the starting position
		ctx.translate(-startPos.x, -startPos.y);
	}

	const handleMouseClick = (e) => {
		const coords = getRelativeCoords(e);

		// Adjust the coordinates based on the starting position
		coords.x = coords.x - startPos.x;
		coords.y = coords.y - startPos.y;

		let isInsideBox = false;

		// Check if the click is within the bounds of any of the boxes
		boxes.forEach((symbol, index) => {
			if (symbol.length > 0) {
				symbol.forEach((box, _) => {
					const b_x = box[0] * scale;
					const b_y = box[1] * scale;
					const b_width = (box[2] - box[0]) * scale;
					const b_height = (box[3] - box[1]) * scale;

					if (coords.x >= b_x && coords.x <= b_x + b_width && coords.y >= b_y && coords.y <= b_y + b_height) {
						drawImageWithFocus(index, b_x, b_y - 5);
						isInsideBox = true;
						return;
					}
				})
			}

			if (isInsideBox) return;
		})

		// If the click is not within any of the boxes, redraw the image
		if (!isInsideBox) drawImage();
	}

	return (
  		<div className='flex h-[100vh]'>
			<div className='w-[15%] border'></div>
			<div className='w-[85%]'>
				<canvas ref={canvasRef} className='w-full h-full' onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp} onClick={handleMouseClick}>

				</canvas>
			</div>

		</div>
  	)
}

export default EditLayout