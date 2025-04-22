import React, { useRef, useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom';
import { TIME_CLASS_NAMES, CLASS_NAMES, CLASS_COLORS, CANVAS_MODE, BOX_ZONE } from '../../config/constants';

import ConfirmDialog from './components/ConfirmDialog';

import OpenWithIcon from '@mui/icons-material/OpenWith';
import CropFreeIcon from '@mui/icons-material/CropFree';
import SearchIcon from '@mui/icons-material/Search';
import ContentCutIcon from '@mui/icons-material/ContentCut';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';

const EditLayout = () => {
	const navigate = useNavigate();

    const canvasRef = useRef(null);
	const location = useLocation();
	const filename = location.state?.filename;
	const page = location.state?.page;
	const zone = location.state?.zone;

	// Page number operations
	const [prevPage, setPrevPage] = useState(null);
	const [nextPage, setNextPage] = useState(null);

	// Canvas operations
	const [image, setImage] = useState(new Image());
	const [boxes, setBoxes] = useState([]); // Each box is represented as [x1, y1, x2, y2] where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner
	const [staffLines, setStaffLines] = useState([]);
	const [scale, setScale] = useState(0.5);
	const [startPos, setStartPos] = useState({x: 0, y: 0});
	const [anchor, setAnchor] = useState({x: 0, y: 0});
	const draggingRef = useRef(false);

	// Focus box operations
	const [focusBoxIndex, setFocusBoxIndex] = useState({symbolIndex: -1, boxIndex: -1});
	const [prevFocusBoxIndex, setPrevFocusBoxIndex] = useState({symbolIndex: 0, boxIndex: 0});
	const [workingMode, setWorkingMode] = useState(CANVAS_MODE.DRAG);
	const dragModeRef = useRef(CANVAS_MODE.DRAG);
	const editModeRef = useRef(CANVAS_MODE.EDIT);
	const cutModeRef = useRef(CANVAS_MODE.CUT);
	const [boxZone, setBoxZone] = useState(BOX_ZONE.OUTSIDE);
	const resizingRef = useRef(false);

	// Search box operations
	const [searchText, setSearchText] = useState("");
	// const [currentSymbolBoxes, setCurrentSymbolBoxes] = useState([]);
	const [listSymbolIndex, setListSymbolIndex] = useState(-1);
	const noSelectionRef = useRef(null);
	const searchBoxRef = useRef(null);
	const symbolListRef = useRef(null);

	// Confirm dialog operations
	const [dialogHeadMessage, setDialogHeadMessage] = useState("");
	const [dialogSubMessage, setDialogSubMessage] = useState("");
	const [isDialogOpen, setDialogOpen] = useState(false);
	const [cutPosition, setCutPosition] = useState({x: 0, y: 0});

	// Draw the image on the canvas
	const drawImage = () => {
		const canvas = canvasRef.current;
		const ctx = canvas.getContext('2d');

		const startX = startPos.x;
		const startY = startPos.y;

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
		const canvasDataIndex = retrievedData.findIndex((image) => image.page === page && image.zone === zone);
		const canvasData = retrievedData[canvasDataIndex];
		const prevCanvasData = canvasDataIndex > 0 ? retrievedData[canvasDataIndex - 1] : null;
		const nextCanvasData = canvasDataIndex < retrievedData.length - 1 ? retrievedData[canvasDataIndex + 1] : null;

		// Set the page number and total pages
		if (prevCanvasData) {
			setPrevPage({page: prevCanvasData.page, zone: prevCanvasData.zone});
		}
		if (nextCanvasData) {
			setNextPage({page: nextCanvasData.page, zone: nextCanvasData.zone});
		}

		const canvas = canvasRef.current;
		const parent = canvas.parentElement;

		canvas.width = parent.getBoundingClientRect().width;
		canvas.height = parent.getBoundingClientRect().height;

        image.src = `data:image/png;base64,${canvasData.image}`;
        image.alt = `Page ${canvasData.page} Zone ${canvasData.zone}`;

		setStartPos(() => ({
			x: canvas.width / 2 - image.width * scale/2,
			y: canvas.height / 2 - image.height * scale/2,
		}));

		// Add boxes for TIME_CLASS_NAMES
		TIME_CLASS_NAMES.forEach(() => canvasData.boxes.push([]));

		setBoxes(() => canvasData.boxes);
		setStaffLines(() => canvasData.staff_lines);

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

	// Insert the cut images into local storage
	const insertCutImage = (cutImages) => {
		const retrievedData = JSON.parse(localStorage.getItem('images'));
		const originalIndex = retrievedData.findIndex((image) => image.page === page && image.zone === zone);

		// Set the filename for the new images
		const filename = retrievedData[originalIndex].filename;
		cutImages.forEach((image) => {
			image.filename = filename;
		});

		// Delete the original image and insert two new images
		retrievedData.splice(originalIndex, 1, ...cutImages);

		// Update the zone count
		let zoneCount = 1;
		retrievedData.forEach((image) => {
			if (image.page === page) {
				image.zone = zoneCount++;
			}
		});

		localStorage.setItem('images', JSON.stringify(retrievedData));

	}

	// Cut image into two halves
	const cutImage = () => {
		const tempCanvas = document.createElement('canvas');
		const tempCtx = tempCanvas.getContext('2d');

		// Set the canvas size to the image size
		const width = image.width;
		const height = image.height;
		tempCanvas.width = width;
		tempCanvas.height = cutPosition.y / scale;
		
		// Above half
		tempCtx.drawImage(image, 0, 0, width, cutPosition.y / scale, 0, 0, width, cutPosition.y / scale);
		const aboveHalf = tempCanvas.toDataURL('image/png').replace("data:image/png;base64,", "");

		// Clear the canvas
		tempCtx.clearRect(0, 0, width, height);

		// Update the height
		tempCanvas.height = height - cutPosition.y / scale;

		// Below half
		tempCtx.drawImage(image, 0, cutPosition.y / scale, width, height - cutPosition.y / scale, 0, 0, width, height - cutPosition.y / scale);
		const belowHalf = tempCanvas.toDataURL('image/png').replace("data:image/png;base64,", "");

		// Create boxes for the above and below halves
		const aboveHalfBoxes = boxes.map((symbol) => {
			return symbol.filter((box) => box[3] <= cutPosition.y / scale);
		});

		const belowHalfBoxes = boxes.map((symbol) => {
			return symbol.filter((box) => box[1] >= cutPosition.y / scale).map((box) => {
				return [box[0], box[1] - cutPosition.y / scale, box[2], box[3] - cutPosition.y / scale];
			});
		});

		// Create staff lines for the above and below halves
		const aboveHalfStaffLines = staffLines.filter((line) => line[1] <= cutPosition.y / scale);
		const belowHalfStaffLines = staffLines.filter((line) => line[1] >= cutPosition.y / scale).map((line) => {
			return [line[0], line[1] - cutPosition.y / scale, line[2], line[3] - cutPosition.y / scale];
		});

		// Create a map for the above and below halves
		const aboveHalfMap = {
			filename: "",
			page: page,
			zone: zone,
			image: aboveHalf,
			boxes: aboveHalfBoxes,
			staff_lines: aboveHalfStaffLines,
		};

		const belowHalfMap = {
			filename: "",
			page: page,
			zone: zone,
			image: belowHalf,
			boxes: belowHalfBoxes,
			staff_lines: belowHalfStaffLines,
		}

		// Insert the cut images into local storage
		insertCutImage([aboveHalfMap, belowHalfMap]);

		// Exit the page
		navigate(-1);
	}

	// Redraw image on scale and drag changes
	useEffect(() => {
		if (!image.src) return;

		if (workingMode === CANVAS_MODE.DRAG) {
			drawImage();
		} else if (workingMode === CANVAS_MODE.EDIT) {
			drawImageWithFocus();
		} else if (workingMode === CANVAS_MODE.CUT) {
			setFocusBoxIndex({symbolIndex: -1, boxIndex: -1});
		}
	}, [scale, startPos, boxes, workingMode]);

	const getRelativeCoords = (e) => {
		const canvas = canvasRef.current;
		const rect = canvas.getBoundingClientRect();
		const x = e.clientX - rect.left;
		const y = e.clientY - rect.top;

		return {x, y};
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
		if (focusBoxIndex.symbolIndex !== -1 && focusBoxIndex.boxIndex > -1 && focusBoxIndex.boxIndex < boxes[focusBoxIndex.symbolIndex].length) {
			// Extract coordinates of corners
			const focusBox = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];
			const x1 = focusBox[0], y1 = focusBox[1];
			const x2 = focusBox[2], y2 = focusBox[1];
			const x3 = focusBox[2], y3 = focusBox[3];
			const x4 = focusBox[0], y4 = focusBox[3];

			// Set the color of the box's border
			ctx.strokeStyle = CLASS_COLORS[focusBoxIndex.symbolIndex];
			ctx.lineWidth = 2;

			// Draw the selected zones except the focus box
			boxes[focusBoxIndex.symbolIndex].forEach((box, _) => {
				if (_ !== focusBoxIndex.boxIndex) {
					const b_width = box[2] - box[0];
					const b_height = box[3] - box[1];
					const b_x = box[0];
					const b_y = box[1];
	
					// Get the selected zones of the original image but draw with the modified scale
					ctx.drawImage(image, b_x, b_y, b_width, b_height, b_x * scale, b_y * scale, b_width * scale, b_height * scale);
					
					// Draw the box
					ctx.beginPath();
					ctx.rect(b_x * scale, b_y * scale, b_width * scale, b_height * scale);
					ctx.stroke();
					ctx.closePath();
				}
			});

			// Draw the focus box last so that it appears on top of the other boxes
			if (focusBoxIndex.boxIndex !== -1) {
				const box = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];
				const b_width = box[2] - box[0];
				const b_height = box[3] - box[1];
				const b_x = box[0];
				const b_y = box[1];

				// Get the selected zones of the original image but draw with the modified scale
				ctx.drawImage(image, b_x, b_y, b_width, b_height, b_x * scale, b_y * scale, b_width * scale, b_height * scale);

				// Draw the box
				ctx.beginPath();
				ctx.rect(b_x * scale, b_y * scale, b_width * scale, b_height * scale);
				ctx.stroke();
				ctx.closePath();
			}

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
				console.log("Click inside box", focusBoxIndex.symbolIndex, focusBoxIndex.boxIndex, focusBox);
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
							setPrevFocusBoxIndex({symbolIndex: index, boxIndex: _});
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
				// Create a new box
				setAnchor({x: coords.x, y: coords.y});

				// Temporarily set the focus box index to the last box in the current symbol
				setFocusBoxIndex({symbolIndex: prevFocusBoxIndex.symbolIndex, boxIndex: boxes[prevFocusBoxIndex.symbolIndex].length});
				setPrevFocusBoxIndex({symbolIndex: prevFocusBoxIndex.symbolIndex, boxIndex: boxes[prevFocusBoxIndex.symbolIndex].length});
				setSearchText(CLASS_NAMES[prevFocusBoxIndex.symbolIndex]);
				resizingRef.current = true;

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
		} else if (workingMode === CANVAS_MODE.EDIT) {
			if (!resizingRef.current) return;

			// Adjust the coordinates based on the starting position
			coords.x = coords.x - startPos.x;
			coords.y = coords.y - startPos.y;

			if (boxZone === BOX_ZONE.OUTSIDE) {
				// If the box is being created, its corners' coordinate should not be limited to the image boundaries. 
				const x1 = Math.min(anchor.x, coords.x) / scale;
				const y1 = Math.min(anchor.y, coords.y) / scale;
				const x2 = Math.max(anchor.x, coords.x) / scale;
				const y2 = Math.max(anchor.y, coords.y) / scale;

				const newBox = [x1, y1, x2, y2];

				// If the box is too small, do not create it
				if (x2 - x1 < 5 || y2 - y1 < 5) {
					console.log("Box too small")
					return;
				}

				setBoxes((prevBoxes) => {
					const updatedBoxes = [...prevBoxes];
					
					// If the box was not created, add a new box to the current symbol
					if (prevFocusBoxIndex.boxIndex === boxes[prevFocusBoxIndex.symbolIndex].length) {
						updatedBoxes[prevFocusBoxIndex.symbolIndex].push(newBox);
					} else {
						// Otherwise, update the box
						updatedBoxes[prevFocusBoxIndex.symbolIndex][prevFocusBoxIndex.boxIndex] = newBox;
					}
					return updatedBoxes;
				});

				console.log("New box", newBox);

			} else {
				// If the box is being resized, its corners' coordinate should be limited to the image boundaries.
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

				// If the box is too small, do not resize it
				if (focusBox[2] - focusBox[0] < 5 || focusBox[3] - focusBox[1] < 5) return;
	
				setBoxes((prevBoxes) => {
					const updatedBoxes = [...prevBoxes];
					updatedBoxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex] = focusBox;
					return updatedBoxes;
				});
			}

		} else if (workingMode === CANVAS_MODE.CUT) {
			// Don't draw the dashed line if the mouse is outside the image
			if (coords.x < startPos.x || coords.x > image.width * scale + startPos.x || coords.y < startPos.y || coords.y > image.height * scale + startPos.y) return;

			// Stick a dashed line to the mouse cursor
			const canvas = canvasRef.current;
			const ctx = canvas.getContext('2d');

			drawImageWithFocus();
		
			ctx.beginPath();
			ctx.setLineDash([10, 5]); // Dashed line pattern
			ctx.moveTo(startPos.x, coords.y); // Fixed starting point
			ctx.lineTo(image.width * scale + startPos.x, coords.y); // Follow the mouse cursor
			ctx.strokeStyle = "red";
			ctx.lineWidth = 2;
			ctx.stroke();

			// Reset the line to a solid line
			ctx.setLineDash([]);

			ctx.closePath();

		}
	}

	const handleMouseUp = (e) => {
		if (workingMode === CANVAS_MODE.DRAG) {
			draggingRef.current = false;
		} else if (workingMode === CANVAS_MODE.EDIT) {
			resizingRef.current = false;

			// Focus on search box and select all text
			if (focusBoxIndex.symbolIndex !== -1 && focusBoxIndex.boxIndex !== -1) {
				searchBoxRef.current.focus();
				searchBoxRef.current.select();
			}
			
			// If the box was not created, reset the focus box index
			if (prevFocusBoxIndex.boxIndex === boxes[prevFocusBoxIndex.symbolIndex].length) {
				setFocusBoxIndex({symbolIndex: prevFocusBoxIndex.symbolIndex, boxIndex: boxes[prevFocusBoxIndex.symbolIndex].length - 1});
				setPrevFocusBoxIndex({symbolIndex: prevFocusBoxIndex.symbolIndex, boxIndex: boxes[prevFocusBoxIndex.symbolIndex].length - 1});
			}
		} else if (workingMode === CANVAS_MODE.CUT) {
			const coords = getRelativeCoords(e);
			setCutPosition({x: coords.x - startPos.x, y: coords.y - startPos.y});
			console.log("Cut position", coords.x - startPos.x, coords.y - startPos.y, image.width * scale, image.height * scale)

			// Update the messages of the dialog
			setDialogHeadMessage("Are you sure to cut the image?");
			setDialogSubMessage("The image will be cut into two halves. The original image will be deleted.");

			// Show the confirmation dialog
			setDialogOpen(true);
		}
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
		cutModeRef.current.classList.remove("bg-zinc-300");
		cutModeRef.current.children[0].classList.remove("text-black");

		if (e.target === dragModeRef.current) {
			dragModeRef.current.classList.add("bg-zinc-300");
			dragModeRef.current.children[0].classList.add("text-black");
			setWorkingMode(CANVAS_MODE.DRAG);
		} else if (e.target === editModeRef.current) {
			editModeRef.current.classList.add("bg-zinc-300");
			editModeRef.current.children[0].classList.add("text-black");
			setWorkingMode(CANVAS_MODE.EDIT);
		} else if (e.target === cutModeRef.current) {
			cutModeRef.current.classList.add("bg-zinc-300");
			cutModeRef.current.children[0].classList.add("text-black");
			setWorkingMode(CANVAS_MODE.CUT);
		}
	}

	const handleTextChange = (e) => {
		setSearchText(e.target.value.toLowerCase());
	}

	const handleSymbolSelect = (e) => {
		const listSymbolIndex = parseInt(e.target.getAttribute("symbol-index"));

		// Update the search text
		setSearchText(CLASS_NAMES[listSymbolIndex]);
	}

	const handleSymbolSave = () => {
		const currentBox = boxes[focusBoxIndex.symbolIndex][focusBoxIndex.boxIndex];
		const currentSymbolBoxes = boxes[focusBoxIndex.symbolIndex];

		setBoxes((prevBoxes) => {
			const updatedBoxes = [...prevBoxes];

			// Remove the focus box from the current symbol
			updatedBoxes[focusBoxIndex.symbolIndex] = currentSymbolBoxes.filter((_, index) => index !== focusBoxIndex.boxIndex);

			// Add the focus box to the selected symbol
			// Avoid adding duplicate boxes by checking if the last box is the same as the current box
			if (updatedBoxes[listSymbolIndex].length === 0 || updatedBoxes[listSymbolIndex][updatedBoxes[listSymbolIndex].length - 1].join() !== currentBox.join()) {
				updatedBoxes[listSymbolIndex].push(currentBox);
			}

			return updatedBoxes;
		});

		// Unfocus all boxes
		setFocusBoxIndex({symbolIndex: -1, boxIndex: -1});
		setSearchText("");
	}

	const handleSymbolDelete = () => {
		const currentSymbolBoxes = boxes[focusBoxIndex.symbolIndex];
		
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
		if (!symbolListRef.current.children) return;
		
		for (let i = 0; i < symbolListRef.current.children.length; i++) {
			const child = symbolListRef.current.children[i];

			// Highlight the symbol in the list
			if (child.children[1].textContent === searchText) {
				child.classList.add("bg-primary");
				child.classList.add("opacity-[100%]");
				
				// Set the symbol index to the selected symbol
				const symbolIndex = parseInt(child.getAttribute("symbol-index"));
				setListSymbolIndex(() => symbolIndex);
				setPrevFocusBoxIndex(() => ({symbolIndex: symbolIndex, boxIndex: focusBoxIndex.boxIndex}));
			} else {
				child.classList.remove("bg-primary");
				child.classList.remove("opacity-[100%]");
			}
		}

		searchBoxRef.current.value = searchText;
	}, [searchText]);

	const handleDelete = () => {
		const retrievedData = JSON.parse(localStorage.getItem('images'));

		const updatedData = retrievedData.filter((image) => image.page !== page || image.zone !== zone);

		localStorage.setItem('images', JSON.stringify(updatedData));
		navigate(-1);
	}

	const handleReset = () => {
		const retrievedData = JSON.parse(localStorage.getItem('images'));
		const canvasData = retrievedData.find((image) => image.page === page && image.zone === zone);

		setBoxes(canvasData.boxes);
	}

	const handleSave = () => {
		const retrievedData = JSON.parse(localStorage.getItem('images'));

		const updatedData = retrievedData.map((image) => {
			if (image.page === page && image.zone === zone) {
				return {
					...image,
					boxes: boxes,
				}
			}
			return image;
		})

		localStorage.setItem('images', JSON.stringify(updatedData));
	}

	const handleDialogConfirm = () => {
		setDialogOpen(false);
		cutImage();
	}

	const handleDialogCancel = () => {
		setDialogOpen(false);
	}

	const handlePreviousPage = () => {
		if (prevPage) {
			navigate(`/edit/${filename}-page${prevPage.page}-zone${prevPage.zone}`, {state: {filename, page: prevPage.page, zone: prevPage.zone}});
			// Force a page reload to ensure all data is refreshed
			window.location.reload();
		}
	};
	
	const handleNextPage = () => {
		if (nextPage) {
			navigate(`/edit/${filename}-page${nextPage.page}-zone${nextPage.zone}`, {state: {filename, page: nextPage.page, zone: nextPage.zone}});
			// Force a page reload to ensure all data is refreshed
			window.location.reload();
		}
	};

	return (
  		<div className='flex h-[100vh] overflow-hidden bg-primary'>
			<div className='relative w-[16%] bg-secondary border-r-2 border-zinc-600 border-solid'>
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

			{/* Canvas operation (top bar) */}
			<div className='relative w-[84%]'>
				<div className='aboslute top-0 left-0 w-full h-16 bg-secondary flex items-center justify-between px-4'>
					<div className='flex flex-col justify-center'>
						<h1 className='text-white opacity-50 text-sm hover:underline hover:cursor-pointer' onClick={() => navigate('/extract')}>
							Home
						</h1>
						<h1 className='text-white text-lg'>{image.alt}</h1>
					</div>
					<div className='flex items-center'>
						<div className='w-16 bg-transparent mx-1 rounded-md border border-2 border-primary text-xs text-center text-white p-2 cursor-pointer hover:bg-primary transition-all duration-100 ease' onClick={handleDelete}>
							<h1>Delete</h1>
						</div>
						<div className='w-16 bg-transparent mx-1 rounded-md border border-2 border-primary text-xs text-center text-white p-2 cursor-pointer hover:bg-primary transition-all duration-100 ease' onClick={handleReset}>
							<h1>Reset</h1>
						</div>
						<div className='w-16 bg-zinc-300 mx-1 rounded-md border border-2 border-primary text-xs text-center text-black p-2 cursor-pointer hover:bg-zinc-400 transition-all duration-100 ease' onClick={handleSave}>
							<h1>Save</h1>
						</div>
					</div>
				</div>
				<canvas ref={canvasRef} className='w-full h-full' onWheel={handleWheel} onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}>
				</canvas>

				{/* Box for switching between drag and edit modes */}
				<div className='absolute bottom-3 left-[50%] -translate-x-[50%] h-10 bg-secondary mx-auto mt-4 rounded-lg grid grid-cols-3'>
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
					<div className='w-10 flex items-center justify-center rounded-md m-1 cursor-pointer transition-all duration-300 ease' ref={cutModeRef} onClick={handleModeSwitch}>
						<h1 className='text-sm font-semibold pointer-events-none transition-all duration-300 ease'>
							<ContentCutIcon />
						</h1>
					</div>
				</div>

				{/* Box for navigating between pages */}
				<div className='absolute top-[50%] -translate-y-[50%] right-3 h-20 bg-secondary mx-auto mt-4 rounded-lg grid grid-rows-2'>
					<div className='w-10 flex items-center justify-center rounded-md m-1 cursor-pointer transition-all duration-300 ease' onClick={handlePreviousPage}>
						<h1 className='text-sm font-semibold pointer-events-none transition-all duration-300 ease'>
							<ArrowUpwardIcon />
						</h1>
					</div>
					<div className='w-10 flex items-center justify-center rounded-md m-1 cursor-pointer transition-all duration-300 ease' onClick={handleNextPage}>
						<h1 className='text-sm font-semibold pointer-events-none transition-all duration-300 ease'>
							<ArrowDownwardIcon />
						</h1>
					</div>
				</div>				

				<ConfirmDialog headMessage={dialogHeadMessage} subMessage={dialogSubMessage}
				isOpen={isDialogOpen} setIsOpen={setDialogOpen} onConfirm={handleDialogConfirm} onCancel={handleDialogCancel} />
			</div>

		</div>
  	)
}

export default EditLayout