import { useEffect, useRef, useState } from 'react';

interface GoogleMapProps {
  center: { lat: number; lng: number };
  zoom?: number;
  height?: string;
  markers?: Array<{
    position: { lat: number; lng: number };
    title: string;
    info?: string;
  }>;
}

// Add Vite env type for TypeScript
interface ImportMeta {
  env: {
    VITE_GOOGLE_MAPS_API_KEY?: string;
    [key: string]: any;
  };
}

declare global {
  interface Window {
    google: any;
    initMap: () => void;
  }
}

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || 'AIzaSyCEZvC-t4uT9tdceCfW7x5lvj8AW9NJ0b0';

const GoogleMap: React.FC<GoogleMapProps> = ({ 
  center, 
  zoom = 13, 
  height = '400px',
  markers = []
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const mapInstance = useRef<any>(null);

  useEffect(() => {
    const loadGoogleMapsScript = () => {
      if (window.google && window.google.maps) {
        setIsLoaded(true);
        return;
      }

      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = () => {
        setIsLoaded(true);
      };
      document.head.appendChild(script);
    };

    loadGoogleMapsScript();
  }, []);

  useEffect(() => {
    if (isLoaded && mapRef.current && !mapInstance.current) {
      // Initialize the map
      mapInstance.current = new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: zoom,
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'on' }]
          }
        ]
      });

      // Add markers
      markers.forEach((marker) => {
        const mapMarker = new window.google.maps.Marker({
          position: marker.position,
          map: mapInstance.current,
          title: marker.title,
        });

        if (marker.info) {
          const infoWindow = new window.google.maps.InfoWindow({
            content: `<div><strong>${marker.title}</strong><br/>${marker.info}</div>`
          });

          mapMarker.addListener('click', () => {
            infoWindow.open(mapInstance.current, mapMarker);
          });
        }
      });
    }
  }, [isLoaded, center, zoom, markers]);

  if (!isLoaded) {
    return (
      <div 
        style={{ height }}
        className="bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center"
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Google Maps...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={mapRef}
      style={{ height }}
      className="rounded-lg overflow-hidden"
    />
  );
};

export default GoogleMap; 