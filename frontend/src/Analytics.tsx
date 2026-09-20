
import {
  Activity,
  BarChart3,
  Database,
  FlaskConical,
  ShieldAlert,
} from 'lucide-react'

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import './App.css'

const evaluationData = [
  {
    metric: 'Accuracy',
    randomForest: 100,
    logisticRegression: 100,
    ruleBaseline: 85.71,
  },
  {
    metric: 'Precision',
    randomForest: 100,
    logisticRegression: 100,
    ruleBaseline: 50,
  },
  {
    metric: 'Recall',
    randomForest: 100,
    logisticRegression: 100,
    ruleBaseline: 100,
  },
  {
    metric: 'F1',
    randomForest: 100,
    logisticRegression: 100,
    ruleBaseline: 66.67,
  },
]

const logDistribution = [
  { name: 'Normal', count: 196 },
  { name: 'Warning', count: 54 },
  { name: 'Error', count: 18 },
]

const featureDescriptions = [
  ['normal_count_last_3', 'Number of normal events in the input window'],
  ['warning_count_last_3', 'Number of warning events in the input window'],
  ['error_count_last_3', 'Number of error events in the input window'],
  ['warning_rate_last_3', 'Warning events divided by three'],
  ['error_rate_last_3', 'Error events divided by three'],
]

function Analytics() {
  return (
    <section>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            MONITORING / ANALYTICS
          </div>

          <h1>Model Analytics</h1>

          <p>
            Dataset characteristics and evaluation
            results from the controlled AnomaLens experiment.
          </p>
        </div>

        <div className="page-status">
          <span className="status-dot" />
          Controlled experiment
        </div>
      </div>

      <section className="metrics-grid">
        <div className="metric-card">
          <div className="metric-top">
            <span>Controlled Sequences</span>
            <FlaskConical size={19} />
          </div>

          <div className="metric-value">50</div>

          <div className="metric-footer">
            32 healthy · 18 failure sequences
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Collected Log Events</span>
            <Database size={19} />
          </div>

          <div className="metric-value">268</div>

          <div className="metric-footer">
            Application logs retrieved from Kubernetes
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Windowed Samples</span>
            <Activity size={19} />
          </div>

          <div className="metric-value">118</div>

          <div className="metric-footer">
            100 negative · 18 positive labels
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>Held-out Test Samples</span>
            <BarChart3 size={19} />
          </div>

          <div className="metric-value">35</div>

          <div className="metric-footer">
            5 positive samples · Sequence-stratified split
          </div>
        </div>
      </section>

      <div
        className="panel"
        style={{ marginTop: 20 }}
      >
        <div className="panel-header">
          <div>
            <h2>Application Log Distribution</h2>

            <p>
              Events collected during the controlled experiment
            </p>
          </div>

          <span className="panel-tag">
            268 events
          </span>
        </div>

        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={logDistribution}
              margin={{ top: 12, right: 16, left: 0, bottom: 4 }}
            >
              <CartesianGrid
                stroke="#292b30"
                strokeDasharray="3 5"
                vertical={false}
              />

              <XAxis
                dataKey="name"
                stroke="#9296a0"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                stroke="#9296a0"
                tickLine={false}
                axisLine={false}
                allowDecimals={false}
              />

              <Tooltip
                contentStyle={{
                  background: '#1b1d21',
                  border: '1px solid #34363c',
                  borderRadius: 10,
                  color: '#f5f5f5',
                }}
              />

              <Bar
                dataKey="count"
                name="Log events"
                fill="#9ca3af"
                radius={[5, 5, 0, 0]}
                maxBarSize={110}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div
        className="panel"
        style={{ marginTop: 20 }}
      >
        <div className="panel-header">
          <div>
            <h2>Model Evaluation</h2>

            <p>
              Results on the 35-sample held-out controlled test set
            </p>
          </div>

          <span className="panel-tag">
            Experimental results
          </span>
        </div>

        <div style={{ width: '100%', height: 340 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={evaluationData}
              margin={{ top: 12, right: 16, left: 0, bottom: 4 }}
            >
              <CartesianGrid
                stroke="#292b30"
                strokeDasharray="3 5"
                vertical={false}
              />

              <XAxis
                dataKey="metric"
                stroke="#9296a0"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                domain={[0, 100]}
                stroke="#9296a0"
                tickLine={false}
                axisLine={false}
                tickFormatter={(value: number) => `${value}%`}
              />

              <Tooltip
                formatter={(value) => `${value}%`}
                contentStyle={{
                  background: '#1b1d21',
                  border: '1px solid #34363c',
                  borderRadius: 10,
                  color: '#f5f5f5',
                }}
              />

              <Legend />

              <Bar
                dataKey="randomForest"
                name="Random Forest"
                fill="#a7f3d0"
                radius={[4, 4, 0, 0]}
              />

              <Bar
                dataKey="logisticRegression"
                name="Logistic Regression"
                fill="#93c5fd"
                radius={[4, 4, 0, 0]}
              />

              <Bar
                dataKey="ruleBaseline"
                name="Rule baseline"
                fill="#fbbf24"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div
          className="pod-list"
          style={{ marginTop: 16 }}
        >
          <div className="pod-card">
            <div className="pod-name">
              Evaluation context
            </div>

            <p className="infrastructure-message">
              Both trained models achieved 100% accuracy,
              precision, recall, and F1 on this small,
              deliberately separable controlled test set.
              These measurements should not be interpreted
              as production performance or evidence of
              generalization to unseen failure scenarios.
            </p>
          </div>
        </div>
      </div>

      <div
        className="panel"
        style={{ marginTop: 20 }}
      >
        <div className="panel-header">
          <div>
            <h2>Feature Engineering</h2>

            <p>
              Five features calculated from each
              three-event sliding window
            </p>
          </div>

          <span className="panel-tag">
            Next-event classification
          </span>
        </div>

        <div className="pod-list">
          {featureDescriptions.map(([name, description]) => (
            <div className="pod-card" key={name}>
              <div className="pod-name">
                {name}
              </div>

              <p className="infrastructure-message">
                {description}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div
        className="panel"
        style={{ marginTop: 20 }}
      >
        <div className="panel-header">
          <div>
            <h2>Experimental Scope</h2>

            <p>
              What these results do and do not establish
            </p>
          </div>

          <ShieldAlert size={19} />
        </div>

        <p className="infrastructure-message">
          The dataset contains application log messages
          collected from a Kubernetes-hosted workload.
          It does not represent native Kubernetes API events.
          The prediction target is whether the next event
          in a controlled sequence is an error.
          Broader workloads, independent datasets, and
          additional failure scenarios are needed before
          making claims about real-world failure prediction.
        </p>
      </div>

      <div className="dashboard-footer">
        AnomaLens · Controlled experimental evaluation
      </div>
    </section>
  )
}

export default Analytics