# Frontend Architecture Documentation

## Overview

The ScrapeCraft frontend is a sophisticated React TypeScript single-page application designed for OSINT operations, investigation management, and real-time data visualization. It implements a modern component-based architecture with comprehensive state management, real-time communication, and responsive design.

## Architecture Stack

### Core Framework
- **React 18**: Modern React with concurrent features
- **TypeScript**: Full type safety and enhanced developer experience
- **Vite**: Fast build tool and development server
- **React Router v6**: Client-side routing

### UI Framework & Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Headless UI**: Accessible component primitives
- **PrismJS**: Syntax highlighting for code display
- **Lucide React**: Modern icon library

### State Management
- **Zustand**: Lightweight state management
- **React Query (TanStack Query)**: Server state management
- **React Hook Form**: Form state management
- **Zod**: Schema validation

### HTTP & Real-time Communication
- **Axios**: HTTP client with interceptors
- **WebSocket API**: Real-time bidirectional communication
- **Custom hooks**: Abstracted API communication

### Development Tools
- **ESLint**: Code linting and quality
- **Prettier**: Code formatting
- **Vitest**: Fast unit testing framework
- **React Testing Library**: Component testing

## Project Structure

```
frontend/
├── public/                     # Static assets
│   ├── index.html             # HTML template
│   ├── logo.png               # Application logo
│   └── manifest.json          # PWA configuration
├── src/
│   ├── components/            # Reusable UI components
│   │   ├── Common/            # Generic components
│   │   │   ├── Button.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── LoadingScreen.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── Layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── SplitView.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── OSINT/             # OSINT-specific components
│   │   │   ├── InvestigationDashboard.tsx
│   │   │   ├── EvidencePanel.tsx
│   │   │   └── SourceManager.tsx
│   │   ├── Pipeline/          # Pipeline management
│   │   │   ├── PipelinePanel.tsx
│   │   │   ├── PipelineEditor.tsx
│   │   │   └── FlowVisualizer.tsx
│   │   ├── Agent/             # AI Agent components
│   │   │   ├── AgentCoordinator.tsx
│   │   │   ├── AgentChat.tsx
│   │   │   └── ApprovalManager.tsx
│   │   └── Forms/             # Form components
│   │       ├── InvestigationForm.tsx
│   │       └── SettingsForm.tsx
│   ├── hooks/                 # Custom React hooks
│   │   ├── useWebSocket.ts    # WebSocket management
│   │   ├── useInvestigation.ts # Investigation state
│   │   ├── usePipeline.ts     # Pipeline operations
│   │   └── useApi.ts          # API communication
│   ├── store/                 # State management
│   │   ├── investigationStore.ts # Investigation state
│   │   ├── pipelineStore.ts   # Pipeline state
│   │   └── uiStore.ts         # UI state
│   ├── services/              # External services
│   │   ├── api.ts             # API client configuration
│   │   ├── websocket.ts       # WebSocket service
│   │   └── storage.ts         # Local storage utilities
│   ├── types/                 # TypeScript type definitions
│   │   ├── investigation.ts   # Investigation types
│   │   ├── pipeline.ts        # Pipeline types
│   │   ├── agent.ts           # Agent types
│   │   └── api.ts             # API response types
│   ├── utils/                 # Utility functions
│   │   ├── formatters.ts      # Data formatting
│   │   ├── validators.ts      # Validation utilities
│   │   └── constants.ts       # Application constants
│   ├── styles/                # Global styles
│   │   ├── globals.css        # Global CSS
│   │   └── components.css     # Component-specific styles
│   ├── App.tsx                # Root application component
│   ├── main.tsx               # Application entry point
│   └── vite-env.d.ts          # Vite type definitions
├── package.json               # Dependencies and scripts
├── tsconfig.json              # TypeScript configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── vite.config.ts             # Vite build configuration
└── Dockerfile                 # Container configuration
```

## Component Architecture

### Component Hierarchy

