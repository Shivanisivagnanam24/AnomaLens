
import { useEffect, useState } from 'react'


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
import Analytics from './Analytics'

const API_BASE = 'http://127.0.0.1:8000'

type InfrastructureResponse = {
  connected: boolean
  total_pods: number | null
  ready_pods: number | null
  pods: {
    name: string
    phase: string
    ready: boolean
    restart_count: number
  }[]
  error?: string
}

type LogsResponse = {
  connected: boolean
  pod?: string | null
  entries: {
    timestamp: string
    level: string
    message: string
  }[]
  error?: string
}

type PredictionEvent = {
  timestamp: string
  event_type: string
  message: string
}

type PredictionResponse = {
  status: string
  pod?: string
  model?: string
  prediction?: number
  prediction_label?: string
  failure_probability?: number | null
  features?: Record<string, number>
  recent_events?: PredictionEvent[]
  recognized_event_count?: number
  checked_at?: string
  note?: string
  message?: string
}

type RecordedAlert = {
  id: string
  created_at: string
  pod: string
  prediction: number
  prediction_label: string
  failure_probability: number | null
  features: Record<string, number>
  recent_events: PredictionEvent[]
  status: string
  evaluation_context: string
}

type AlertsResponse = {
  status: string
  count: number
  alerts: RecordedAlert[]
  storage_file?: string
  checked_at?: string
}

const navigation = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Infrastructure', icon: Server },
  { label: 'Log Explorer', icon: Terminal },
  { label: 'Predictive Alerts', icon: ShieldAlert },
  { label: 'Analytics', icon: Activity },
]

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

function formatTime(value: string) {
  const date = new Date(value)

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString()
}

function formatProbability(value: number | null | undefined) {
  return value === null || value === undefined
    ? 'N/A'
    : `${Math.round(value * 100)}%`
}

