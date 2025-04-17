import React, { useState, useEffect, useRef } from 'react';
import ReactJson from 'react-json-view';
import 'react-json-pretty/themes/monikai.css'; // Choose a theme for JSON formatting

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

  const handleGenerateAudio = () => {
    const data = {
      "music_sheet": musicSheetData,
      "measure_playtime": parseInt(measurePlaytimeRef.current.value) || 0,
    }

    try {
      const response = fetch("http://localhost:5000/api/generate-audio", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }

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
        className="w-full max-w-4xl p-6 rounded-lg shadow-lg bg-secondary"
      >
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
                base00: 'transparent', // Background (tertiary-color)
                base01: 'transparent', // Secondary background
                base02: '#2C2F38', // Primary color
                base03: '#fff', // Comments
                base04: '#fff', // Secondary text
                base05: '#fff', // Text
                base06: '#fff', // Text
                base07: '#fff', // Text
                base08: '#ff4d4f', // Error
                base09: '#a3e6a3', // Strings
                base0A: '#f8f8f2', // Values
                base0B: '#a3e6a3', // Strings
                base0C: '#ae81ff', // Booleans
                base0D: '#66d9ef', // Keys
                base0E: '#ae81ff', // Booleans
                base0F: '#f8f8f2', // Values
              }}
              style={{ padding: '1rem', lineHeight: '1.3', height: '400px', overflowY: 'auto', fontSize: '0.9rem' }}
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

        {/* An input (number) and a send button */}
        <div className='mt-6'>
          <input
            ref={measurePlaytimeRef}
            type="number"
            placeholder="Enter measure playtime (miliseconds)..."
            className="w-full p-2 rounded-sm text-white focus:outline-none bg-primary mb-4"
          />
          <button
            className="w-full p-2 rounded-sm bg-green-500 text-white cursor-pointer hover:bg-green-600 focus:outline-none"
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