```
App
├── Header
├── SplitView
│   ├── Sidebar
│   │   ├── Navigation
│   │   └── QuickActions
│   └── MainContent
│       ├── InvestigationDashboard
│       │   ├── EvidencePanel
│       │   ├── SourceManager
│       │   └── TimelineView
│       ├── PipelinePanel
│       │   ├── PipelineEditor
│       │   └── FlowVisualizer
│       └── AgentCoordinator
│           ├── AgentChat
│           └── ApprovalManager
└── StatusBar
```

### Component Patterns

#### 1. Container/Presentation Pattern
```typescript
// Container Component (logic)
const InvestigationContainer: React.FC = () => {
  const { investigation, loading } = useInvestigation();
  const { createEvidence } = useEvidence();
  
  return (
    <InvestigationDashboard
      investigation={investigation}
      loading={loading}
      onEvidenceCreate={createEvidence}
    />
  );
};

// Presentation Component (UI)
const InvestigationDashboard: React.FC<InvestigationDashboardProps> = ({
  investigation,
  loading,
  onEvidenceCreate
}) => {
  // Pure UI rendering logic
};
```

#### 2. Custom Hooks Pattern
```typescript
// WebSocket Hook
const useWebSocket = (pipelineId: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/api/ws/${pipelineId}`);
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };
    
    setSocket(ws);
    
    return () => ws.close();
  }, [pipelineId]);
  
  const sendMessage = useCallback((message: Message) => {
    socket?.send(JSON.stringify(message));
  }, [socket]);
  
  return { messages, sendMessage };
};
```

#### 3. State Management Pattern
```typescript
// Zustand Store
interface InvestigationStore {
  investigations: Investigation[];
  currentInvestigation: Investigation | null;
  loading: boolean;
  
  // Actions
  setInvestigations: (investigations: Investigation[]) => void;
  setCurrentInvestigation: (investigation: Investigation | null) => void;
  createInvestigation: (data: CreateInvestigationData) => Promise<void>;
  updateInvestigation: (id: string, data: UpdateInvestigationData) => Promise<void>;
}

const useInvestigationStore = create<InvestigationStore>((set, get) => ({
  investigations: [],
  currentInvestigation: null,
  loading: false,
  
  setInvestigations: (investigations) => set({ investigations }),
  setCurrentInvestigation: (currentInvestigation) => set({ currentInvestigation }),
  
  createInvestigation: async (data) => {
    set({ loading: true });
    try {
      const investigation = await api.createInvestigation(data);
      set(state => ({
        investigations: [...state.investigations, investigation],
        currentInvestigation: investigation,
        loading: false
      }));
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  }
}));
```

## State Management Architecture

### Client State (Zustand)

#### Investigation Store
```typescript
interface InvestigationState {
  // Data
  investigations: Investigation[];
  currentInvestigation: Investigation | null;
  evidence: Evidence[];
  sources: Source[];
  
  // UI State
  loading: boolean;
  error: string | null;
  selectedEvidence: string | null;
  
  // Actions
  fetchInvestigations: () => Promise<void>;
  createInvestigation: (data: CreateInvestigationData) => Promise<void>;
  updateInvestigation: (id: string, data: Partial<Investigation>) => Promise<void>;
  deleteInvestigation: (id: string) => Promise<void>;
  setCurrentInvestigation: (investigation: Investigation | null) => void;
}
```

#### Pipeline Store
```typescript
interface PipelineState {
  pipelines: Pipeline[];
  currentPipeline: Pipeline | null;
  nodes: PipelineNode[];
  edges: PipelineEdge[];
  
  // Actions
  fetchPipelines: () => Promise<void>;
  createPipeline: (data: CreatePipelineData) => Promise<void>;
  updatePipeline: (id: string, data: Partial<Pipeline>) => Promise<void>;
  executePipeline: (id: string) => Promise<void>;
}
```

#### UI Store
```typescript
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activePanel: string;
  notifications: Notification[];
  
  // Actions
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setActivePanel: (panel: string) => void;
  addNotification: (notification: Notification) => void;
}
```

### Server State (React Query)

```typescript
// API Hooks
export const useInvestigations = () => {
  return useQuery({
    queryKey: ['investigations'],
    queryFn: () => api.getInvestigations(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useInvestigation = (id: string) => {
  return useQuery({
    queryKey: ['investigation', id],
    queryFn: () => api.getInvestigation(id),
    enabled: !!id,
  });
};

export const useCreateInvestigation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: api.createInvestigation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations'] });
    },
  });
};
```

## Communication Architecture

### HTTP Client (Axios)

```typescript
// API Configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh
      await refreshToken();
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### WebSocket Communication