function App() {
  const [activePage, setActivePage] = useState('Overview')

  const [infrastructure, setInfrastructure] =
    useState<InfrastructureResponse | null>(null)

  const [logs, setLogs] =
    useState<LogsResponse | null>(null)

  const [prediction, setPrediction] =
    useState<PredictionResponse | null>(null)

  const [alerts, setAlerts] =
    useState<AlertsResponse | null>(null)

  const [infrastructureError, setInfrastructureError] =
    useState(false)

  const [logsError, setLogsError] =
    useState(false)

  const [predictionError, setPredictionError] =
    useState(false)

  const [alertsError, setAlertsError] =
    useState(false)

  useEffect(() => {
    let active = true

    async function fetchData() {
      try {
        const response = await fetch(
          `${API_BASE}/api/infrastructure`
        )

        if (!response.ok) {
          throw new Error('Infrastructure request failed')
        }

        const data: InfrastructureResponse =
          await response.json()

        if (active) {
          setInfrastructure(data)
          setInfrastructureError(false)
        }
      } catch {
        if (active) {
          setInfrastructure(null)
          setInfrastructureError(true)
        }
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/logs`
        )

        if (!response.ok) {
          throw new Error('Log request failed')
        }

        const data: LogsResponse =
          await response.json()

        if (active) {
          setLogs(data)
          setLogsError(false)
        }
      } catch {
        if (active) {
          setLogs(null)
          setLogsError(true)
        }
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/prediction`
        )

        if (!response.ok) {
          throw new Error('Prediction request failed')
        }

        const data: PredictionResponse =
          await response.json()

        if (active) {
          setPrediction(data)
          setPredictionError(false)
        }
      } catch {
        if (active) {
          setPrediction(null)
          setPredictionError(true)
        }
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/alerts`
        )

        if (!response.ok) {
          throw new Error('Alert history request failed')
        }

        const data: AlertsResponse =
          await response.json()

        if (active) {
          setAlerts(data)
          setAlertsError(false)
        }
      } catch {
        if (active) {
          setAlerts(null)
          setAlertsError(true)
        }
      }
    }

    void fetchData()

    const interval = window.setInterval(() => {
      void fetchData()
    }, 10000)

    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [])

  const readyPods =
    infrastructure?.connected
      ? infrastructure.ready_pods
      : null

  const totalPods =
    infrastructure?.connected
      ? infrastructure.total_pods
      : null

  const healthLabel = infrastructureError
    ? 'Unavailable'
    : infrastructure === null
      ? 'Checking...'
      : !infrastructure.connected
        ? 'Unavailable'
        : readyPods !== null && readyPods > 0
          ? 'Ready'
          : 'Not ready'

  const podLabel =
    readyPods !== null && totalPods !== null
      ? `${readyPods} / ${totalPods}`
      : infrastructureError
        ? 'Unavailable'
        : 'Checking...'

  const predictionAvailable =
    !predictionError &&
    prediction?.status === 'success' &&
    prediction.prediction !== undefined

  const riskLabel = predictionError
    ? 'Unavailable'
    : prediction === null
      ? 'Checking...'
      : predictionAvailable
        ? prediction.prediction === 1
          ? 'Elevated'
          : 'Low'
        : 'Not available'

  const probability =
    predictionAvailable
      ? prediction?.failure_probability
      : null

  const predictionMessage = predictionError
    ? 'Cannot reach prediction API'
    : prediction?.message ??
      'Waiting for three recognized application events'

  const recordedAlerts =
    !alertsError && alerts?.status === 'success'
      ? alerts.alerts
      : []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-symbol">
            <Search size={22} strokeWidth={2.2} />
          </div>

          <div>
            <div className="brand-name">
              AnomaLens
            </div>

            <div className="brand-caption">
              INFRASTRUCTURE INTELLIGENCE
            </div>
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

          <ChevronDown
            size={15}
            className="muted-icon"
          />
        </div>

        <div className="navigation-heading">
          WORKSPACE
        </div>

        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <button
                type="button"
                key={item.label}
                onClick={() => setActivePage(item.label)}
                className={`navigation-item ${
                  activePage === item.label
                    ? 'active'
                    : ''
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="navigation-item">
            <Settings2 size={18} />
            <span>Settings</span>
          </div>

          <div className="sidebar-profile">
            <div className="profile-avatar">
              A
            </div>

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

            <span className="breadcrumb-divider">
              /
            </span>

            <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <span className="environment-badge">
              <span className="environment-dot" />
              Local environment
            </span>

            <button
              className="icon-button"
              aria-label="Notifications"
              type="button"
            >
              <Bell size={19} />
            </button>

            <div className="topbar-avatar">
              A
            </div>
          </div>
        </header>

        <div className="dashboard-content">

          {activePage === 'Infrastructure' ? (
            <section>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">
                    MONITORING / INFRASTRUCTURE
                  </div>

                  <h1>Kubernetes Infrastructure</h1>

                  <p>
                    Current AnomaLens pod status from Minikube.
                  </p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Application Pods</h2>
                    <p>Refreshed every 10 seconds</p>
                  </div>

                  <span className="panel-tag">
                    {infrastructure?.connected
                      ? `${readyPods} / ${totalPods} ready`
                      : 'Connection unavailable'}
                  </span>
                </div>

                {infrastructure?.connected ? (
                  infrastructure.pods.length > 0 ? (
                    <div className="pod-list">
                      {infrastructure.pods.map((pod) => (
                        <div
                          className="pod-card"
                          key={pod.name}
                        >
                          <div className="pod-name">
                            {pod.name}
                          </div>

                          <div className="pod-details">
                            <span>
                              Phase: {pod.phase}
                            </span>

                            <span>
                              Readiness:{' '}
                              {pod.ready
                                ? 'Ready'
                                : 'Not ready'}
                            </span>

                            <span>
                              Restarts: {pod.restart_count}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="infrastructure-message">
                      No application pods found.
                    </p>
                  )
                ) : (
                  <p className="infrastructure-message">
                    {infrastructureError
                      ? 'Cannot reach monitoring API.'
                      : infrastructure?.error ??
                        'Checking Kubernetes connection...'}
                  </p>
                )}
              </div>
            </section>

          ) : activePage === 'Log Explorer' ? (
            <section>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">
                    MONITORING / LOG EXPLORER
                  </div>

                  <h1>Application Logs</h1>

                  <p>
                    Recent application logs from the
                    Kubernetes workload.
                  </p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Recent Kubernetes Logs</h2>

                    <p>
                      {logs?.connected
                        ? `Pod: ${logs.pod ?? 'None'}`
                        : 'Awaiting log data'}
                    </p>
                  </div>

                  <span className="panel-tag">
                    Live · 10s refresh
                  </span>
                </div>

                {!logs?.connected ? (
                  <p className="infrastructure-message">
                    {logsError
                      ? 'Cannot reach monitoring API.'
                      : logs?.error ??
                        'Loading logs...'}
                  </p>
                ) : logs.entries.length === 0 ? (
                  <p className="infrastructure-message">
                    No recent log entries found.
                  </p>
                ) : (
                  <div className="log-list">
                    {logs.entries.map((entry, index) => (
                      <div
                        className="log-row"
                        key={`${entry.timestamp}-${index}`}
                      >
                        <span className="log-time">
                          {entry.timestamp ||
                            'No timestamp'}
                        </span>

                        <span
                          className={`log-level level-${entry.level.toLowerCase()}`}
                        >
                          {entry.level}
                        </span>

                        <span className="log-message">
                          {entry.message}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

          ) : activePage === 'Predictive Alerts' ? (
            <section>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">
                    MONITORING / PREDICTIVE ALERTS
                  </div>

                  <h1>Predictive Alerts</h1>

                  <p>
                    Current experimental prediction
                    and saved alert history.
                  </p>
                </div>

                <div className="page-status">
                  <span className="status-dot" />
                  Experimental model
                </div>
              </div>

              <section className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-top">
                    <span>Current Prediction</span>
                    <ShieldAlert size={19} />
                  </div>

                  <div
                    className={`metric-value ${
                      predictionAvailable &&
                      prediction?.prediction === 1
                        ? 'warning'
                        : predictionAvailable
                          ? 'healthy'
                          : ''
                    }`}
                  >
                    {riskLabel}
                  </div>

                  <div className="metric-footer">
                    {predictionAvailable
                      ? prediction?.prediction_label
                      : predictionMessage}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Current Model Estimate</span>
                    <Activity size={19} />
                  </div>

                  <div className="metric-value">
                    {formatProbability(probability)}
                  </div>

                  <div className="metric-footer">
                    Not a validated real-world
                    failure probability
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Recorded Alerts</span>
                    <Bell size={19} />
                  </div>

                  <div className="metric-value">
                    {alertsError
                      ? 'N/A'
                      : alerts === null
                        ? '...'
                        : recordedAlerts.length}
                  </div>

                  <div className="metric-footer">
                    Saved in alert_history.json
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Recognized Events</span>
                    <Terminal size={19} />
                  </div>

                  <div className="metric-value">
                    {prediction?.recognized_event_count ??
                      'N/A'}
                  </div>

                  <div className="metric-footer">
                    Events matching training patterns
                  </div>
                </div>
              </section>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Current Prediction Details</h2>

                    <p>
                      Latest three-event model inference
                    </p>
                  </div>

                  <span className="panel-tag">
                    Live · 10s refresh
                  </span>
                </div>

                {predictionAvailable ? (
                  <div className="pod-list">
                    <div className="pod-card">
                      <div className="pod-name">
                        {prediction?.prediction_label}
                      </div>

                      <div className="pod-details">
                        <span>
                          Pod: {prediction?.pod}
                        </span>

                        <span>
                          Predicted class:{' '}
                          {prediction?.prediction}
                        </span>

                        <span>
                          Model estimate:{' '}
                          {formatProbability(probability)}
                        </span>
                      </div>
                    </div>

                    <p className="infrastructure-message">
                      {prediction?.note}
                    </p>
                  </div>
                ) : (
                  <p className="infrastructure-message">
                    {predictionMessage}
                  </p>
                )}
              </div>

              <div
                className="panel"
                style={{ marginTop: 20 }}
              >
                <div className="panel-header">
                  <div>
                    <h2>Current Input Features</h2>

                    <p>
                      Calculated from the latest three
                      recognized application events
                    </p>
                  </div>
                </div>

                {predictionAvailable &&
                prediction?.features ? (
                  <div className="pod-list">
                    {Object.entries(
                      prediction.features
                    ).map(([name, value]) => (
                      <div
                        className="pod-card"
                        key={name}
                      >
                        <div className="pod-details">
                          <span>{name}</span>
                          <strong>{value}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="infrastructure-message">
                    No input features available yet.
                  </p>
                )}
              </div>

              <div
                className="panel"
                style={{ marginTop: 20 }}
              >
                <div className="panel-header">
                  <div>
                    <h2>Events Used for Current Prediction</h2>

                    <p>
                      Latest three recognized events
                    </p>
                  </div>
                </div>

                {predictionAvailable &&
                prediction?.recent_events ? (
                  <div className="log-list">
                    {prediction.recent_events.map(
                      (event, index) => (
                        <div
                          className="log-row"
                          key={`${event.timestamp}-${index}`}
                        >
                          <span className="log-time">
                            {event.timestamp}
                          </span>

                          <span
                            className={`log-level level-${event.event_type}`}
                          >
                            {event.event_type.toUpperCase()}
                          </span>

                          <span className="log-message">
                            {event.message}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="infrastructure-message">
                    No prediction window available yet.
                  </p>
                )}
              </div>

              <div
                className="panel"
                style={{ marginTop: 20 }}
              >
                <div className="panel-header">
                  <div>
                    <h2>Recorded Alert History</h2>

                    <p>
                      Previously detected experimental
                      warning predictions
                    </p>
                  </div>

                  <span className="panel-tag">
                    {alertsError
                      ? 'Unavailable'
                      : `${recordedAlerts.length} saved`}
                  </span>
                </div>

                {alertsError ? (
                  <p className="infrastructure-message">
                    Cannot reach alert history API.
                  </p>
                ) : alerts === null ? (
                  <p className="infrastructure-message">
                    Loading saved alerts...
                  </p>
                ) : recordedAlerts.length === 0 ? (
                  <p className="infrastructure-message">
                    No alerts have been recorded yet.
                  </p>
                ) : (
                  <div className="pod-list">
                    {recordedAlerts.map((alert) => (
                      <div
                        className="pod-card"
                        key={alert.id}
                      >
                        <div className="pod-name">
                          <TriangleAlert
                            size={16}
                            style={{
                              display: 'inline-block',
                              verticalAlign: 'middle',
                              marginRight: 8,
                            }}
                          />

                          {alert.prediction_label}
                        </div>

                        <div className="pod-details">
                          <span>
                            Recorded:{' '}
                            {formatTime(alert.created_at)}
                          </span>

                          <span>
                            Model estimate:{' '}
                            {formatProbability(
                              alert.failure_probability
                            )}
                          </span>

                          <span>
                            Status: {alert.status}
                          </span>
                        </div>

                        <p className="infrastructure-message">
                          Pod: {alert.pod}
                        </p>

                        <div className="pod-details">
                          <span>
                            Normal:{' '}
                            {alert.features.normal_count_last_3}
                          </span>

                          <span>
                            Warning:{' '}
                            {alert.features.warning_count_last_3}
                          </span>

                          <span>
                            Error:{' '}
                            {alert.features.error_count_last_3}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

          ) : activePage === 'Overview' ? (
            <>
              <section className="page-heading">
                <div>
                  <div className="eyebrow">
                    MONITORING / OVERVIEW
                  </div>

                  <h1>Infrastructure Overview</h1>

                  <p>
                    Monitor Kubernetes workloads,
                    application logs, and experimental
                    failure signals.
                  </p>
                </div>

                <div className="page-status">
                  <span className="status-dot" />
                  Experimental monitoring dashboard
                </div>
              </section>

              <section className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-top">
                    <span>Pod Readiness</span>
                    <HeartPulse size={19} />
                  </div>

                  <div
                    className={`metric-value ${
                      healthLabel === 'Ready'
                        ? 'healthy'
                        : healthLabel === 'Not ready'
                          ? 'warning'
                          : ''
                    }`}
                  >
                    {healthLabel}
                  </div>

                  <div className="metric-footer">
                    <CircleCheck size={14} />
                    Kubernetes pod readiness,
                    not an HTTP health check
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Running Pods</span>
                    <Boxes size={19} />
                  </div>

                  <div className="metric-value">
                    {podLabel}
                  </div>

                  <div className="metric-footer">
                    Live Kubernetes ready / total pods
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Current Failure Prediction</span>
                    <ShieldAlert size={19} />
                  </div>

                  <div
                    className={`metric-value ${
                      predictionAvailable &&
                      prediction?.prediction === 1
                        ? 'warning'
                        : predictionAvailable
                          ? 'healthy'
                          : ''
                    }`}
                  >
                    {riskLabel}
                  </div>

                  <div className="metric-footer">
                    <TriangleAlert size={14} />

                    {predictionAvailable
                      ? 'Experimental Random Forest output'
                      : predictionMessage}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-top">
                    <span>Recorded Alerts</span>
                    <Bell size={19} />
                  </div>

                  <div className="metric-value">
                    {alertsError
                      ? 'N/A'
                      : alerts === null
                        ? '...'
                        : recordedAlerts.length}
                  </div>

                  <div className="metric-footer">
                    Saved experimental warning predictions
                  </div>
                </div>
              </section>

              <section className="dashboard-grid">
                <div className="panel activity-panel">
                  <div className="panel-header">
                    <div>
                      <h2>Application Activity</h2>

                      <p>
                        Illustrative request activity
                        over time
                      </p>
                    </div>

                    <span className="panel-tag">
                      Demo data
                    </span>
                  </div>

                  <div className="chart-container">
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >
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
                      <h2>Current Failure Prediction</h2>

                      <p>
                        Experimental model estimate
                      </p>
                    </div>

                    <ShieldAlert
                      size={19}
                      className="panel-icon"
                    />
                  </div>

                  <div className="risk-display">
                    <div
                      className="risk-ring"
                      style={{
                        background:
                          probability === null ||
                          probability === undefined
                            ? '#303238'
                            : `conic-gradient(
                                #fbbf24 0deg ${probability * 360}deg,
                                #303238 ${probability * 360}deg 360deg
                              )`,
                      }}
                    >
                      <div className="risk-ring-inner">
                        <span className="risk-percentage">
                          {formatProbability(probability)}
                        </span>

                        <span className="risk-label">
                          MODEL ESTIMATE
                        </span>
                      </div>
                    </div>

                    <div className="risk-status">
                      {riskLabel}
                    </div>

                    <p>
                      {predictionAvailable
                        ? prediction?.prediction_label
                        : predictionMessage}
                    </p>
                  </div>

                  <div className="risk-footer">
                    <span className="risk-indicator" />
                    Experimental model output,
                    not production-validated
                  </div>
                </div>
              </section>

              <section className="panel events-panel">
                <div className="panel-header">
                  <div>
                    <h2>Recent Recognized Events</h2>

                    <p>
                      Latest events used by the model
                    </p>
                  </div>

                  <span className="panel-tag">
                    Live log events
                  </span>
                </div>

                <div className="event-list">
                  {prediction?.recent_events?.length ? (
                    prediction.recent_events.map(
                      (event, index) => (
                        <div
                          className="event-row"
                          key={`${event.timestamp}-${index}`}
                        >
                          <div
                            className={`event-icon ${
                              event.event_type === 'normal'
                                ? 'event-success'
                                : 'event-warning'
                            }`}
                          >
                            {event.event_type === 'normal' ? (
                              <CircleCheck size={17} />
                            ) : (
                              <TriangleAlert size={17} />
                            )}
                          </div>

                          <div className="event-description">
                            <strong>
                              {event.event_type.toUpperCase()}
                            </strong>

                            <span>
                              {event.message}
                            </span>
                          </div>

                          <span className="event-time">
                            {formatTime(event.timestamp)}
                          </span>
                        </div>
                      )
                    )
                  ) : (
                    <p className="infrastructure-message">
                      No recognized events available yet.
                    </p>
                  )}
                </div>
              </section>

              <div className="dashboard-footer">
                AnomaLens · Controlled experimental prototype
              </div>
            </>

            ) : activePage === 'Analytics' ? (
              <Analytics />
            ) : (
              <section>
                <div className="page-heading">
                  <div>
                    <div className="eyebrow">
                      MONITORING / {activePage.toUpperCase()}
                  </div>

                  <h1>{activePage}</h1>

                  <p>
                    This module will be connected in
                    the next implementation stage.
                  </p>
                </div>
              </div>

              <div className="panel">
                <p className="infrastructure-message">
                  No live data is available for
                  this module yet.
                </p>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App