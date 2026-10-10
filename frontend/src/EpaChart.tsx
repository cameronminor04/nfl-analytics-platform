import {
    Bar,
    BarChart,
    CartesianGrid,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
  } from "recharts";
  
  type StatRow = {
    team: string;
    season: number;
    epa_per_play: number;
  };
  
  type Props = {
    rows: StatRow[];
    side: string;
  };
  
  export default function EpaChart({ rows, side }: Props) {
    if (rows.length < 2) {
      return <p>Pick "All teams" to see the league chart.</p>;
    }
  
    const label =
      side === "defense"
        ? "EPA allowed per play (lower is better)"
        : "EPA per play (higher is better)";
  
    return (
      <div style={{ width: "100%", height: 340, marginBottom: 24 }}>
        <h3 style={{ margin: "0 0 8px" }}>{label}</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="team" interval={0} tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip formatter={(v) => Number(v).toFixed(3)} />
            <ReferenceLine y={0} stroke="#888" />
            <Bar dataKey="epa_per_play" fill="#1a437c" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }