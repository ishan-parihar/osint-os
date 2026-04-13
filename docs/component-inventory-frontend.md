# ScrapeCraft Frontend Component Inventory

This document provides a comprehensive inventory of all UI components in the ScrapeCraft frontend application, including their categorization, props interfaces, design patterns, and state management integration.

## Component Architecture Overview

The ScrapeCraft frontend follows a modular, feature-based component architecture with clear separation of concerns:

- **Common Components**: Reusable UI building blocks
- **Layout Components**: Application shell and navigation
- **Feature Components**: Domain-specific functionality (OSINT, Chat, Pipeline, Workflow)
- **Settings Components**: Configuration and preferences

## Component Categories

### 📁 Common Components (src/components/Common/)

Reusable UI components that form the design system foundation.

#### Button.tsx
**Purpose**: Primary button component with multiple variants and states
**Props**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  loading?: boolean;
  as?: React.ElementType;
  href?: string;
}
```
**Features**:
- Multiple visual variants (primary, secondary, destructive)
- Three size options (sm, md, lg)
- Loading state with spinner
- Custom render component support
- Full accessibility support
- Focus ring and hover states

---

#### Input.tsx
**Purpose**: Text input component with error handling
**Props**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}
```
**Features**:
- Error message display
- Focus states and transitions
- Disabled state handling
- Full HTML input attribute support

---

#### LoadingSpinner.tsx
**Purpose**: Animated loading indicator
**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```
**Features**:
- Three size variations
- Custom className support
- Smooth rotation animation

---

#### LoadingScreen.tsx
**Purpose**: Full-screen loading overlay for application initialization
**Props**: None
**Features**:
- Logo animation
- Branded loading message
- Fixed positioning with high z-index
- Integration with application initialization flow

---

#### ClassificationBanner.tsx
**Purpose**: Security classification banner for investigations
**Props**:
```typescript
interface ClassificationBannerProps {
  classification: 'UNCLASSIFIED' | 'CONFIDENTIAL' | 'SECRET' | 'TOP_SECRET';
  compact?: boolean;
}
```
**Features**:
- Four classification levels with distinct styling
- Compact and full display modes
- Color-coded security levels
- Dual display (mirrored text) for full mode

---

### 📁 Layout Components (src/components/Layout/)

Core application layout and navigation components.

#### Header.tsx
**Purpose**: Application header with navigation and controls
**Props**: None
**Features**:
- Logo and branding
- Current investigation display
- New investigation creation
- Settings modal trigger
- Integration with investigation store
- Responsive design

---

#### SplitView.tsx
**Purpose**: Main application layout with resizable panels
**Props**: None
**Features**:
- Resizable panel layout (Agent Coordinator, Chat, Dashboard)
- Draggable divider with visual feedback
- Integration with agent coordination and investigation dashboard
- Keyboard navigation support
- Responsive breakpoints

---

#### StatusBar.tsx
**Purpose**: Application status bar with system information
**Props**: None
**Features**:
- Investigation status display
- Target and evidence counts
- WebSocket connection status
- Real-time status updates
- System information display

---

### 📁 Chat Components (src/components/Chat/)

Real-time chat interface for investigation planning and communication.

#### ChatContainer.tsx
**Purpose**: Chat interface wrapper with investigation context
**Props**: None
**Features**:
- Investigation context integration
- Empty state handling
- Integration with InvestigationPlanner
- Responsive layout

---

#### MessageList.tsx
**Purpose**: Scrollable message display with auto-scroll
**Props**:
```typescript
interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}
```
**Features**:
- Auto-scroll to latest message
- Loading indicator during AI responses
- Smooth scroll behavior
- Message bubble rendering

---

#### MessageBubble.tsx
**Purpose**: Individual message display with rich content support
**Props**:
```typescript
interface MessageBubbleProps {
  message: ChatMessage;
}
```
**Features**:
- User/AI message differentiation
- Markdown rendering with syntax highlighting
- Timestamp formatting
- Tool usage display
- Avatar and role indicators
- Responsive design with max-width constraints

---

#### InputArea.tsx
**Purpose**: Message input with quick actions and keyboard shortcuts
**Props**:
```typescript
interface InputAreaProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
  placeholder?: string;
  quickActions?: string[];
  onQuickAction?: (action: string) => void;
}
```
**Features**:
- Multi-line text input with auto-resize
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Quick action buttons
- Loading state handling
- Form submission handling

---

#### QuickActions.tsx
**Purpose**: Predefined action buttons for common tasks
**Props**:
```typescript
interface QuickActionsProps {
  onAction: (action: string) => void;
  actions: string[];
  disabled?: boolean;
}
```
**Features**:
- Dynamic action button generation
- Disabled state handling
- Responsive button layout
- Integration with input area

---

#### StreamingMessage.tsx
**Purpose**: Real-time streaming message display
**Props**:
```typescript
interface StreamingMessageProps {
  content: string;
  isComplete: boolean;
  timestamp: string;
}
```
**Features**:
- Real-time content updates
- Typing indicator animation
- Markdown rendering
- Completion state handling

---

### 📁 OSINT Components (src/components/OSINT/)

Domain-specific components for OSINT investigation management.

#### InvestigationDashboard.tsx
**Purpose**: Main investigation management interface
**Props**:
```typescript
interface InvestigationDashboardProps {
  investigation: Investigation;
  onPhaseChange: (phase: string) => void;
  onAgentAssignment: (assignment: any) => void;
}
```
**Features**:
- Tabbed interface (Overview, Targets, Search, Agents, Evidence, Analysis, Threats, Reports)
- Classification banner integration
- Real-time investigation updates
- Agent assignment coordination
- Phase transition management

---

#### TargetManager.tsx
**Purpose**: Investigation target management and tracking
**Props**:
```typescript
interface TargetManagerProps {
  targets: InvestigationTarget[];
}
```
**Features**:
- Target list with search and filtering
- Target type categorization (PERSON, ORGANIZATION, LOCATION, etc.)
- Priority and status indicators
- Detailed target information display
- Alias management
- Collection requirements tracking

---

#### SearchComponent.tsx
**Purpose**: Integrated web search for investigations
**Props**:
```typescript
interface SearchComponentProps {
  investigationId?: string;
  onSearchComplete?: (results: SearchResponse) => void;
  placeholder?: string;
  className?: string;
}
```
**Features**:
- Real-time web search integration
- Investigation-scoped search
- Search result display with scoring
- Source attribution
- Error handling and retry logic
- Search metadata display

---

#### EvidenceViewer.tsx
**Purpose**: Collected evidence management and analysis
**Props**:
```typescript
interface EvidenceViewerProps {
  investigationId?: string;
}
```
**Features**:
- Evidence list with advanced filtering
- Source type categorization
- Reliability and relevance scoring
- Detailed evidence inspection
- Tag management
- Related evidence linking
- Metadata display

---

#### ThreatAssessment.tsx
**Purpose**: Threat analysis and risk assessment
**Props**:
```typescript
interface ThreatAssessmentProps {
  investigationId?: string;
  threats?: ThreatAssessmentType[];
}
```
**Features**:
- Threat level visualization
- Risk scoring calculations
- Indicators and recommendations display
- Threat categorization
- Mitigation strategies
- Source attribution

---

#### AnalysisView.tsx
**Purpose**: Evidence analysis and correlation tools
**Props**: Not explicitly defined (receives evidence and analysis results)
**Features**:
- Evidence correlation analysis
- Pattern detection
- Timeline analysis
- Relationship mapping

---

#### Reports.tsx
**Purpose**: Investigation report generation and management
**Props**: Not explicitly defined (receives reports array)
**Features**:
- Report generation tools
- Classification handling
- Distribution management
- Approval workflows

---

#### InvestigationPlanner.tsx (src/components/OSINT/Chat/)
**Purpose**: AI-powered investigation planning interface
**Props**:
```typescript
interface InvestigationPlannerProps {
  investigationId: string;
}
```
**Features**:
- Real-time AI investigation planning
- WebSocket integration for live updates
- Investigation status monitoring
- Error handling with fallback polling
- Quick action templates
- Progress tracking

---

### 📁 Workflow Components (src/components/Workflow/)

Agent coordination and workflow management components.

#### AgentCoordinator.tsx
**Purpose**: AI agent management and coordination interface
**Props**: None
**Features**:
- Real-time agent status monitoring
- Agent task assignment
- Performance metrics display
- WebSocket integration
- Agent lifecycle management
- Event logging
- Connection status monitoring

---

#### WorkflowSidebar.tsx
**Purpose**: Workflow navigation and control sidebar
**Props**: Not explicitly defined
**Features**:
- Workflow step navigation
- Progress tracking
- Quick access controls

---

#### ApprovalManager.tsx
**Purpose**: Investigation approval and sign-off workflows
**Props**: Not explicitly defined
**Features**:
- Approval chain management
- Sign-off tracking
- Role-based approvals

---

#### ApprovalDialog.tsx
**Purpose**: Modal dialog for approval actions
**Props**: Not explicitly defined
**Features**:
- Approval confirmation
- Comment capture
- Decision logging

---

### 📁 Pipeline Components (src/components/Pipeline/)

Data processing and pipeline management components.

#### PipelinePanel.tsx
**Purpose**: Pipeline configuration and execution interface
**Props**: None
**Features**:
- Tabbed pipeline management (URLs, Schema, Code, Output)
- Pipeline execution control
- Real-time progress monitoring

---

#### URLManager.tsx
**Purpose**: URL collection and management for pipelines
**Props**: Not explicitly defined
**Features**:
- URL list management
- Validation and testing
- Bulk import capabilities

---

#### SchemaEditor.tsx
**Purpose**: Data schema definition and editing
**Props**: Not explicitly defined
**Features**:
- Visual schema builder
- Field type configuration
- Validation rules

---

#### CodeViewer.tsx
**Purpose**: Pipeline code display and editing
**Props**: Not explicitly defined
**Features**:
- Syntax highlighting
- Code editing
- Error display

---

#### OutputView.tsx
**Purpose**: Pipeline execution results display
**Props**: Not explicitly defined
**Features**:
- Results visualization
- Export capabilities
- Error handling

---

#### OutputDisplay.tsx
**Purpose**: Real-time pipeline output monitoring
**Props**: Not explicitly defined
**Features**:
- Live output streaming
- Progress indicators
- Error highlighting

---

### 📁 Settings Components (src/components/Settings/)

Application configuration and preferences management.

#### SettingsModal.tsx
**Purpose**: Application settings and API key management
**Props**:
```typescript
interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```
**Features**:
- API key management (OpenRouter, ScrapeGraph)
- Modal overlay with backdrop
- Form validation
- Success/error messaging
- Keyboard navigation (ESC to close)

---

## Design System Patterns

### Color Scheme
- **Primary**: Blue tones for main actions
- **Secondary**: Gray tones for secondary elements
- **Success**: Green for positive states
- **Warning**: Yellow/Orange for caution states
- **Error**: Red for error states
- **Muted**: Subtle gray for disabled/secondary text

### Typography
- **Headings**: Font-semibold with size variations
- **Body**: Regular weight with good line height
- **Small**: text-sm for captions and metadata
- **Code**: Monospace with syntax highlighting

### Spacing
- Consistent use of Tailwind spacing scale
- Padding: 1, 2, 3, 4, 6 units
- Margin: 1, 2, 3, 4, 6 units
- Gap: 1, 2, 3, 4 units

### Borders & Shadows
- Border radius: rounded-md, rounded-lg, rounded-full
- Border colors: border-border, border-primary
- Shadow: Shadow-md for hover states

### Animation
- Transitions: duration-200 for smooth interactions
- Animations: animate-spin, animate-pulse, animate-bounce
- Custom animations: animate-slide-up, animate-fade-in

## State Management Integration

### Zustand Stores

#### useInvestigationStore
**Components Using**:
- Header.tsx
- SplitView.tsx
- StatusBar.tsx
- ChatContainer.tsx
- InvestigationPlanner.tsx
- AgentCoordinator.tsx

**Features**:
- Investigation CRUD operations
- Target management
- Evidence collection
- Threat assessment
- Report generation

#### useChatStore
**Components Using**:
- MessageList.tsx
- InputArea.tsx
- InvestigationPlanner.tsx

**Features**:
- Message management
- Real-time chat
- AI integration
- Message history

#### useWebSocketStore
**Components Using**:
- StatusBar.tsx
- InvestigationPlanner.tsx
- AgentCoordinator.tsx

**Features**:
- Real-time connectivity
- Event handling
- Status monitoring
- Error recovery

## Props Interface Patterns

### Common Patterns
1. **Extending HTML Props**: `extends React.ButtonHTMLAttributes<HTMLButtonElement>`
2. **Optional Props**: Default values provided for most optional props
3. **Children Props**: `children: React.ReactNode` for composition
4. **Callback Props**: `onAction: (value: string) => void` pattern
5. **State Props**: `isLoading: boolean`, `error: string | null`

### Data Flow Patterns
1. **Top-down Data Flow**: Props passed from parent to child
2. **Event Bubbling**: Callbacks passed up for state updates
3. **Store Integration**: Direct store access in components
4. **Context Sharing**: Investigation context shared across components

## Component Reusability

### Highly Reusable
- Button, Input, LoadingSpinner (Common/)
- MessageBubble, InputArea (Chat/)
- ClassificationBanner (Common/)

### Domain-Specific
- InvestigationDashboard, TargetManager (OSINT/)
- AgentCoordinator (Workflow/)
- PipelinePanel (Pipeline/)

### Configuration-Driven
- SettingsModal (Settings/)
- SearchComponent (OSINT/)

## Testing Coverage

### Test Files Found
- `Button.test.tsx` - Unit tests for Button component

### Testing Recommendations
- Add unit tests for all Common components
- Add integration tests for OSINT workflows
- Add E2E tests for complete investigation flows
- Add accessibility tests for all interactive components

## Technology Stack

### Core Dependencies
- **React 18.2.0**: Component framework
- **TypeScript 4.9.5**: Type safety
- **Tailwind CSS 3.4.18**: Styling
- **Zustand 4.5.7**: State management

### UI Dependencies
- **clsx 2.1.0**: Conditional class names
- **react-markdown 10.1.0**: Markdown rendering
- **remark-gfm 4.0.1**: GitHub-flavored markdown
- **date-fns 3.6.0**: Date formatting

### Code Highlighting
- **prismjs 1.29.0**: Syntax highlighting
- **@types/prismjs 1.26.0**: TypeScript definitions

## Accessibility Features

### Keyboard Navigation
- Tab order management
- Enter/Space key interactions
- Escape key for modals
- Shift+Enter for new lines in text areas

### Screen Reader Support
- Semantic HTML elements
- ARIA labels and roles
- Focus indicators
- Status announcements

### Visual Accessibility
- High contrast colors
- Focus ring indicators
- Loading state indicators
- Error message handling

## Performance Considerations

### Optimization Strategies
- Component memoization where appropriate
- Lazy loading for heavy components
- Efficient re-rendering with proper dependencies
- Virtual scrolling for large lists (potential improvement)

### Bundle Optimization
- Component-based code splitting opportunities
- Dynamic imports for heavy dependencies
- Tree shaking for unused components

## Future Enhancements

### Component Library
- Storybook integration for component documentation
- Design system token standardization
- Component variant system
- Theme support (dark/light modes)

### Advanced Features
- Drag-and-drop interfaces
- Advanced filtering and search
- Real-time collaboration
- Mobile-responsive improvements
- Progressive web app capabilities

---

*This inventory was generated on November 10, 2025, and reflects the current state of the ScrapeCraft frontend component architecture.*