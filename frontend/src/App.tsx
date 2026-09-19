import {
  Activity,
  Bell,
  Boxes,
  ChevronDown,
  CircleCheck,
  Cloud,
  HeartPulse,
  LayoutDashboard,
  Menu,
  Search,
  Server,
  Settings2,
  ShieldAlert,
  Terminal,
  TriangleAlert,
} from 'lucide-react'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import './App.css'

const activityData = [
  { time: '09:00', requests: 32 },
  { time: '09:30', requests: 42 },
  { time: '10:00', requests: 38 },
  { time: '10:30', requests: 55 },
  { time: '11:00', requests: 47 },
  { time: '11:30', requests: 62 },
  { time: '12:00', requests: 58 },
  { time: '12:30', requests: 71 },
  { time: '13:00', requests: 64 },
  { time: '13:30', requests: 79 },
  { time: '14:00', requests: 73 },
]

const navigation = [
  { label: 'Overview', icon: LayoutDashboard, active: true },
  { label: 'Infrastructure', icon: Server, active: false },
  { label: 'Log Explorer', icon: Terminal, active: false },
  { label: 'Predictive Alerts', icon: ShieldAlert, active: false },
  { label: 'Analytics', icon: Activity, active: false },
]

const events = [
  {
    type: 'success',
    title: 'Health check completed',
    description: 'Application responding normally',
    time: '14:32:08',
  },
  {
    type: 'warning',
    title: 'High response time detected',
    description: 'Performance degradation warning',
    time: '14:31:42',
  },
  {
    type: 'success',
    title: 'Application endpoint accessed',
    description: 'HTTP 200 response',
    time: '14:30:15',
  },
]

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-symbol">
            <Search size={22} strokeWidth={2.2} />
          </div>

          <div>
            <div className="brand-name">AnomaLens</div>
            <div className="brand-caption">INFRASTRUCTURE INTELLIGENCE</div>
          </div>
        </div>

        <div className="workspace">
          <div className="workspace-icon">
            <Cloud size={18} />
          </div>

          <div className="workspace-details">
            <strong>Local Workspace</strong>
            <span>Development environment</span>
          </div>

          <ChevronDown size={15} className="muted-icon" />
        </div>

        <div className="navigation-heading">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <div
                key={item.label}
                className={`navigation-item ${
                  item.active ? 'active' : ''
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </div>
            )
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="navigation-item">
            <Settings2 size={18} />
            <span>Settings</span>
          </div>

          <div className="sidebar-profile">
            <div className="profile-avatar">A</div>

            <div>
              <strong>AnomaLens</strong>
              <span>Development console</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <Menu size={18} />
            <span>Workspace</span>
            <span className="breadcrumb-divider">/</span>
            <strong>Overview</strong>
          </div>

          <div className="topbar-actions">
            <span className="environment-badge">
              <span className="environment-dot" />
              Demo environment
            </span>

            <button
              className="icon-button"
              aria-label="Notifications"
            >
              <Bell size={19} />
            </button>

            <div className="topbar-avatar">A</div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">MONITORING / OVERVIEW</div>

              <h1>Infrastructure Overview</h1>

              <p>
                Monitor application health, Kubernetes workloads,
                and predictive failure signals.
              </p>
            </div>

            <div className="page-status">
              <span className="status-dot" />
              Prototype dashboard
            </div>
          </section>

          <section className="metrics-grid">
            <div className="metric-card">
              <div className="metric-top">
                <span>Application Health</span>
                <HeartPulse size={19} />
              </div>

              <div className="metric-value healthy">Healthy</div>

              <div className="metric-footer">
                <CircleCheck size={14} />
                Illustrative application status
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-top">
                <span>Running Pods</span>
                <Boxes size={19} />
              </div>

              <div className="metric-value">1 / 1</div>

              <div className="metric-footer">
                Kubernetes workload example
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-top">
                <span>Predicted Failure Risk</span>
                <ShieldAlert size={19} />
              </div>

              <div className="metric-value warning">Elevated</div>

              <div className="metric-footer">
                <TriangleAlert size={14} />
                Illustrative warning state
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-top">
                <span>Active Alerts</span>
                <Bell size={19} />
              </div>

              <div className="metric-value">02</div>

              <div className="metric-footer">
                Illustrative alert count
              </div>
            </div>
          </section>

          <section className="dashboard-grid">
            <div className="panel activity-panel">
              <div className="panel-header">
                <div>
                  <h2>Application Activity</h2>
                  <p>Illustrative request activity over time</p>
                </div>

                <span className="panel-tag">Demo data</span>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={activityData}>
                    <defs>
                      <linearGradient
                        id="activityGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor="#8b919b"
                          stopOpacity={0.24}
                        />
                        <stop
                          offset="100%"
                          stopColor="#8b919b"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      stroke="#292b30"
                      strokeDasharray="3 5"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#777b83"
                      tickLine={false}
                      axisLine={false}
                      tick={{ fontSize: 11 }}
                    />

                    <YAxis
                      stroke="#777b83"
                      tickLine={false}
                      axisLine={false}
                      tick={{ fontSize: 11 }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: '#1b1d21',
                        border: '1px solid #34363c',
                        borderRadius: 10,
                        color: '#f5f5f5',
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="requests"
                      stroke="#b3b7bf"
                      strokeWidth={2.5}
                      fill="url(#activityGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel risk-panel">
              <div className="panel-header">
                <div>
                  <h2>Failure Risk</h2>
                  <p>Predictive monitoring</p>
                </div>

                <ShieldAlert size={19} className="panel-icon" />
              </div>

              <div className="risk-display">
                <div className="risk-ring">
                  <div className="risk-ring-inner">
                    <span className="risk-percentage">75%</span>
                    <span className="risk-label">DEMO VALUE</span>
                  </div>
                </div>

                <div className="risk-status">Elevated Risk</div>

                <p>
                  Example of how a potential failure warning
                  will appear once live prediction is connected.
                </p>
              </div>

              <div className="risk-footer">
                <span className="risk-indicator" />
                Illustrative prediction, not live model output
              </div>
            </div>
          </section>

          <section className="panel events-panel">
            <div className="panel-header">
              <div>
                <h2>Recent Activity</h2>
                <p>Application events and monitoring signals</p>
              </div>

              <span className="panel-tag">Sample events</span>
            </div>

            <div className="event-list">
              {events.map((event, index) => (
                <div className="event-row" key={index}>
                  <div
                    className={`event-icon ${
                      event.type === 'warning'
                        ? 'event-warning'
                        : 'event-success'
                    }`}
                  >
                    {event.type === 'warning' ? (
                      <TriangleAlert size={17} />
                    ) : (
                      <CircleCheck size={17} />
                    )}
                  </div>

                  <div className="event-description">
                    <strong>{event.title}</strong>
                    <span>{event.description}</span>
                  </div>

                  <span className="event-time">{event.time}</span>

                  <span
                    className={`event-badge ${
                      event.type === 'warning'
                        ? 'badge-warning'
                        : 'badge-success'
                    }`}
                  >
                    {event.type === 'warning' ? 'WARNING' : 'INFO'}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <div className="dashboard-footer">
            AnomaLens · Controlled experimental prototype
          </div>
        </div>
      </main>
    </div>
  )
}

export default App