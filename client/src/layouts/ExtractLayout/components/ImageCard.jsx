import React, {useState, useEffect, useRef} from 'react';
import { useNavigate } from 'react-router-dom';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { CLASS_NAMES } from '../../../config/constants';

const ImageCard = ({filename, page, zone, data, boxes}) => {
    const navigate = useNavigate();

    const generateSymbols = () => {
        const symbols = [];

        boxes.forEach((box, index) => {
            if (box.length > 0) {
                symbols.push(`${box.length} ${CLASS_NAMES[index]}`);
            }
        })

        return symbols;
    }

    const handleNavigate = () => {
        navigate(`/edit/${filename}-page${page}-zone${zone}`, {state: {filename, page, zone}});
    }

    return (
        <div onClick={handleNavigate} className='relative bg-secondary w-full rounded-md border border-tertiary border-2 p-2'>
            <div className='h-[100px] relative cursor-pointer'>
                {/* <canvas ref={canvasRef} className='w-full h-full object-fill brightness-75 rounded-md'></canvas> */}
                <img src={`data:image/png;base64,${data}`} alt={`Page ${page}`} className='w-full h-full object-cover brightness-75 rounded-md'/>
                <div className='absolute bottom-0 left-0 w-full h-full bg-transparent hover:bg-[rgba(0,0,0,0.5)] transition-all duration-300 ease'>
                    <ul className='w-full h-[100px] overflow-y-scroll scrollbar-hide absolute bottom-0 left-0 p-3 hover:opacity-100 opacity-0 transition-opacity duration-300 ease'>
                        {generateSymbols().map((symbol, index) => (
                            <li key={index} className='text-white text-xs text-zinc-200'>{symbol}</li>
                        ))}
                    </ul>
                </div>
            </div>
            <div className='flex items-center justify-between px-1 pt-2 font-bold'>
                <h1 className='relative text-sm'>Page {page} <span className='opacity-40'>Zone {zone}</span></h1>
                <div className='bg-primary rounded-[50%] cursor-pointer'>
                    <ArrowForwardIcon className='opacity-30'/>
                </div>
            </div>
        </div>
    )
}

export default ImageCard