import React, { useState, useEffect, useRef } from 'react'
import WaveSurferPlayer from '@wavesurfer/react';

import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';

const AudioPlayer = ({ audioUrl, jsonData }) => {
  const audioRef = useRef(null);
  const dataListRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [dataList, setDataList] = useState([]);

  const [isPlaying, setIsPlaying] = useState(false);
  const wavesurferRef = useRef(null);

  const handlePlayPause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
      setIsPlaying(!isPlaying);
    }
  };

  useEffect(() => {
    const audio = audioRef.current;

    if (!audio) return; // Ensure audio is loaded

    const handleTimeUpdate = () => {
      const time = audio.currentTime * 1000; // Convert to milliseconds

      const currentIndex = jsonData.findIndex((measure, index) => {
        const nextMeasure = jsonData[index + 1];
        
        if (nextMeasure) {
          return time >= measure["time"] && time < nextMeasure["time"]; // Check if time is between the current and next measure
        }
        return time >= measure["time"]; // For the last measure, check if time is greater than or equal to the last measure's time
      });

      setCurrentIndex(currentIndex);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, [audioRef.current]);

  useEffect(() => {
    if (jsonData.length > 0) {
      // Reset the data list
      setDataList([]);

      // Refill the data list 
      for (let i=0; i<=currentIndex+2; i++){
        if (i >= jsonData.length) break; // Prevent out of bounds access
        const dataStr = `Page: ${jsonData[i]["page"]}, Zone: ${jsonData[i]["zone"]}, Measure: ${jsonData[i]["measure"]}, Time: ${jsonData[i]["time"]}`;
        setDataList((prevData) => [...prevData, dataStr]);
      }
    }
  }, [currentIndex]);

  useEffect(() => {
    // Scroll to the bottom of the data list when it changes
    if (dataListRef.current) {
      dataListRef.current.scrollTop = dataListRef.current.scrollHeight;
    }
  }, [dataList]);

  return (
    <div className="flex flex-col items-center justify-center mt-4">
        <h1 className='text-center mb-4'>
          <span className="text-2xl font-bold text-white">Generated audio</span>
        </h1>
        <div className='p-6 rounded-lg shadow-lg bg-secondary w-[50%] flex items-center justify-center flex-col'>
          <h2 className='text-lg font-semibold text-white mb-4'>Audio Data:</h2>
          <div className='text-white mb-4 h-48 overflow-y-auto p-6' ref={dataListRef}>
            {dataList.map((data, index) => (
              <div key={index} className='mb-2'>
                {index === dataList.length - 3 ? (
                  <span className='text-green-400'>{data}</span>
                ) : (
                  <span className='text-gray-400 opacity-50'>{data}</span>
                )}
              </div>
            ))}
          </div>
          {/* <audio ref={audioRef} controls className="w-full max-w-md">
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio> */}
          <div className='w-full flex justify-center flex-col bg-primary rounded-md p-4'>
            <div className="w-full">
              <WaveSurferPlayer
                height={100}
                waveColor="#ffffff"
                progressColor="#ffffff69"
                cursorColor="#1ABC9C"
                barWidth={3}
                barRadius={3}
                barGap={2}
                url={audioUrl}
                onReady={(wavesurfer) => {
                  wavesurferRef.current = wavesurfer;
                  // Get the media element and assign to audioRef
                  audioRef.current = wavesurfer.getMediaElement();
                }}
              />
            </div>
            <button
                onClick={handlePlayPause}
                className="block mx-auto p-4 bg-blue-500 w-12 h-12 flex justify-center items-center text-white rounded-[50%] hover:bg-blue-600 transition duration-200"
              >
                {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
              </button>
          </div>

        </div>
    </div>
  )
}

export default AudioPlayer