```typescript
// WebSocket Service
class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(pipelineId: string) {
    const wsUrl = `${WS_BASE_URL}/api/ws/${pipelineId}`;
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(pipelineId);
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  private attemptReconnect(pipelineId: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect(pipelineId);
      }, 1000 * Math.pow(2, this.reconnectAttempts)); // Exponential backoff
    }
  }
  
  sendMessage(message: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }
}
```

## Routing Architecture

```typescript
// Route Configuration
const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: <Navigate to="/investigations" replace />,
      },
      {
        path: 'investigations',
        children: [
          {
            index: true,
            element: <InvestigationList />,
          },
          {
            path: ':id',
            element: <InvestigationDetail />,
            children: [
              {
                path: 'evidence',
                element: <EvidencePanel />,
              },
              {
                path: 'timeline',
                element: <TimelineView />,
              },
            ],
          },
        ],
      },
      {
        path: 'pipelines',
        children: [
          {
            index: true,
            element: <PipelineList />,
          },
          {
            path: ':id',
            element: <PipelineDetail />,
          },
          {
            path: 'new',
            element: <PipelineEditor />,
          },
        ],
      },
      {
        path: 'agents',
        element: <AgentCoordinator />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
    ],
  },
]);

// Protected Routes
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};
```

## Form Architecture

```typescript
// Form Validation with Zod
const investigationSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title too long'),
  description: z.string().min(1, 'Description is required'),
  classification: z.enum(['PUBLIC', 'CONFIDENTIAL', 'SECRET']),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
  tags: z.array(z.string()).optional(),
});

type InvestigationFormData = z.infer<typeof investigationSchema>;

// Form Component
const InvestigationForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<InvestigationFormData>({
    resolver: zodResolver(investigationSchema),
  });
  
  const { createInvestigation } = useInvestigationStore();
  
  const onSubmit = async (data: InvestigationFormData) => {
    try {
      await createInvestigation(data);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          {...register('title')}
          className="w-full px-3 py-2 border rounded"
        />
        {errors.title && (
          <p className="text-red-500 text-sm">{errors.title.message}</p>
        )}
      </div>
      
      {/* Other form fields */}
      
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-500 text-white py-2 rounded"
      >
        {isSubmitting ? 'Creating...' : 'Create Investigation'}
      </button>
    </form>
  );
};
```

## Real-time Architecture

### WebSocket Integration

```typescript
// Real-time Updates Hook
const useRealtimeUpdates = (pipelineId: string) => {
  const [messages, setMessages] = useState<RealtimeMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  
  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/api/ws/${pipelineId}`);
    
    ws.onopen = () => {
      setConnectionStatus('connected');
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
      
      // Handle different message types
      switch (message.type) {
        case 'pipeline_update':
          // Update pipeline state
          break;
        case 'task_complete':
          // Handle task completion
          break;
        case 'error':
          // Handle errors
          break;
      }
    };
    
    ws.onclose = () => {
      setConnectionStatus('disconnected');
    };
    
    return () => ws.close();
  }, [pipelineId]);
  
  return { messages, connectionStatus };
};
```

## Performance Architecture

### Code Splitting

```typescript
// Lazy Loading Components
const InvestigationDetail = lazy(() => import('./components/OSINT/InvestigationDetail'));
const PipelineEditor = lazy(() => import('./components/Pipeline/PipelineEditor'));
const AgentCoordinator = lazy(() => import('./components/Agent/AgentCoordinator'));

// Route-based code splitting
const router = createBrowserRouter([
  {
    path: '/investigations/:id',
    element: (
      <Suspense fallback={<LoadingScreen />}>
        <InvestigationDetail />
      </Suspense>
    ),
  },
]);
```

### Memoization

```typescript
// Memoized Components
const EvidenceCard = React.memo<EvidenceCardProps>(({ evidence, onUpdate }) => {
  return (
    <div className="border rounded p-4">
      <h3>{evidence.title}</h3>
      <p>{evidence.description}</p>
      <button onClick={() => onUpdate(evidence.id)}>
        Update
      </button>
    </div>
  );
});

