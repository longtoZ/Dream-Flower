import React, { useRef, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom';
import { CLASS_NAMES, CLASS_COLORS, CANVAS_MODE, BOX_ZONE } from '../../config/constants';

import OpenWithIcon from '@mui/icons-material/OpenWith';
import CropFreeIcon from '@mui/icons-material/CropFree';
import SearchIcon from '@mui/icons-material/Search';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';

const EditLayout = () => {
    const canvasRef = useRef(null);
	const location = useLocation();
	const page = location.state?.page;
	const zone = location.state?.zone;

	// Canvas operations
	const [image, setImage] = useState(new Image());
	const [boxes, setBoxes] = useState([]); // Each box is represented as [x1, y1, x2, y2] where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner
	const [scale, setScale] = useState(0.5);
	const [startPos, setStartPos] = useState({x: 0, y: 0});
	const [anchor, setAnchor] = useState({x: 0, y: 0});
	const draggingRef = useRef(false);

	// Focus box operations
	const [focusBoxIndex, setFocusBoxIndex] = useState({symbolIndex: -1, boxIndex: -1});
	const [workingMode, setWorkingMode] = useState(CANVAS_MODE.DRAG);
	const dragModeRef = useRef(CANVAS_MODE.DRAG);
	const editModeRef = useRef(CANVAS_MODE.EDIT);
	const [boxZone, setBoxZone] = useState(BOX_ZONE.OUTSIDE);
	const resizingRef = useRef(false);

	// Search box operations
	const [searchText, setSearchText] = useState("");
	const [currentSymbolBoxes, setCurrentSymbolBoxes] = useState([]);
	const [listSymbolIndex, setListSymbolIndex] = useState(-1);
	const noSelectionRef = useRef(null);
	const searchBoxRef = useRef(null);
	const symbolListRef = useRef(null);

	// Draw the image on the canvas
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
		const retrievedData = JSON.parse(localStorage.getItem('images'));
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

		if (workingMode === CANVAS_MODE.DRAG) {
			drawImage();
		} else if (workingMode === CANVAS_MODE.EDIT) {
			drawImageWithFocus();
		}
	}, [scale, startPos, boxes]);

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
		const coords = getRelativeCoords(e);

		if (workingMode === CANVAS_MODE.DRAG) {
			draggingRef.current = true;

			// Set the anchor point to the current mouse position
			setAnchor({
				x: coords.x,
				y: coords.y,
			});
		} else {
			// Adjust the coordinates based on the starting position
			coords.x = coords.x - startPos.x;
			coords.y = coords.y - startPos.y;

			// Check if the click is within the the focus box
			if (focusBoxIndex.symbolIndex !== -1 && focusBoxIndex.boxIndex !== -1) {
				const focusBox = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];
				const x1 = focusBox[0] * scale, y1 = focusBox[1] * scale;
				const x2 = focusBox[2] * scale, y2 = focusBox[1] * scale;
				const x3 = focusBox[2] * scale, y3 = focusBox[3] * scale;
				const x4 = focusBox[0] * scale, y4 = focusBox[3] * scale;

				// Check if the click is within the handles (to resize) or inside the box (to move)
				const handleEdge = 8;
				let isValidZone = false;

				if (Math.abs(coords.x - x1) <= handleEdge && Math.abs(coords.y - y1) <= handleEdge) {
					isValidZone = true;
					resizingRef.current = true;
					setBoxZone(BOX_ZONE.TOP_LEFT);
				} else if (Math.abs(coords.x - x2) <= handleEdge && Math.abs(coords.y - y2) <= handleEdge) {
					isValidZone = true;
					resizingRef.current = true;
					setBoxZone(BOX_ZONE.TOP_RIGHT);
				} else if (Math.abs(coords.x - x3) <= handleEdge && Math.abs(coords.y - y3) <= handleEdge) {
					isValidZone = true;
					resizingRef.current = true;
					setBoxZone(BOX_ZONE.BOTTOM_RIGHT);
				} else if (Math.abs(coords.x - x4) <= handleEdge && Math.abs(coords.y - y4) <= handleEdge) {
					isValidZone = true;
					resizingRef.current = true;
					setBoxZone(BOX_ZONE.BOTTOM_LEFT);
				} else if (coords.x >= x1 && coords.x <= x3 && coords.y >= y1 && coords.y <= y3) {
					isValidZone = true;
					resizingRef.current = true;
					setBoxZone(BOX_ZONE.INSIDE);
				}

				if (isValidZone) return;
			}
			
			// If the click is not within the focus box, do not proceed resizing or moving
			setBoxZone(BOX_ZONE.OUTSIDE);
			setFocusBoxIndex({symbolIndex: -1, boxIndex: -1});

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
							setFocusBoxIndex({symbolIndex: index, boxIndex: _});
							setSearchText(CLASS_NAMES[index]);
							isInsideBox = true;
							return;
						}
					})
				}

				if (isInsideBox) return;
			})

			// If the click is not within any of the boxes, redraw the image
			if (!isInsideBox) {
				console.log("Click outside box")
				drawImage();
			}
		}
	}

	const handleMouseMove = (e) => {
		const canvasRect = canvasRef.current.getBoundingClientRect();
		const coords = getRelativeCoords(e);
		// console.log(coords.x, coords.y, anchor.x, anchor.y)

		if (workingMode === CANVAS_MODE.DRAG) {
			if (!draggingRef.current) return;

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
		} else {
			if (!resizingRef.current) return;
			if (boxZone === BOX_ZONE.OUTSIDE) return;

			// Adjust the coordinates based on the starting position
			coords.x = coords.x - startPos.x;
			coords.y = coords.y - startPos.y;

			const focusBox = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];

			// Resize the box. On each corner resizing, the opposite corner should remain fixed
			if (boxZone === BOX_ZONE.TOP_LEFT) {
				focusBox[0] = Math.min(focusBox[2], Math.max(0, coords.x / scale));
				focusBox[1] = Math.min(focusBox[3], Math.max(0, coords.y / scale));
			} else if (boxZone === BOX_ZONE.TOP_RIGHT) {
				focusBox[1] = Math.min(focusBox[3], Math.max(0, coords.y / scale));
				focusBox[2] = Math.max(focusBox[0], Math.min(image.width, coords.x / scale));
			} else if (boxZone === BOX_ZONE.BOTTOM_RIGHT) {
				focusBox[2] = Math.max(focusBox[0], Math.min(image.width, coords.x / scale));
				focusBox[3] = Math.max(focusBox[1], Math.min(image.height, coords.y / scale));
			} else if (boxZone === BOX_ZONE.BOTTOM_LEFT) {
				focusBox[0] = Math.min(focusBox[2], Math.max(0, coords.x / scale));
				focusBox[3] = Math.max(focusBox[1], Math.min(image.height, coords.y / scale));
			} else if (boxZone === BOX_ZONE.INSIDE) {
				const b_width = focusBox[2] - focusBox[0];
				const b_height = focusBox[3] - focusBox[1];

				// Limit the box to the image boundaries so that it keeps the size when touching the edges
				focusBox[0] = Math.min(image.width - b_width, Math.max(0, coords.x / scale - b_width / 2));
				focusBox[1] = Math.min(image.height - b_height, Math.max(0, coords.y / scale - b_height / 2));
				focusBox[2] = Math.min(image.width, Math.max(b_width, coords.x / scale + b_width / 2));
				focusBox[3] = Math.min(image.height, Math.max(b_height, coords.y / scale + b_height / 2));
			}

			setBoxes((prevBoxes) => {
				const updatedBoxes = [...prevBoxes];
				updatedBoxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex] = focusBox;
				return updatedBoxes;
			});
		}
	}

	const handleMouseUp = (e) => {
		if (workingMode === CANVAS_MODE.DRAG) {
			draggingRef.current = false;
		} else if (workingMode === CANVAS_MODE.EDIT) {
			resizingRef.current = false;
		}
	}

	const drawImageWithFocus = () => {
		const canvas = canvasRef.current;
		const ctx = canvas.getContext('2d');

		ctx.clearRect(0, 0, canvas.width, canvas.height);

		// Adjust the starting position
		ctx.translate(startPos.x, startPos.y);

		// Set global alpha for dimmed image
		ctx.globalAlpha = 0.5;

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

		// Reset global alpha
		ctx.globalAlpha = 1;

		// Check if the focus box is valid
		if (focusBoxIndex.symbolIndex !== -1 && focusBoxIndex.boxIndex !== -1) {
			// Extract coordinates of corners
			const focusBox = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];
			const x1 = focusBox[0], y1 = focusBox[1];
			const x2 = focusBox[2], y2 = focusBox[1];
			const x3 = focusBox[2], y3 = focusBox[3];
			const x4 = focusBox[0], y4 = focusBox[3];

			// Set the color of the box's border
			ctx.strokeStyle = CLASS_COLORS[focusBoxIndex.symbolIndex];
			ctx.lineWidth = 2;

			boxes[focusBoxIndex.symbolIndex].forEach((box, _) => {
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
			ctx.strokeStyle = CLASS_COLORS[focusBoxIndex.symbolIndex];
			ctx.lineWidth = 2;
			ctx.strokeText(CLASS_NAMES[focusBoxIndex.symbolIndex], x1 * scale, y1 * scale - 5);
			ctx.fillStyle = "white";
			ctx.fillText(CLASS_NAMES[focusBoxIndex.symbolIndex], x1 * scale, y1 * scale - 5);

			// Add handles at four corners
			const handleEdge = 4;

			ctx.beginPath();
			ctx.fillStyle = "white";
			ctx.fillRect(x1 * scale - handleEdge, y1 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.fillRect(x2 * scale - handleEdge, y2 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.fillRect(x3 * scale - handleEdge, y3 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.fillRect(x4 * scale - handleEdge, y4 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.strokeStyle = "black";
			ctx.lineWidth = 1;
			ctx.strokeRect(x1 * scale - handleEdge, y1 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.strokeRect(x2 * scale - handleEdge, y2 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.strokeRect(x3 * scale - handleEdge, y3 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.strokeRect(x4 * scale - handleEdge, y4 * scale - handleEdge, 2 * handleEdge, 2 * handleEdge);
			ctx.closePath();
		}

		// Reset the starting position
		ctx.translate(-startPos.x, -startPos.y);
	}

	// Resize the box when the focusBoxIndex changes
	useEffect(() => {
		if (focusBoxIndex.symbolIndex !== -1 && focusBoxIndex.boxIndex !== -1) {
			noSelectionRef.current.style.display = "none";
			drawImageWithFocus();
		} else {
			noSelectionRef.current.style.display = "flex";
		}
	}, [focusBoxIndex]);

	// Handle switching between drag and edit modes
	const handleModeSwitch = (e) => {

		dragModeRef.current.classList.remove("bg-zinc-300");
		dragModeRef.current.children[0].classList.remove("text-black");
		editModeRef.current.classList.remove("bg-zinc-300");
		editModeRef.current.children[0].classList.remove("text-black");

		if (e.target === dragModeRef.current) {
			dragModeRef.current.classList.add("bg-zinc-300");
			dragModeRef.current.children[0].classList.add("text-black");
			setWorkingMode(CANVAS_MODE.DRAG);
		} else if (e.target === editModeRef.current) {
			editModeRef.current.classList.add("bg-zinc-300");
			editModeRef.current.children[0].classList.add("text-black");
			setWorkingMode(CANVAS_MODE.EDIT);
		}
	}

	const handleTextChange = (e) => {
		setSearchText(e.target.value.toLowerCase());
	}

	const handleSymbolSelect = (e) => {
		const listSymbolIndex = parseInt(e.target.getAttribute("symbol-index"));
		setListSymbolIndex(() => listSymbolIndex);
		setCurrentSymbolBoxes(() => boxes[focusBoxIndex.symbolIndex]);

		// Update the search text
		setSearchText(CLASS_NAMES[listSymbolIndex]);
	}

	const handleSymbolSave = () => {
		const currentBox = currentSymbolBoxes[focusBoxIndex.boxIndex];

		setBoxes((prevBoxes) => {
			const updatedBoxes = [...prevBoxes];
			// Remove the focus box from the current symbol
			updatedBoxes[focusBoxIndex.symbolIndex] = currentSymbolBoxes.filter((_, index) => index !== focusBoxIndex.boxIndex);

			// Add the focus box to the selected symbol
			updatedBoxes[listSymbolIndex].push(currentBox);

			return updatedBoxes;
		});

		// Unfocus all boxes
		setFocusBoxIndex({symbolIndex: -1, boxIndex: -1});
		setSearchText("");
	}

	const handleSymbolDelete = () => {
		setBoxes((prevBoxes) => {
			const updatedBoxes = [...prevBoxes];
			updatedBoxes[focusBoxIndex.symbolIndex] = currentSymbolBoxes.filter((_, index) => index !== focusBoxIndex.boxIndex);
			return updatedBoxes;
		});

		// Unfocus all boxes
		setFocusBoxIndex({symbolIndex: -1, boxIndex: -1});
		setSearchText("");
	}

	// Highlight the symbol in the list when the search text changes
	useEffect(() => {
		if (!symbolListRef.current.children || searchText === "") return;
		
		for (let i = 0; i < symbolListRef.current.children.length; i++) {
			const child = symbolListRef.current.children[i];

			// Highlight the symbol in the list
			if (child.children[1].textContent === searchText) {
				child.classList.add("bg-primary");
				child.classList.add("opacity-[100%]");
			} else {
				child.classList.remove("bg-primary");
				child.classList.remove("opacity-[100%]");
			}
		}

		searchBoxRef.current.value = searchText;
	}, [searchText]);

	return (
  		<div className='flex h-[100vh] bg-primary'>
			<div className='relative w-[16%] bg-secondary'>
				<div className='p-2 absolute flex flex-col justify-center items-center top-0 left-0 w-full h-full bg-[rgba(0,0,0,0.25)] z-10 backdrop-blur-xs' ref={noSelectionRef}>
					<h1 className='text-lg'>No box selected</h1>
					<p className='py-2 text-xs opacity-[40%] text-center'>Click on a box to start editing</p>
				</div>

				<div className='px-1 flex items-center mx-auto mt-10 w-[85%] h-8 bg-primary rounded-md text-sm'>
					<SearchIcon className='m-1' style={{fontSize: "1.2rem"}}/>
					<input type="text" className='text-xs p-1 w-full h-full focus:outline-none' placeholder='Search symbols...' onChange={handleTextChange} ref={searchBoxRef}/>
				</div>

				<div className='mx-auto mt-2 flex justify-between w-[85%]'>
					<div className='w-[48%] bg-transparent rounded-md border border-2 border-primary text-xs text-white p-2 cursor-pointer hover:bg-primary transition-all duration-100 ease' onClick={handleSymbolDelete}>
						<h1 className='text-center'>Delete</h1>
					</div>
					<div className='w-[48%] bg-transparent rounded-md border border-2 border-primary text-xs text-white p-2 cursor-pointer hover:bg-primary transition-all duration-100 ease' onClick={handleSymbolSave}>
						<h1 className='text-center'>Save</h1>
					</div>

				</div>

				<h2 className='mt-6 mb-2 mx-[7.5%] text-xs opacity-[30%] mb-1'>Available symbols</h2>
				<div className='mx-auto w-[85%] flex flex-col overflow-y-scroll h-[80%] scrollbar-hide' ref={symbolListRef}>
					{CLASS_NAMES.map((name, index) => (
						<div className={`grid grid-cols-3 items-center opacity-[30%] cursor-pointer hover:opacity-[100%] hover:bg-primary px-1 py-2 rounded-md transition-all duration-100 ease ${name.includes(searchText) ? 'block' : 'hidden'}`} symbol-index={index} key={index} style={{gridTemplateColumns: "1.5rem 8.6rem 1rem"}} onClick={handleSymbolSelect}> 
							<span className='w-3 h-3 m-1 rounded-[50%] pointer-events-none' style={{backgroundColor: CLASS_COLORS[index]}}></span>
							<p className='text-xs pointer-events-none'>{name}</p>
							<p className='text-xs pointer-events-none'>{boxes[index]?.length}</p>
						</div>
					))}
				</div>
			</div>
			<div className='relative w-[84%]'>
				<canvas ref={canvasRef} className='w-full h-full' onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}>
				</canvas>
				<div className='absolute bottom-3 left-[50%] -translate-x-[50%] h-10 bg-secondary mx-auto mt-4 rounded-lg grid grid-cols-2'>
					<div className='w-10 flex items-center justify-center bg-zinc-300 rounded-md m-1 cursor-pointer transition-all duration-300 ease' ref={dragModeRef} onClick={handleModeSwitch}>
						<h1 className='text-sm text-black font-semibold pointer-events-none transition-all duration-300 ease'>
							<OpenWithIcon />
						</h1>
					</div>
					<div className='w-10 flex items-center justify-center rounded-md m-1 cursor-pointer transition-all duration-300 ease' ref={editModeRef} onClick={handleModeSwitch}>
						<h1 className='text-sm font-semibold pointer-events-none transition-all duration-300 ease'>
							<CropFreeIcon />
						</h1>
					</div>
				</div>
			</div>

		</div>
  	)
}

export default EditLayout