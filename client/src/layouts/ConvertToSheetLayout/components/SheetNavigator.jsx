import React, { useState, useEffect, use } from 'react';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css'; // Choose a theme for JSON formatting

import { v4 as uuidv4 } from "uuid";

const containerStyle = {
  '--primary-color': '#2C2F38',
  '--secondary-color': '#1d2029',
  '--tertiary-color': '#30323b'
};

const SheetNavigator = ({ musicSheetData }) => {
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

  // Initialize state once data is available
  useEffect(() => {
    if (musicSheetData && musicSheetData.length > 0) {
      const firstPage = musicSheetData[0].page;
      const firstZone = musicSheetData[0].zone;
      setSelectedPage(firstPage);
      setSelectedZone(firstZone);
      // Default to treble_zone if available, otherwise bass_zone
      const firstZoneData = musicSheetData.find(
        (item) => item.page === firstPage && item.zone === firstZone
      );
      const firstMeasure =
        firstZoneData?.treble_zone?.[0]?.measure ||
        firstZoneData?.bass_zone?.[0]?.measure ||
        0;
      setSelectedMeasure(firstMeasure);

      // Derive available options for dropdowns
      setPages([...new Set(musicSheetData.map((item) => item.page))]);
      setZones([
        ...new Set(
          musicSheetData
            .filter((item) => item.page === selectedPage)
            .map((item) => item.zone)
        ),
      ]);
      setMeasures([
        ...new Set(
          musicSheetData
            .find((item) => item.page === selectedPage && item.zone === selectedZone)
            ?.[selectedClef]?.map((measure) => measure.measure) || []
        ),
      ]);

    }
  }, [musicSheetData]);

  useEffect(() => {
    console.log('Selected Page:', selectedPage);
    console.log('Selected Zone:', selectedZone);
    console.log('Selected Measure:', selectedMeasure);
    console.log('Selected Clef:', selectedClef);
    console.log('Selected Data:', selectedData);
    // Get the selected JSON part
    setSelectedData(() => musicSheetData
    .find((item) => item.page === selectedPage && item.zone === selectedZone)
    ?.[selectedClef]?.find((measure) => measure.measure === selectedMeasure));

    // Check duration validity
    setIsDurationCorrect(selectedData?.duration === 1);

  }, [selectedPage, selectedZone, selectedMeasure, selectedClef]);

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ backgroundColor: '#1d2029' }}
    >
      <div
        className="w-full max-w-4xl p-6 rounded-lg shadow-lg"
        style={{ backgroundColor: '#2C2F38' }}
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
              className="w-full p-2 rounded-md text-white focus:outline-none"
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
              className="w-full p-2 rounded-md text-white focus:outline-none"
              style={{ backgroundColor: '#30323b' }}
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
              value={selectedMeasure ?? ''}
              onChange={(e) => setSelectedMeasure(Number(e.target.value))}
              className="w-full p-2 rounded-md text-white focus:outline-none"
              style={{ backgroundColor: '#30323b' }}
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
              className="w-full p-2 rounded-md text-white focus:outline-none"
              style={{ backgroundColor: '#30323b' }}
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
          className="mb-6 p-4 rounded-md"
          style={{ backgroundColor: '#30323b' }}
        >
          <h2 className="text-lg font-semibold text-white mb-2">
            Selected JSON Data
          </h2>
          {selectedData ? (
            <JSONPretty
              id="json-pretty"
              data={selectedData}
              theme={{
                main: 'line-height:1.3;color:#fff;background:#30323b;overflow:auto;',
                error: 'color:#ff4d4f;',
                key: 'color:#66d9ef;',
                string: 'color:#a3e6a3;',
                value: 'color:#f8f8f2;',
                boolean: 'color:#ae81ff;',
              }}
            />
          ) : (
            <p className="text-gray-400">No data available for the selected options.</p>
          )}
        </div>

        {/* Duration Validation */}
        <div
          className="p-4 rounded-md"
          style={{ backgroundColor: '#30323b' }}
        >
          <h2 className="text-lg font-semibold text-white mb-2">
            Duration Validation
          </h2>
          {selectedData ? (
            <p
              className={`text-sm ${isDurationCorrect ? 'text-green-400' : 'text-red-400'}`}
            >
              Duration is {isDurationCorrect ? 'Correct (1)' : `Incorrect (${selectedData.duration})`}
            </p>
          ) : (
            <p className="text-gray-400">No duration data available.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default SheetNavigator;