// Memoized Calculations
const useFilteredEvidence = (evidence: Evidence[], filter: string) => {
  return useMemo(() => {
    return evidence.filter(item =>
      item.title.toLowerCase().includes(filter.toLowerCase()) ||
      item.description.toLowerCase().includes(filter.toLowerCase())
    );
  }, [evidence, filter]);
};
```

## Testing Architecture

### Component Testing

```typescript
// InvestigationDashboard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { InvestigationDashboard } from './InvestigationDashboard';

describe('InvestigationDashboard', () => {
  const mockInvestigation = {
    id: '1',
    title: 'Test Investigation',
    description: 'Test Description',
    status: 'active',
  };
  
  it('renders investigation details', () => {
    render(<InvestigationDashboard investigation={mockInvestigation} />);
    
    expect(screen.getByText('Test Investigation')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });
  
  it('handles evidence creation', async () => {
    const onCreateEvidence = jest.fn();
    
    render(
      <InvestigationDashboard 
        investigation={mockInvestigation} 
        onCreateEvidence={onCreateEvidence}
      />
    );
    
    fireEvent.click(screen.getByText('Add Evidence'));
    
    await waitFor(() => {
      expect(onCreateEvidence).toHaveBeenCalledWith(mockInvestigation.id);
    });
  });
});
```

### Hook Testing

```typescript
// useWebSocket.test.ts
import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from './useWebSocket';

describe('useWebSocket', () => {
  let mockWebSocket: jest.Mocked<WebSocket>;
  
  beforeEach(() => {
    mockWebSocket = {
      addEventListener: jest.fn(),
      send: jest.fn(),
      close: jest.fn(),
    } as any;
    
    global.WebSocket = jest.fn(() => mockWebSocket);
  });
  
  it('connects to WebSocket on mount', () => {
    renderHook(() => useWebSocket('test-pipeline'));
    
    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/api/ws/test-pipeline');
  });
  
  it('sends messages', () => {
    const { result } = renderHook(() => useWebSocket('test-pipeline'));
    
    act(() => {
      result.current.sendMessage({ type: 'test', content: 'message' });
    });
    
    expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
      type: 'test',
      content: 'message'
    }));
  });
});
```

## Security Architecture

### Authentication

```typescript
// Auth Hook
const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Validate token with backend
      validateToken(token)
        .then(({ user }) => {
          setUser(user);
          setIsAuthenticated(true);
        })
        .catch(() => {
          localStorage.removeItem('access_token');
        });
    }
  }, []);
  
  const login = async (credentials: LoginCredentials) => {
    const response = await api.post('/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    setUser(user);
    setIsAuthenticated(true);
  };
  
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
  };
  
  return { isAuthenticated, user, login, logout };
};
```

### Input Validation

```typescript
// Sanitization and Validation
import { z } from 'zod';

// Schema validation for API responses
const apiResponseSchema = z.object({
  data: z.any(),
  message: z.string(),
  status: z.enum(['success', 'error']),
});

// XSS Prevention
const sanitizeInput = (input: string): string => {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
};
```

## Deployment Architecture

### Build Process

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react', 'lucide-react'],
          utils: ['axios', 'zustand'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

### Docker Configuration

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Conclusion

The ScrapeCraft frontend represents a modern, scalable, and maintainable architecture for complex OSINT operations. Its component-based design, comprehensive state management, and real-time capabilities provide an excellent foundation for both current requirements and future enhancements.

The architecture emphasizes:
- **Type Safety**: Full TypeScript coverage
- **Performance**: Optimized rendering and code splitting
- **User Experience**: Real-time updates and responsive design
- **Maintainability**: Modular structure and comprehensive testing
- **Security**: Authentication, validation, and XSS protection
- **Scalability**: Efficient state management and lazy loading

This foundation enables rapid development of sophisticated OSINT tools while maintaining code quality and user experience standards.