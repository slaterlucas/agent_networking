import React from "react";
import Map, { Marker } from "react-map-gl";

interface Pin {
  id: string;
  lat: number;
  lng: number;
  emoji: string;
  title: string;
}

interface MapViewProps {
  pins: Pin[];
  onPinSelect: (pin: Pin) => void;
}

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

const MapView: React.FC<MapViewProps> = ({ pins, onPinSelect }) => {
  return (
    <Map
      mapboxAccessToken={MAPBOX_TOKEN}
      initialViewState={{ longitude: 2.3522, latitude: 48.8566, zoom: 12 }}
      style={{ width: "100%", height: "100%" }}
      mapStyle="mapbox://styles/mapbox/streets-v11"
    >
      {pins.map((pin) => (
        <Marker
          key={pin.id}
          longitude={pin.lng}
          latitude={pin.lat}
          anchor="bottom"
          onClick={() => onPinSelect(pin)}
        >
          <span className="text-2xl cursor-pointer" title={pin.title}>{pin.emoji}</span>
        </Marker>
      ))}
    </Map>
  );
};

export default MapView; 