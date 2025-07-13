import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix default marker icon issue in Leaflet
const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});
L.Marker.prototype.options.icon = DefaultIcon;

const INITIAL_POSITION: [number, number] = [48.8566, 2.3522]; // Paris

function AddPin({ onAdd }: { onAdd: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      onAdd(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

const MapView = () => {
  const [pins, setPins] = useState<{ lat: number; lng: number; id: number }[]>([]);
  const [selectedPin, setSelectedPin] = useState<number | null>(null);

  const handleAddPin = (lat: number, lng: number) => {
    setPins((prev) => [...prev, { lat, lng, id: Date.now() }]);
  };

  return (
    <MapContainer center={INITIAL_POSITION} zoom={13} style={{ width: '100%', height: '100%' }}>
      <TileLayer
        // @ts-ignore
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <AddPin onAdd={handleAddPin} />
      {pins.map((pin) => (
        <Marker
          key={pin.id}
          position={[pin.lat, pin.lng]}
          eventHandlers={{
            click: () => setSelectedPin(pin.id),
          }}
        >
          {selectedPin === pin.id && (
            <Popup eventHandlers={{ remove: () => setSelectedPin(null) }}>
              <div className="text-sm font-semibold">Pinned location<br />({pin.lat.toFixed(4)}, {pin.lng.toFixed(4)})</div>
            </Popup>
          )}
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView;
