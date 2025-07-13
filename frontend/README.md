# Agent Networking Frontend

A modern React web application for managing and interacting with personal and service agents in the Agent Networking system.

## Features

- **Dashboard**: Monitor agent status, activities, and collaborations
- **Chat Interface**: Communicate directly with agents
- **Map View**: Visualize agent locations and activities
- **Settings**: Configure agent preferences and privacy settings
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Built-in dark mode support

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Lucide React** for icons
- **clsx & tailwind-merge** for class name utilities

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. **Navigate to the frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AgentDashboard.tsx    # Main dashboard view
│   │   ├── AgentChat.tsx         # Chat interface
│   │   ├── AgentMap.tsx          # Map view
│   │   └── AgentSettings.tsx     # Settings page
│   ├── lib/
│   │   └── utils.ts              # Utility functions
│   ├── App.tsx                   # Main app component
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Global styles
├── public/                       # Static assets
├── package.json                  # Dependencies and scripts
├── vite.config.ts               # Vite configuration
├── tailwind.config.js           # Tailwind CSS configuration
└── tsconfig.json                # TypeScript configuration
```

## Key Components

### AgentDashboard
- Displays agent status and statistics
- Shows recent activities and collaborations
- Quick actions for agent management

### AgentChat
- Real-time chat interface with agents
- Message history and timestamps
- Agent identification and status

### AgentMap
- Visual representation of agent locations
- Activity timeline and collaboration tracking
- Location-based agent interactions

### AgentSettings
- Agent configuration and permissions
- Privacy and data sharing controls
- Integration management
- Notification preferences

## Styling

The application uses Tailwind CSS with custom utility classes:

- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary action buttons
- `.card` - Card containers with consistent styling
- `.input-field` - Form input styling

## Development

### Adding New Components

1. Create a new component in `src/components/`
2. Import and add to the router in `App.tsx`
3. Follow the existing component patterns

### Styling Guidelines

- Use Tailwind CSS classes for styling
- Follow the existing color scheme and spacing
- Ensure dark mode compatibility
- Use the custom utility classes for consistency

### State Management

Currently using React's built-in state management. For more complex state, consider adding:

- React Context for global state
- Zustand for lightweight state management
- React Query for server state

## Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Environment Variables

Create a `.env` file for environment-specific configuration:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new interfaces
3. Test components in both light and dark modes
4. Ensure responsive design works on mobile devices

## License

This project is part of the Agent Networking system. 