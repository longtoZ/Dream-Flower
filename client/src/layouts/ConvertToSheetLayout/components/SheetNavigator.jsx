import React, { useState, useEffect, useRef, useContext } from 'react';
import ReactJson from 'react-json-view';

import { AudioContext } from '../../../context/Audio';

const SheetNavigator = ({ receivedData }) => {
  const [musicSheetData, setMusicSheetData] = useState(receivedData || []);
  const [pages, setPages] = useState([]);
  const [zones, setZones] = useState([]);
  const [measures, setMeasures] = useState([]);
  const [selectedData, setSelectedData] = useState(null);
  const [isDurationCorrect, setIsDurationCorrect] = useState(false);

  // State for dropdown selections
  const [selectedPage, setSelectedPage] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const [selectedMeasure, setSelectedMeasure] = useState(null);
  const [selectedClef, setSelectedClef] = useState('treble_zone');

  const measurePlaytimeRef = useRef(null);
  const [selectedAudioTheme, setSelectedAudioTheme] = useState('classical_piano');
  
  const setAudioUrl = useContext(AudioContext).setAudioUrl;
  const setJsonData = useContext(AudioContext).setJsonData;

  // Initialize state once data is available
  useEffect(() => {
    setMusicSheetData(() => receivedData || []);

    if (musicSheetData && musicSheetData.length > 0) {
      console.log(musicSheetData);
      const firstPage = musicSheetData[0].page;
      const firstZone = musicSheetData[0].zone;
      setSelectedPage(() => firstPage);
      setSelectedZone(() => firstZone);

      // Default to treble_zone if available, otherwise bass_zone
      const firstZoneData = musicSheetData.find(
        (item) => item.page === firstPage && item.zone === firstZone
      );
      const firstMeasure =
        firstZoneData?.treble_zone?.[0]?.measure ||
        firstZoneData?.bass_zone?.[0]?.measure ||
        0;
      setSelectedMeasure(() => firstMeasure);
    }
  }, [receivedData]);

  useEffect(() => {     
     // Derive available options for dropdowns
    setPages(() => [...new Set(musicSheetData.map((item) => item.page))]);
    setZones(() => [
      ...new Set(
        musicSheetData
          .filter((item) => item.page === selectedPage)
          .map((item) => item.zone)
      ),
    ]);
    setMeasures(() => [
      ...new Set(
        musicSheetData
          .find((item) => item.page === selectedPage && item.zone === selectedZone)
          ?.[selectedClef]?.map((measure) => measure.measure) || []
      ),
    ]);

    // Get the selected JSON part
    setSelectedData(() => musicSheetData
    .find((item) => item.page === selectedPage && item.zone === selectedZone)
    ?.[selectedClef]?.find((measure) => measure.measure === selectedMeasure));

  }, [selectedPage, selectedZone, selectedMeasure, selectedClef, musicSheetData]);

  useEffect(() => {
      // Check duration validity
      setIsDurationCorrect(() => selectedData?.measure_duration === selectedData?.measure_playtime);
  }, [selectedData]);

  const handleGenerateAudio = async () => {
    const data = {
      "music_sheet": musicSheetData,
      "measure_playtime": parseInt(measurePlaytimeRef.current.value) || 0,
      "audio_theme": selectedAudioTheme,
    }

    try {
      const response = await fetch("http://localhost:5000/api/generate-audio", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }

      // Handle multipart response
      const contentType = response.headers.get("Content-Type");
      const boundaryMatch = contentType.match(/boundary=(.+)$/);
  
      if (!boundaryMatch) {
        console.error("No boundary found in response.");
        return;
      }
  
      const boundary = boundaryMatch[1];
      const rawData = await response.arrayBuffer();
      const decoder = new TextDecoder("utf-8");
      const textData = decoder.decode(rawData);
  
      // Split parts
      const parts = textData.split(`--${boundary}`);
      const jsonPart = parts.find(p => p.includes("application/json"));
      const audioPartStartIndex = textData.indexOf("Content-Type: audio/mp3");
  
      // Get JSON
      const jsonMatch = jsonPart?.match(/{[\s\S]*}/);
      jsonMatch[0] = '[' + jsonMatch[0] + ']';
      if (jsonMatch) {
        const json = JSON.parse(jsonMatch[0]);
        setJsonData(json);
      }
  
      // Get audio blob
      const audioRaw = rawData.slice(audioPartStartIndex + textData.slice(audioPartStartIndex).indexOf("\r\n\r\n") + 4);
      const audioBlob = new Blob([audioRaw], { type: "audio/mp3" });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      console.log("Audio generated successfully.");
    } catch (error) {
      console.error("Error generating audio:", error);
    }
  }

  return (
    <div
      className="flex items-center justify-center"
    >
      <div
        className="h-[94vh] w-[40vw] mx-10">
        <h1 className="mt-10 text-2xl font-bold text-white mb-6">Sheet Navigation</h1>
        <div className='w-full p-6 rounded-lg shadow-lg bg-secondary'>

          {/* Dropdown Menus */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
            {/* Page Dropdown */}
            <div>
              <label className="block text-sm font-medium text-white mb-1">
                Page
              </label>
              <select
                value={selectedPage ?? ''}
                onChange={(e) => {
                  const newPage = Number(e.target.value);
                  setSelectedPage(newPage);
                  const newZones = [
                    ...new Set(
                      musicSheetData
                        .filter((item) => item.page === newPage)
                        .map((item) => item.zone)
                    ),
                  ];
                  const newZone = newZones[0] || 1;
                  setSelectedZone(newZone);
                  const newMeasures = [
                    ...new Set(
                      musicSheetData
                        .find(
                          (item) =>
                            item.page === newPage && item.zone === newZone
                        )
                        ?.[selectedClef]?.map((measure) => measure.measure) || []
                    ),
                  ];
                  setSelectedMeasure(newMeasures[0] || 0);
                }}
                className="w-full p-2 rounded-sm text-white focus:outline-none"
                style={{ backgroundColor: '#30323b' }}
                disabled={!pages.length}
              >
                {pages.length > 0 ? (
                  pages.map((page) => (
                    <option key={`page-${page}`} value={page}>
                      Page {page}
                    </option>
                  ))
                ) : (
                  <option key="no-page" value="">
                    No Pages
                  </option>
                )}
              </select>
            </div>

            {/* Zone Dropdown */}
            <div>
              <label className="block text-sm font-medium text-white mb-1">
                Zone
              </label>
              <select
                title='Zone'
                value={selectedZone ?? ''}
                onChange={(e) => {
                  const newZone = Number(e.target.value);
                  setSelectedZone(newZone);
                  const newMeasures = [
                    ...new Set(
                      musicSheetData
                        .find(
                          (item) =>
                            item.page === selectedPage && item.zone === newZone
                        )
                        ?.[selectedClef]?.map((measure) => measure.measure) || []
                    ),
                  ];
                  setSelectedMeasure(newMeasures[0] || 0);
                }}
                className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary"
                disabled={!zones.length}
              >
                {zones.length > 0 ? (
                  zones.map((zone) => (
                    <option key={`zone-${zone}`} value={zone}>
                      Zone {zone}
                    </option>
                  ))
                ) : (
                  <option key="no-zone" value="">
                    No Zones
                  </option>
                )}
              </select>
            </div>

            {/* Measure Dropdown */}
            <div>
              <label className="block text-sm font-medium text-white mb-1">
                Measure
              </label>
              <select
                title='Measure'
                value={selectedMeasure ?? ''}
                onChange={(e) => setSelectedMeasure(Number(e.target.value))}
                className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary"
                disabled={!measures.length}
              >
                {measures.length > 0 ? (
                  measures.map((measure) => (
                    <option key={`measure-${measure}`} value={measure}>
                      Measure {measure}
                    </option>
                  ))
                ) : (
                  <option key="no-measure" value="">
                    No Measures
                  </option>
                )}
              </select>
            </div>

            {/* Clef Dropdown */}
            <div>
              <label className="block text-sm font-medium text-white mb-1">
                Clef
              </label>
              <select
                title='Clef'
                value={selectedClef}
                onChange={(e) => {
                  const newClef = e.target.value;
                  setSelectedClef(newClef);
                  const newMeasures = [
                    ...new Set(
                      musicSheetData
                        .find(
                          (item) =>
                            item.page === selectedPage && item.zone === selectedZone
                        )
                        ?.[newClef]?.map((measure) => measure.measure) || []
                    ),
                  ];
                  setSelectedMeasure(newMeasures[0] || 0);
                }}
                className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary"
              >
                {[
                  { value: 'treble_zone', label: 'Treble' },
                  { value: 'bass_zone', label: 'Bass' },
                ].map((clef) => (
                  <option key={`clef-${clef.value}`} value={clef.value}>
                    {clef.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* JSON Viewer */}
          <div
            className="mb-6 p-4 rounded-sm bg-primary"
          >
            <h2 className="text-lg font-semibold text-white mb-2">
              Selected JSON Data
            </h2>
            {selectedData ? (
              <ReactJson
                src={selectedData}
                theme={{
                  base00: 'transparent',    // Background
                  base01: '#2e2a3b',        // Secondary background
                  base02: '#3b354a',        // Highlights
                  base03: '#cfcfe0',        // Comments / faint text
                  base04: '#e0e0ff',        // Secondary text
                  base05: '#ffffff',        // Main text
                  base06: '#c3f0ca',        // Attributes / variables
                  base07: '#d4bfff',        // Function names / brighter lilac
                  base08: '#ff6b81',        // Errors / invalid
                  base09: '#ffd166',        // Numbers
                  base0A: '#f9f871',        // Constants / values
                  base0B: '#95f9c3',        // Strings (light mint green)
                  base0C: '#7ec180',        // Booleans / regex (violet-lavender)
                  base0D: '#b388ff',        // Keys (bold violet)
                  base0E: '#d67fff',        // Keywords (soft pink-violet)
                  base0F: '#f78fb3',        // Special cases / undefined
                }}
                style={{ padding: '1rem', lineHeight: '1.3', height: '350px', overflowY: 'auto', fontSize: '0.9rem' }}
                displayDataTypes={false}
                displayObjectSize={false}
                indentWidth={4}
                onEdit={(edit) => {
                  const { updated_src, namespace, existing_src } = edit;

                  // if (namespace.includes('notes') && !/^[A-G][0-8]$/.test(updated_src)) {
                  //   console.log('Invalid note:', updated_src, namespace);
                  //   return false; // Block invalid note
                  // }
                  // if (namespace.includes('duration') && typeof updated_src !== 'number') {
                  //   console.log('Invalid duration:', updated_src);
                  //   return false; // Block invalid duration
                  // }
                  setMusicSheetData((prevData) => {
                    const updatedData = [...prevData];
                    const index = updatedData.findIndex((item) => item.page === selectedPage && item.zone === selectedZone);
                    if (index !== -1) {
                      updatedData[index][selectedClef][selectedMeasure] = updated_src;
                    }
                    
                    return updatedData;
                  })
                }}
              />
            ) : (
              <p className="text-gray-400">No data available for the selected options.</p>
            )}
          </div>

          {/* Duration Validation */}
          <div
            className="p-4 rounded-sm bg-primary"
          >
            <h2 className="text-lg font-semibold text-white mb-2">
              Duration Validation
            </h2>
            {selectedData ? (
              <p
                className={`text-sm ${isDurationCorrect ? 'text-green-400' : 'text-red-400'}`}
              >
                Duration is {isDurationCorrect ? `Correct (${selectedData.measure_duration})` : `Incorrect (${selectedData.measure_duration})`}
              </p>
            ) : (
              <p className="text-gray-400">No duration data available.</p>
            )}
          </div>
        </div>
        
      </div>

      <div className="h-[94vh] w-[40vw] mx-10">
        <h1 className="mt-10 text-2xl font-bold text-white mb-6">Sound Options</h1>
        <div className='w-full p-6 rounded-lg shadow-lg bg-secondary'>
          {/* Measure playtime input */}
          <h2 className='text-md font-semibold text-white mb-2'>
            Measure playtime
          </h2>
          <input
            ref={measurePlaytimeRef}
            type="number"
            placeholder="Enter miliseconds..."
            min={500}
            max={10000}
            className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary mb-4"
          />

          {/* Audio theme dropdown */}
          <h2 className='text-md font-semibold text-white mb-2'>
            Audio theme
          </h2>
          <select
            className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary mb-4"
            onChange={(e) => {
              const newTheme = e.target.value;
              setSelectedAudioTheme(newTheme);
            }}
          >
            <option value="classical_piano">Classical Piano</option>
            <option value="upright_piano">Upright Piano</option>
            <option value="auditorium_piano">Auditorium Piano</option>
            <option value="organ">Organ</option>
            <option value="violin">Violin</option>
          </select>

          <button
            className="w-full p-2 rounded-sm bg-zinc-200 text-black cursor-pointer hover:bg-zinc-300 focus:outline-none"
            onClick={handleGenerateAudio}
          >
            Generate audio
          </button>
        </div>
      </div>
    </div>
  );
}

export default SheetNavigator;